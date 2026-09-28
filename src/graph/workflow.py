"""LangGraph Agent 状态图：Supervisor 编排与角色 Worker 回边。"""

from langgraph.graph import StateGraph, END
from src.graph.state import AgentState
from src.graph.nodes.parse_node import parse_intent_node
from src.graph.nodes.hitl_node import human_in_loop_node
from src.agents.supervisor import supervisor_node, route_from_supervisor
from src.agents.collector_agent import collector_agent_node
from src.agents.knowledge_agent import knowledge_agent_node
from src.agents.diagnosis_agent import diagnosis_agent_node
from src.agents.critic_agent import critic_agent_node
from src.agents.roles import COLLECTOR, KNOWLEDGE, DIAGNOSIS, CRITIC, HITL


def build_agent_workflow():
    """组装 Supervisor + Worker 的 StateGraph。"""
    workflow = StateGraph(AgentState)

    workflow.add_node("parse_intent", parse_intent_node)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node(COLLECTOR, collector_agent_node)
    workflow.add_node(KNOWLEDGE, knowledge_agent_node)
    workflow.add_node(DIAGNOSIS, diagnosis_agent_node)
    workflow.add_node(CRITIC, critic_agent_node)
    workflow.add_node(HITL, human_in_loop_node)

    workflow.set_entry_point("parse_intent")
    workflow.add_edge("parse_intent", "supervisor")
    workflow.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            COLLECTOR: COLLECTOR,
            KNOWLEDGE: KNOWLEDGE,
            DIAGNOSIS: DIAGNOSIS,
            CRITIC: CRITIC,
            HITL: HITL,
        },
    )
    workflow.add_edge(COLLECTOR, "supervisor")
    workflow.add_edge(KNOWLEDGE, "supervisor")
    workflow.add_edge(DIAGNOSIS, "supervisor")
    workflow.add_edge(CRITIC, "supervisor")
    workflow.add_edge(HITL, END)

    return workflow.compile()


agent_app = build_agent_workflow()
