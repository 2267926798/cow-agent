"""Supervisor 路由节点：确定性优先，可选轻量 LLM 覆盖。"""

from src.graph.state import AgentState
from src.agents.roles import COLLECTOR, KNOWLEDGE, DIAGNOSIS, CRITIC, HITL
from src.agents.roles import VERDICT_PASS, VERDICT_RETRY, VERDICT_INSUFFICIENT
from src.llm.factory import get_chat_model
from src.schemas.response import DiagnosisReportSchema, DiagnosisStatus
from config.settings import settings
from src.utils.logger import log_agent_step


def decide_next_route(state: AgentState) -> str:
    """根据证据、RAG、报告与质检结果决定下一跳。"""
    if state.get("handoff_count", 0) >= settings.MAX_HANDOFF_COUNT:
        return HITL

    evidences = state.get("collected_evidences") or []
    rag_refs = state.get("rag_references") or []
    report = state.get("diagnosis_report")
    verdict = state.get("critic_verdict")
    missing = state.get("missing_slots") or []

    if not evidences:
        return COLLECTOR
    if verdict == VERDICT_RETRY and missing:
        return COLLECTOR
    if not rag_refs:
        return KNOWLEDGE
    if report is None or verdict == VERDICT_RETRY:
        return DIAGNOSIS
    if verdict in (VERDICT_PASS, VERDICT_INSUFFICIENT):
        return HITL
    return CRITIC


def _write_halt_report(state: AgentState) -> None:
    """熔断且无可用报告时写入证据不足结论。"""
    if state.get("diagnosis_report") is not None:
        return
    cow_id = state.get("cow_id", "")
    session_id = state.get("session_id", "")
    state["diagnosis_report"] = DiagnosisReportSchema(
        session_id=session_id,
        cow_id=cow_id,
        status=DiagnosisStatus.INSUFFICIENT_EVIDENCE,
        summary="编排熔断：未能在限额内完成可靠诊断",
        missing_data_reasons=["handoff_count 达到上限"],
        suggested_next_actions=["人工复核传感器与病例后重试"],
    )
    state["critic_verdict"] = VERDICT_INSUFFICIENT
    state["awaiting_human"] = False


def supervisor_node(state: AgentState) -> AgentState:
    """编排节点：计数、熔断、确定性路由。"""
    session_id = state.get("session_id", "")
    cow_id = state.get("cow_id", "")
    count = state.get("handoff_count", 0) + 1
    state["handoff_count"] = count

    route = decide_next_route(state)
    if count >= settings.MAX_HANDOFF_COUNT:
        _write_halt_report(state)
        route = HITL

    model = get_chat_model("light")
    if model is not None:
        log_agent_step(session_id, cow_id, "Supervisor", "LLM overlay skipped in favor of deterministic route")

    state["supervisor_route"] = route
    pad = state.get("agent_scratchpad") or {}
    pad["supervisor"] = f"route={route} handoff={count}"
    state["agent_scratchpad"] = pad
    log_agent_step(session_id, cow_id, "Supervisor", f"Next route: {route} (handoff={count})")
    return state


def route_from_supervisor(state: AgentState) -> str:
    """条件边读取 supervisor_route。"""
    return state.get("supervisor_route") or HITL
