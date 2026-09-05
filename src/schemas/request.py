"""Agent API 请求与人工确认入参数据模型。
"""

from typing import Optional
from pydantic import BaseModel, Field


class DiagnoseRequest(BaseModel):
    """诊断发起请求 Model。"""

    cow_id: str = Field(description="牛只耳标编号", example="8892")
    user_query: str = Field(description="告警文本或用户提问", example="8892号牛体温偏高且反刍下降，请进行诊断")
    session_id: Optional[str] = Field(default=None, description="会话ID，若不传则自动生成")
    trigger_source: str = Field(default="MANUAL_CHAT", description="触发源: MANUAL_CHAT 或 IOT_ALARM")


class ConfirmWorkOrderRequest(BaseModel):
    """Human-in-the-Loop 人工确认与派单回复 Model。"""

    session_id: str = Field(description="要恢复的 Agent 会话 ID")
    action: str = Field(description="操作动作: APPROVE (确认派单) 或 REJECT (驳回)")
    operator_id: str = Field(description="操作兽医/运维人员 ID", example="VET-007")
    modified_suggest: Optional[str] = Field(default=None, description="人工修改后的处置建议 (可选)")
