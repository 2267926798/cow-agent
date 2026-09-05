"""Human-in-the-Loop 人工确认与恢复节点。

中断状态机挂起，等待兽医输入确认动作后再派发工单。
"""

from src.graph.state import AgentState
from src.schemas.response import DiagnosisStatus
from src.utils.logger import log_agent_step


def human_in_loop_node(state: AgentState) -> AgentState:
    """6. HITL 节点: 挂起状态机等待人工确认，或处理恢复后的派单动作。

    入参 1 个，符合规范约束。
    """
    session_id = state["session_id"]
    cow_id = state["cow_id"]
    action = state.get("human_action")

    if not action:
        log_agent_step(session_id, cow_id, "HITLNode", "State is INTERRUPTED, awaiting human confirmation in UI")
        state["awaiting_human"] = True
        return state

    log_agent_step(session_id, cow_id, "HITLNode", f"Resumed state with human action: {action}")
    state["awaiting_human"] = False

    if action == "APPROVE":
        if state.get("diagnosis_report"):
            state["diagnosis_report"].status = DiagnosisStatus.SUCCESS
            if state.get("human_modified_suggest"):
                state["diagnosis_report"].summary += f" (人工修正: {state['human_modified_suggest']})"
        log_agent_step(session_id, cow_id, "HITLNode", "WorkOrder created successfully following human APPROVE")
    else:
        if state.get("diagnosis_report"):
            state["diagnosis_report"].status = DiagnosisStatus.FAILED
            state["diagnosis_report"].summary = "诊断方案已被兽医人工驳回/撤销"
        log_agent_step(session_id, cow_id, "HITLNode", "WorkOrder rejected by human operator")

    return state
