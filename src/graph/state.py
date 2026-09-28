"""LangGraph Agent 共享状态 TypedDict 数据模型。

包含图流转过程中的上下文、消息历史、证据链、Supervisor 路由及 HITL 中断状态。
"""

from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage
from src.schemas.evidence import EvidenceItem
from src.schemas.response import DiagnosisReportSchema


class AgentState(TypedDict):
    """Agent 全局共享状态类型。"""

    session_id: str
    cow_id: str
    trigger_source: str
    raw_input: str

    messages: List[BaseMessage]
    time_window: str
    suspected_tags: List[str]

    collected_evidences: List[EvidenceItem]
    rag_references: List[Dict[str, Any]]

    diagnosis_report: Optional[DiagnosisReportSchema]
    loop_count: int
    executed_tools: List[str]

    awaiting_human: bool
    human_action: Optional[str]
    human_modified_suggest: Optional[str]

    supervisor_route: str
    agent_scratchpad: Dict[str, str]
    critic_verdict: Optional[str]
    missing_slots: List[str]
    handoff_count: int
