"""FastAPI 服务入口。

提供 Agent 诊断触发接口与 Human-in-the-Loop 人工确认派单接口。
"""

import uuid
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from src.schemas.request import DiagnoseRequest, ConfirmWorkOrderRequest
from src.schemas.response import DiagnosisReportSchema
from src.graph.workflow import agent_app
from src.utils.logger import logger

app = FastAPI(
    title=settings.APP_NAME,
    description="智慧牧场 AI Agent 诊断与工单服务",
    version="1.0.0"
)

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 内存会话存储 (生产环境换 Redis Checkpointer)
SESSION_STORE: Dict[str, Dict[str, Any]] = {}


@app.get("/health")
def health_check() -> Dict[str, str]:
    """健康检查接口。"""
    return {"status": "UP", "service": settings.APP_NAME}


@app.post("/api/v1/agent/diagnose", response_model=DiagnosisReportSchema)
def trigger_agent_diagnose(req: DiagnoseRequest) -> DiagnosisReportSchema:
    """发起 Agent 诊断工作流接口。

    入参 1 个，符合规范约束。
    """
    session_id = req.session_id or f"sess_{uuid.uuid4().hex[:8]}"
    logger.info("Received diagnose request for cow_id: {}, session_id: {}", req.cow_id, session_id)

    initial_state = {
        "session_id": session_id,
        "cow_id": req.cow_id,
        "trigger_source": req.trigger_source,
        "raw_input": req.user_query,
        "messages": [],
        "time_window": "24h",
        "suspected_tags": [],
        "collected_evidences": [],
        "rag_references": [],
        "diagnosis_report": None,
        "loop_count": 0,
        "executed_tools": [],
        "awaiting_human": False,
        "human_action": None,
        "human_modified_suggest": None
    }

    # 执行 LangGraph 状态机
    final_state = agent_app.invoke(initial_state)

    # 暂存 State 到内存 Store
    SESSION_STORE[session_id] = final_state

    report = final_state.get("diagnosis_report")
    if not report:
        raise HTTPException(status_code=500, detail="Failed to generate diagnosis report")

    return report


@app.post("/api/v1/agent/confirm", response_model=DiagnosisReportSchema)
def confirm_work_order(req: ConfirmWorkOrderRequest) -> DiagnosisReportSchema:
    """Human-in-the-Loop 兽医人工确认派单或修正恢复接口。

    入参 1 个，符合规范约束。
    """
    session_id = req.session_id
    logger.info("Received human confirm action: {} for session_id: {}", req.action, session_id)

    if session_id not in SESSION_STORE:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found or expired")

    state = SESSION_STORE[session_id]
    state["human_action"] = req.action
    state["human_modified_suggest"] = req.modified_suggest

    # 唤醒恢复状态机向下流转
    final_state = agent_app.invoke(state)
    SESSION_STORE[session_id] = final_state

    report = final_state.get("diagnosis_report")
    if not report:
        raise HTTPException(status_code=500, detail="Failed to update report state after human confirmation")

    return report


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
