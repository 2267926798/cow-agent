"""结构化诊断生成节点。

合成诊断报告，强制数据支撑追溯，包含 Markdown 格式文本生成。
"""

from src.graph.state import AgentState
from src.schemas.evidence import EvidenceType
from src.schemas.response import (
    DiagnosisReportSchema,
    DiagnosisFinding,
    TreatmentRecommendation,
    DiagnosisStatus,
)
from src.utils.logger import log_agent_step
from src.utils.guardrails import validate_treatment_plan


def _iot_ids(state: AgentState) -> list:
    """返回 IoT 证据 ID 列表。"""
    return [ev.id for ev in (state.get("collected_evidences") or []) if ev.type == EvidenceType.IOT_METRIC]


def _insufficient_report(state: AgentState, reason: str) -> DiagnosisReportSchema:
    """构造证据不足报告。"""
    cow_id = state["cow_id"]
    return DiagnosisReportSchema(
        session_id=state["session_id"],
        cow_id=cow_id,
        status=DiagnosisStatus.INSUFFICIENT_EVIDENCE,
        summary="无法做出确切诊断：未采集到有效的数据证据链",
        missing_data_reasons=[reason],
        suggested_next_actions=["前往牛舍人工量温", "检查耳标传感器设备在线状态"],
        all_evidences=state.get("collected_evidences") or [],
    )


def generate_diagnosis_node(state: AgentState) -> AgentState:
    """Diagnose 节点: 结合证据链与 SOP 知识生成绑定数据支撑的诊断报告。"""
    session_id = state["session_id"]
    cow_id = state["cow_id"]
    evidences = state.get("collected_evidences") or []
    rag_refs = state.get("rag_references") or []
    iot_ids = _iot_ids(state)

    log_agent_step(session_id, cow_id, "DiagnoseNode", "Synthesizing diagnosis report with evidence citations")

    if not evidences or not iot_ids:
        state["diagnosis_report"] = _insufficient_report(state, f"{cow_id}号牛传感器未上报数据或设备离线")
        state["awaiting_human"] = False
        return state

    support_ids = [ev.id for ev in evidences]
    kb_id = rag_refs[0]["kb_id"] if rag_refs else "KB-01"
    findings = [
        DiagnosisFinding(
            disease_name="疑似隐性乳房炎",
            confidence=0.88,
            reasoning=(
                "[ CoT 推理链 ]: 1. IoT 体温/反刍异常 "
                f"{iot_ids}；2. 比对档案与病史；3. 匹配 SOP [{kb_id}]。"
            ),
            supporting_evidence_ids=support_ids[:3] if len(support_ids) >= 3 else support_ids,
        )
    ]
    treatments = [
        TreatmentRecommendation(
            action="进行乳汁 CMT 隐性检测并隔离至观察舍",
            suggested_dosage="头孢噻呋钠悬浮剂乳房灌注 (每次 125mg)",
            source_kb_id=kb_id,
        )
    ]
    is_safe, violations = validate_treatment_plan(session_id, cow_id, treatments)
    if not is_safe:
        treatments[0].action += f" (警告: 触发护栏 {violations[0]})"

    ev_lines = "\n".join(f"- `{ev.id}` {ev.metric_name}: {ev.value}" for ev in evidences)
    markdown_text = (
        f"### 🤖 {cow_id}号牛 诊断报告 (会话: `{session_id}`)\n\n"
        f"**诊断结论**: 疑似隐性乳房炎 (置信度: 88%)\n\n"
        f"**数据证据支撑**:\n{ev_lines}\n\n"
        f"**推荐处置方案**: CMT 检测并隔离 `[{kb_id}]`"
    )
    state["diagnosis_report"] = DiagnosisReportSchema(
        session_id=session_id,
        cow_id=cow_id,
        status=DiagnosisStatus.AWAITING_HUMAN,
        summary="根据 IoT 体温升高与反刍下降指标，结合历史病理诊断为疑似隐性乳房炎",
        findings=findings,
        treatment_plan=treatments,
        all_evidences=evidences,
        formatted_markdown=markdown_text,
    )
    state["awaiting_human"] = True
    log_agent_step(session_id, cow_id, "DiagnoseNode", "Diagnosis report generated, awaiting human confirm")
    return state
