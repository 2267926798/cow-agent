"""诊断报告与数据支撑输出数据模型。
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from src.schemas.evidence import EvidenceItem


class DiagnosisStatus(str, Enum):
    """诊断报告状态枚举。"""

    SUCCESS = "SUCCESS"
    AWAITING_HUMAN = "AWAITING_HUMAN"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    FAILED = "FAILED"


class DiagnosisFinding(BaseModel):
    """单条诊断疾病结论与归因依据。"""

    disease_name: str = Field(description="疑似疾病名称")
    confidence: float = Field(description="诊断置信度 0.0 ~ 1.0")
    reasoning: str = Field(description="CoT 推导逻辑链")
    supporting_evidence_ids: List[str] = Field(description="支持该诊断的证据 ID 列表 (如 ['EV-01', 'EV-02'])")


class TreatmentRecommendation(BaseModel):
    """处置动作与用药方案。"""

    action: str = Field(description="处置动作/护理方案")
    suggested_dosage: str = Field(description="推荐用药及剂量")
    source_kb_id: str = Field(description="处方来源 SOP 编号 (如 KB-01)")


class DiagnosisReportSchema(BaseModel):
    """结构化诊断报告输出全貌。"""

    session_id: str = Field(description="会话 ID")
    cow_id: str = Field(description="牛只耳标编号")
    status: DiagnosisStatus = Field(description="诊断状态")
    summary: str = Field(description="核心诊断结论摘要")
    findings: List[DiagnosisFinding] = Field(default_factory=list, description="诊断发现列表")
    treatment_plan: List[TreatmentRecommendation] = Field(default_factory=list, description="处置建议")
    all_evidences: List[EvidenceItem] = Field(default_factory=list, description="完整的底层数据证据支撑清单")
    missing_data_reasons: Optional[List[str]] = Field(default=None, description="证据不足时的缺失数据原因列举")
    suggested_next_actions: Optional[List[str]] = Field(default=None, description="建议运维人员/兽医采取的排查操作")
    formatted_markdown: str = Field(default="", description="附带角标引用的 Markdown 渲染格式文本")
