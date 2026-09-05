"""Tool Call / MCP 工具驱动数据采集节点。

并发/多轮调用底层 IoT 与档案 DB，搜集证据项。
"""

from src.graph.state import AgentState
from src.tools.iot_tools import fetch_iot_metrics_mock
from src.tools.cow_profile_tools import fetch_cow_profile_mock
from src.schemas.evidence import EvidenceItem, EvidenceType
from src.utils.logger import log_agent_step


def execute_tool_calls_node(state: AgentState) -> AgentState:
    """2. ToolCall 节点: 驱动 Tool / MCP 客户端查询 IoT 与档案数据库。

    入参 1 个，符合规范约束。
    """
    session_id = state["session_id"]
    cow_id = state["cow_id"]
    loop_count = state.get("loop_count", 0) + 1
    state["loop_count"] = loop_count

    log_agent_step(session_id, cow_id, "ToolCallNode", f"Executing Tool/MCP fetching loop #{loop_count}")

    evidences = state.get("collected_evidences", [])

    # 1. 采集 IoT 数据
    iot_raw = fetch_iot_metrics_mock(cow_id, state.get("time_window", "24h"))
    if iot_raw.get("sensor_status") == "ONLINE":
        ev1 = EvidenceItem(
            id=f"EV-01",
            type=EvidenceType.IOT_METRIC,
            source=f"TDengine ({iot_raw['device_id']})",
            metric_name="24h最高体温",
            value=f"{iot_raw['max_temperature']} ℃",
            timestamp=iot_raw["timestamp"],
            description=f"过去24小时最高体温，正常范围: {iot_raw['normal_temp_range']}"
        )
        ev2 = EvidenceItem(
            id=f"EV-02",
            type=EvidenceType.IOT_METRIC,
            source=f"TDengine ({iot_raw['device_id']})",
            metric_name="24h反刍分钟数",
            value=f"{iot_raw['rumination_minutes']} min",
            timestamp=iot_raw["timestamp"],
            description=f"24h累计反刍，同比下降: {int(iot_raw['rumination_drop_rate']*100)}%"
        )
        evidences.extend([ev1, ev2])

    # 2. 采集牛只档案与历史病历
    profile_raw = fetch_cow_profile_mock(cow_id)
    ev3 = EvidenceItem(
        id=f"EV-03",
        type=EvidenceType.COW_PROFILE,
        source="MySQL (tb_cow_profile)",
        metric_name="牛只档案",
        value=f"牛舍:{profile_raw['barn_id']} | 胎次:{profile_raw['parity']} | 阶段:{profile_raw['lactation_stage']}",
        description="基本档案及产奶阶段"
    )
    evidences.append(ev3)

    if profile_raw.get("history"):
        h_item = profile_raw["history"][0]
        ev4 = EvidenceItem(
            id=f"EV-04",
            type=EvidenceType.MEDICAL_HISTORY,
            source="MySQL (tb_cow_medical_history)",
            metric_name="既往病史",
            value=f"患 {h_item['disease']} (用药:{h_item['treatment']})",
            timestamp=h_item["date"],
            description="历史就诊与用药记录"
        )
        evidences.append(ev4)

    state["collected_evidences"] = evidences
    log_agent_step(session_id, cow_id, "ToolCallNode", f"Collected {len(evidences)} evidences")
    return state
