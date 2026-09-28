"""质检 Worker：校验证据引用与 SOP 编号，不调用业务工具。"""

from typing import List, Set
from src.graph.state import AgentState
from src.agents.roles import VERDICT_PASS, VERDICT_RETRY, VERDICT_INSUFFICIENT
from src.schemas.evidence import EvidenceType
from src.schemas.response import DiagnosisStatus, DiagnosisReportSchema
from src.utils.logger import log_agent_step


def _evidence_ids(state: AgentState) -> Set[str]:
    """收集已采证据 ID。"""
    return {ev.id for ev in (state.get("collected_evidences") or [])}


def _kb_ids(state: AgentState) -> Set[str]:
    """收集 RAG 文档 kb_id。"""
    return {ref.get("kb_id", "") for ref in (state.get("rag_references") or [])}


def _has_iot(state: AgentState) -> bool:
    """是否存在 IoT 类证据。"""
    for ev in state.get("collected_evidences") or []:
        if ev.type == EvidenceType.IOT_METRIC:
            return True
    return False


def _invalid_finding_ids(state: AgentState, valid: Set[str]) -> List[str]:
    """返回诊断中引用了不存在证据的 ID。"""
    report = state.get("diagnosis_report")
    if not report:
        return ["missing_report"]
    bad = []
    for finding in report.findings:
        for eid in finding.supporting_evidence_ids:
            if eid not in valid:
                bad.append(eid)
    return bad


def _invalid_kb_ids(state: AgentState, valid_kb: Set[str]) -> List[str]:
    """返回处方中未出现在 RAG 的 SOP 编号。"""
    report = state.get("diagnosis_report")
    if not report:
        return []
    bad = []
    for rec in report.treatment_plan:
        if rec.source_kb_id not in valid_kb:
            bad.append(rec.source_kb_id)
    return bad


def _mark_insufficient(state: AgentState, reasons: List[str]) -> AgentState:
    """将报告降级为证据不足且清空处方。"""
    session_id = state["session_id"]
    cow_id = state["cow_id"]
    report = DiagnosisReportSchema(
        session_id=session_id,
        cow_id=cow_id,
        status=DiagnosisStatus.INSUFFICIENT_EVIDENCE,
        summary="无法做出确切诊断：IoT 或关键证据不足",
        missing_data_reasons=reasons,
        suggested_next_actions=["前往牛舍人工量温", "检查耳标传感器设备在线状态"],
        all_evidences=state.get("collected_evidences") or [],
    )
    state["diagnosis_report"] = report
    state["critic_verdict"] = VERDICT_INSUFFICIENT
    state["awaiting_human"] = False
    state["missing_slots"] = []
    return state


def critic_agent_node(state: AgentState) -> AgentState:
    """Critic Worker：PASS / RETRY / INSUFFICIENT。"""
    session_id = state["session_id"]
    cow_id = state["cow_id"]
    log_agent_step(session_id, cow_id, "CriticAgent", "Validating citations and evidence coverage")

    if not _has_iot(state):
        state = _mark_insufficient(state, [f"{cow_id}号牛传感器未上报或设备离线"])
        return state

    valid_ev = _evidence_ids(state)
    valid_kb = _kb_ids(state)
    bad_ev = _invalid_finding_ids(state, valid_ev)
    bad_kb = _invalid_kb_ids(state, valid_kb)

    if bad_ev or bad_kb:
        state["critic_verdict"] = VERDICT_RETRY
        state["diagnosis_report"] = None
        state["missing_slots"] = []
        pad = state.get("agent_scratchpad") or {}
        pad["critic"] = f"RETRY bad_ev={bad_ev} bad_kb={bad_kb}"
        state["agent_scratchpad"] = pad
        log_agent_step(session_id, cow_id, "CriticAgent", pad["critic"])
        return state

    state["critic_verdict"] = VERDICT_PASS
    pad = state.get("agent_scratchpad") or {}
    pad["critic"] = "PASS"
    state["agent_scratchpad"] = pad
    log_agent_step(session_id, cow_id, "CriticAgent", "PASS")
    return state
