"""诊断 Worker：只读证据与 SOP，禁止调用 IoT/DB 工具。"""

from src.graph.state import AgentState
from src.graph.nodes.diagnose_node import generate_diagnosis_node
from src.utils.logger import log_agent_step


def diagnosis_agent_node(state: AgentState) -> AgentState:
    """Diagnosis Worker：合成结构化报告并重置质检状态。"""
    session_id = state["session_id"]
    cow_id = state["cow_id"]
    log_agent_step(session_id, cow_id, "DiagnosisAgent", "Synthesizing report from evidence+SOP only")
    state["critic_verdict"] = None
    state = generate_diagnosis_node(state)
    pad = state.get("agent_scratchpad") or {}
    report = state.get("diagnosis_report")
    status = report.status.value if report else "none"
    pad["diagnosis"] = f"status={status}"
    state["agent_scratchpad"] = pad
    return state
