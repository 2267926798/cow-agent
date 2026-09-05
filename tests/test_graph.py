"""Agent 状态机全链路流程与 HITL 人工确认单元测试。
"""

import pytest
from src.graph.workflow import agent_app
from src.schemas.response import DiagnosisStatus


def test_agent_graph_full_flow():
    """测试完整诊断工作流 (Parse -> Tool -> Evidence -> RAG -> Diagnose -> HITL)。"""
    initial_state = {
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
        "human_modified_suggest": None
    }

    # 执行状态机
    final_state = agent_app.invoke(initial_state)

    report = final_state.get("diagnosis_report")
    assert report is not None
    assert report.cow_id == "8892"
    assert report.status == DiagnosisStatus.AWAITING_HUMAN
    assert len(report.all_evidences) >= 3
    assert len(report.findings) >= 1
    # 验证证据引用包含 EV-01
    assert "EV-01" in report.findings[0].supporting_evidence_ids


def test_agent_graph_human_confirmation_approve():
    """测试 HITL 兽医确认派单 (APPROVE)。"""
    state = {
        "session_id": "test_sess_002",
        "cow_id": "8892",
        "trigger_source": "MANUAL_CHAT",
        "raw_input": "测试派单",
        "messages": [],
        "time_window": "24h",
        "suspected_tags": [],
        "collected_evidences": [],
        "rag_references": [],
        "diagnosis_report": None,
        "loop_count": 0,
        "executed_tools": [],
        "awaiting_human": False,
        "human_action": "APPROVE",
        "human_modified_suggest": "隔离并补充生理盐水"
    }

    final_state = agent_app.invoke(state)
    report = final_state.get("diagnosis_report")
    assert report is not None
    assert report.status == DiagnosisStatus.SUCCESS
    assert "隔离并补充生理盐水" in report.summary
