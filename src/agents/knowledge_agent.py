"""知识检索 Worker：仅允许 SOP 工具，写入 rag_references。"""

from src.graph.state import AgentState
from src.graph.nodes.rag_node import search_rag_knowledge_node
from src.tools.registry import get_tools_for_role
from src.agents.roles import KNOWLEDGE
from src.utils.logger import log_agent_step


def knowledge_agent_node(state: AgentState) -> AgentState:
    """Knowledge Worker：按症状 Tag 召回兽医 SOP。"""
    session_id = state["session_id"]
    cow_id = state["cow_id"]
    get_tools_for_role(KNOWLEDGE)
    log_agent_step(session_id, cow_id, "KnowledgeAgent", "Retrieving veterinary SOP references")
    state = search_rag_knowledge_node(state)
    pad = state.get("agent_scratchpad") or {}
    refs = state.get("rag_references") or []
    pad["knowledge"] = f"rag={len(refs)}"
    state["agent_scratchpad"] = pad
    return state
