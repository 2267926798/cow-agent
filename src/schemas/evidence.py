"""数据证据项与来源追溯数据模型。
"""

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class EvidenceType(str, Enum):
    """数据证据来源类型枚举。"""

    IOT_METRIC = "iot_metric"
    COW_PROFILE = "cow_profile"
    MEDICAL_HISTORY = "medical_history"
    VET_KNOWLEDGE = "vet_knowledge"


class EvidenceItem(BaseModel):
    """单条数据证据项模型，用于诊断归因追溯。"""

    id: str = Field(description="证据唯一编号，如 EV-01, KB-01")
    type: EvidenceType = Field(description="证据类型")
    source: str = Field(description="数据来源，如 TDengine, MySQL, Milvus")
    metric_name: str = Field(description="指标或知识库条目名称")
    value: Any = Field(description="采样数值、差异比或描述片段")
    timestamp: Optional[str] = Field(default=None, description="数据采样时间戳")
    description: str = Field(description="证据详细可读描述")

    def to_formatted_str(self) -> str:
        """格式化为便于 Prompt 引用展示的字符串。"""
        time_info = f" (时间: {self.timestamp})" if self.timestamp else ""
        return f"[{self.id}] {self.metric_name}: {self.value} | 来源: {self.source}{time_info} | {self.description}"
