"""向量知识库 SOP 检索与重排节点。

拿提取的特征 Tag 去 Milvus/VectorDB 召回文献与规程。
"""

from src.graph.state import AgentState
from src.tools.rag_tools import search_vector_kb_mock
from src.utils.logger import log_agent_step


def search_rag_knowledge_node(state: AgentState) -> AgentState:
    """4. RAG Match 节点: 拿异常特征检索兽医 SOP 指南与处置规程。

    入参 1 个，符合规范约束。
    """
    session_id = state["session_id"]
    cow_id = state["cow_id"]
    tags = state.get("suspected_tags", ["fever", "rumination_drop"])

    query_str = " ".join(tags)
    log_agent_step(session_id, cow_id, "RAGNode", f"Searching Vet KB with tags: '{query_str}'")

    kb_results = search_vector_kb_mock(query_str)
    state["rag_references"] = kb_results

    log_agent_step(session_id, cow_id, "RAGNode", f"Retrieved {len(kb_results)} SOP documents")
    return state
