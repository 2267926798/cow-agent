"""LangGraph Agent 共享状态 TypedDict 数据模型。

包含图流转过程中的上下文、消息历史、证据链及 HITL 中断状态。
"""

from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage
from src.schemas.evidence import EvidenceItem
from src.schemas.response import DiagnosisReportSchema


class AgentState(TypedDict):
    """Agent 全局共享状态类型。"""

    session_id: str                      # 诊断会话 ID
    cow_id: str                          # 牛只耳标编号
    trigger_source: str                  # 触发来源: MANUAL_CHAT 或 IOT_ALARM
    raw_input: str                       # 原始输入告警或提问

    messages: List[BaseMessage]          # LangChain 对话消息历史列表
    time_window: str                     # 时间窗口 (如 24h)
    suspected_tags: List[str]            # 提取的特征/症状 Tag 列表

    collected_evidences: List[EvidenceItem] # 采沉淀的数据证据链列表
    rag_references: List[Dict[str, Any]]    # 召回的兽医 SOP 知识片段

    diagnosis_report: Optional[DiagnosisReportSchema] # 结构化诊断报告
    loop_count: int                      # ReAct 循环计数器 (死循环熔断)
    executed_tools: List[str]            # 已执行过的 Tool 记录

    awaiting_human: bool                 # 是否处于 Human-in-the-Loop 中断挂起状态
    human_action: Optional[str]          # 人工确认动作: APPROVE 或 REJECT
    human_modified_suggest: Optional[str] # 人工修改后的处置建议
