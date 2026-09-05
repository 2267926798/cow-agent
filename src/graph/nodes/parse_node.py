"""告警解析与意图提取图节点。

提取 cow_id, time_window 以及初始症状 Tag。
"""

import re
from src.graph.state import AgentState
from src.utils.logger import log_agent_step


def parse_intent_node(state: AgentState) -> AgentState:
    """1. Parse 节点: 解析告警文本或提问提取关键实体参数。

    入参 1 个，符合规范约束。
    """
    session_id = state.get("session_id", "sess_unknown")
    raw_input = state.get("raw_input", "")
    cow_id = state.get("cow_id", "")

    log_agent_step(session_id, cow_id, "ParseNode", f"Parsing raw input: '{raw_input}'")

    # 如果未显式传入 cow_id，通过正则表达式智能抽取 4 位数字耳标号
    if not cow_id:
        match = re.search(r"\b\d{4}\b", raw_input)
        if match:
            cow_id = match.group(0)
        else:
            cow_id = "8892"  # 缺省 fallback

    # 简易抽取关键字特征 Tag
    tags = []
    if "体温" in raw_input or "热" in raw_input or "fever" in raw_input.lower():
        tags.append("fever")
    if "反刍" in raw_input or "采食" in raw_input:
        tags.append("rumination_drop")

    if not tags:
        tags = ["fever", "rumination_drop"]

    state["cow_id"] = cow_id
    state["time_window"] = "24h"
    state["suspected_tags"] = tags
    state["loop_count"] = 0
    state["executed_tools"] = []
    state["collected_evidences"] = []
    state["rag_references"] = []

    log_agent_step(session_id, cow_id, "ParseNode", f"Extracted Cow ID: {cow_id}, Tags: {tags}")
    return state
