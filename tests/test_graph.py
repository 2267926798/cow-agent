"""Agent 状态机：Supervisor 编排、质检打回、熔断与 HITL 测试。"""

from src.graph.workflow import agent_app
from src.schemas.response import DiagnosisStatus, DiagnosisFinding, DiagnosisReportSchema
from src.schemas.evidence import EvidenceItem, EvidenceType
from src.agents.supervisor import decide_next_route, supervisor_node
from src.agents.critic_agent import critic_agent_node
from src.agents.diagnosis_agent import diagnosis_agent_node
from src.agents.roles import COLLECTOR, KNOWLEDGE, DIAGNOSIS, CRITIC, HITL, VERDICT_RETRY
from config.settings import settings


def _base_state(**overrides) -> dict:
    """构造可 invoke 的初始状态。"""
    state = {
        "session_id": "test_sess_001",
        "cow_id": "8892",
        "trigger_source": "MANUAL_CHAT",
        "raw_input": "8892号牛体温39.8度，反刍大幅下降，请诊断",
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
        "human_modified_suggest": None,
        "supervisor_route": "",
        "agent_scratchpad": {},
        "critic_verdict": None,
        "missing_slots": [],
        "handoff_count": 0,
    }
    state.update(overrides)
    return state


def test_agent_graph_full_flow():
    """发热+反刍下降：Collector→Knowledge→Diagnosis→Critic PASS→HITL。"""
    final_state = agent_app.invoke(_base_state(), {"recursion_limit": settings.RECURSION_LIMIT})
    report = final_state.get("diagnosis_report")
    assert report is not None
    assert report.cow_id == "8892"
    assert report.status == DiagnosisStatus.AWAITING_HUMAN
    assert len(report.all_evidences) >= 3
    assert len(report.findings) >= 1
    assert "EV-01" in report.findings[0].supporting_evidence_ids
    assert final_state.get("critic_verdict") == "PASS"
    assert final_state.get("handoff_count", 0) <= settings.MAX_HANDOFF_COUNT


def test_agent_graph_human_confirmation_approve():
    """HITL 兽医确认派单 (APPROVE)。"""
    state = _base_state(
        session_id="test_sess_002",
        raw_input="测试派单",
        human_action="APPROVE",
        human_modified_suggest="隔离并补充生理盐水",
    )
    final_state = agent_app.invoke(state, {"recursion_limit": settings.RECURSION_LIMIT})
    report = final_state.get("diagnosis_report")
    assert report is not None
    assert report.status == DiagnosisStatus.SUCCESS
    assert "隔离并补充生理盐水" in report.summary


def test_offline_sensor_insufficient_evidence():
    """传感器离线：不得出具处方，状态为 INSUFFICIENT_EVIDENCE。"""
    state = _base_state(
        session_id="test_sess_offline",
        cow_id="9999",
        raw_input="9999号牛告警，请诊断",
    )
    final_state = agent_app.invoke(state, {"recursion_limit": settings.RECURSION_LIMIT})
    report = final_state.get("diagnosis_report")
    assert report is not None
    assert report.status == DiagnosisStatus.INSUFFICIENT_EVIDENCE
    assert not report.treatment_plan


def test_critic_rejects_hallucinated_evidence():
    """Critic 发现假引用 EV-99 后打回，Diagnosis 仅引用真实证据。"""
    ev = EvidenceItem(
        id="EV-01",
        type=EvidenceType.IOT_METRIC,
        source="TDengine",
        metric_name="体温",
        value="39.8",
        description="mock",
    )
    fake_report = DiagnosisReportSchema(
        session_id="crit",
        cow_id="8892",
        status=DiagnosisStatus.AWAITING_HUMAN,
        summary="fake",
        findings=[
            DiagnosisFinding(
                disease_name="幻觉病",
                confidence=0.9,
                reasoning="无",
                supporting_evidence_ids=["EV-99"],
            )
        ],
    )
    state = _base_state(
        collected_evidences=[ev],
        rag_references=[{"kb_id": "KB-01"}],
        diagnosis_report=fake_report,
    )
    after_critic = critic_agent_node(state)
    assert after_critic["critic_verdict"] == VERDICT_RETRY
    assert after_critic["diagnosis_report"] is None

    after_diag = diagnosis_agent_node(after_critic)
    ids = after_diag["diagnosis_report"].findings[0].supporting_evidence_ids
    assert "EV-99" not in ids
    assert "EV-01" in ids


def test_handoff_limit_forces_halt():
    """handoff_count 超限时强制结束。"""
    state = _base_state(handoff_count=settings.MAX_HANDOFF_COUNT)
    assert decide_next_route(state) == HITL
    halted = supervisor_node(state)
    assert halted["supervisor_route"] == HITL
    assert halted["diagnosis_report"] is not None
    assert halted["diagnosis_report"].status == DiagnosisStatus.INSUFFICIENT_EVIDENCE


def test_deterministic_routes():
    """确定性路由顺序。"""
    empty = _base_state()
    assert decide_next_route(empty) == COLLECTOR
    with_ev = _base_state(collected_evidences=[object()])
    assert decide_next_route(with_ev) == KNOWLEDGE
    with_rag = _base_state(collected_evidences=[object()], rag_references=[{"kb_id": "KB-01"}])
    assert decide_next_route(with_rag) == DIAGNOSIS
    with_report = _base_state(
        collected_evidences=[object()],
        rag_references=[{"kb_id": "KB-01"}],
        diagnosis_report=DiagnosisReportSchema(
            session_id="s", cow_id="1", status=DiagnosisStatus.AWAITING_HUMAN, summary="x"
        ),
    )
    assert decide_next_route(with_report) == CRITIC
