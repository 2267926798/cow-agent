"""证据链汇总与特征提炼节点。

去除重复证据项，提炼核心异常特征。
"""

from src.graph.state import AgentState
from src.utils.logger import log_agent_step


def summarize_evidence_node(state: AgentState) -> AgentState:
    """3. Evidence 节点: 证据链汇总、去重与指标提炼。

    入参 1 个，符合规范约束。
    """
    session_id = state["session_id"]
    cow_id = state["cow_id"]
    evidences = state.get("collected_evidences", [])

    log_agent_step(session_id, cow_id, "EvidenceNode", f"Deduplicating and summarizing {len(evidences)} evidences")

    # 按 id 键去重
    seen_ids = set()
    unique_evidences = []
    for ev in evidences:
        if ev.id not in seen_ids:
            seen_ids.add(ev.id)
            unique_evidences.append(ev)

    state["collected_evidences"] = unique_evidences
    log_agent_step(session_id, cow_id, "EvidenceNode", f"Final summarized evidences count: {len(unique_evidences)}")
    return state
