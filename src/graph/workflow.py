"""LangGraph Agent 状态图连线与条件路由流转模块。

连接 Parse -> ToolCall -> Evidence -> RAG -> Diagnose -> HITL 工作流。
"""

from langgraph.graph import StateGraph, END
from src.graph.state import AgentState
from src.graph.nodes.parse_node import parse_intent_node
from src.graph.nodes.tool_call_node import execute_tool_calls_node
from src.graph.nodes.evidence_node import summarize_evidence_node
from src.graph.nodes.rag_node import search_rag_knowledge_node
from src.graph.nodes.diagnose_node import generate_diagnosis_node
from src.graph.nodes.hitl_node import human_in_loop_node
from src.utils.logger import logger


def should_continue_loop(state: AgentState) -> str:
    """条件路由逻辑: 检查 ReAct 循环次数防死循环。

    入参 1 个，符合规范约束。
    """
    loop_count = state.get("loop_count", 0)
    if loop_count >= 3:
        logger.warning("[Session: {}] Loop count limit reached ({}), forcing break to Evidence Summary", state.get("session_id"), loop_count)
        return "evidence_summary"
    return "evidence_summary"  # 当前轮次直通汇总


def build_agent_workflow():
    """组装构建 LangGraph StateGraph 图。

    无入参，符合规范约束。
    """
    workflow = StateGraph(AgentState)

    # 1. 注册图状态节点
    workflow.add_node("parse_intent", parse_intent_node)
    workflow.add_node("execute_tools", execute_tool_calls_node)
    workflow.add_node("evidence_summary", summarize_evidence_node)
    workflow.add_node("search_rag", search_rag_knowledge_node)
    workflow.add_node("diagnose", generate_diagnosis_node)
    workflow.add_node("hitl_confirm", human_in_loop_node)

    # 2. 连接常规图边
    workflow.set_entry_point("parse_intent")
    workflow.add_edge("parse_intent", "execute_tools")

    # 3. 条件路由判定 (带防死循环熔断)
    workflow.add_conditional_edges(
        "execute_tools",
        should_continue_loop,
        {
            "evidence_summary": "evidence_summary",
            "execute_tools": "execute_tools"
        }
    )

    workflow.add_edge("evidence_summary", "search_rag")
    workflow.add_edge("search_rag", "diagnose")
    workflow.add_edge("diagnose", "hitl_confirm")
    workflow.add_edge("hitl_confirm", END)

    # 4. 编译成 Runnable Graph (可配合 Redis Checkpointer 使用)
    app = workflow.compile()
    return app


# 单例编译后的 Graph 实例
agent_app = build_agent_workflow()
