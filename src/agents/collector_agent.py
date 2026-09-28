"""采集 Worker：并行拉取 IoT 与档案，禁止写诊断结论。"""

from concurrent.futures import ThreadPoolExecutor
from src.graph.state import AgentState
from src.graph.nodes.evidence_node import summarize_evidence_node
from src.tools.iot_tools import fetch_iot_metrics_mock
from src.tools.cow_profile_tools import fetch_cow_profile_mock
from src.tools.registry import get_tools_for_role
from src.agents.roles import COLLECTOR
from src.schemas.evidence import EvidenceItem, EvidenceType
from src.utils.logger import log_agent_step


def _fetch_bundle(cow_id: str, time_window: str) -> tuple:
    """并行查询 IoT 与档案 mock。"""
    with ThreadPoolExecutor(max_workers=2) as pool:
        iot_fut = pool.submit(fetch_iot_metrics_mock, cow_id, time_window)
        profile_fut = pool.submit(fetch_cow_profile_mock, cow_id)
        return iot_fut.result(), profile_fut.result()


def _iot_evidences(iot_raw: dict) -> list:
    """将在线 IoT 数据转为证据项。"""
    if iot_raw.get("sensor_status") != "ONLINE":
        return []
    ev1 = EvidenceItem(
        id="EV-01",
        type=EvidenceType.IOT_METRIC,
        source=f"TDengine ({iot_raw['device_id']})",
        metric_name="24h最高体温",
        value=f"{iot_raw['max_temperature']} ℃",
        timestamp=iot_raw["timestamp"],
        description=f"过去24小时最高体温，正常范围: {iot_raw['normal_temp_range']}",
    )
    drop = int(iot_raw["rumination_drop_rate"] * 100)
    ev2 = EvidenceItem(
        id="EV-02",
        type=EvidenceType.IOT_METRIC,
        source=f"TDengine ({iot_raw['device_id']})",
        metric_name="24h反刍分钟数",
        value=f"{iot_raw['rumination_minutes']} min",
        timestamp=iot_raw["timestamp"],
        description=f"24h累计反刍，同比下降: {drop}%",
    )
    return [ev1, ev2]


def _profile_evidences(profile_raw: dict) -> list:
    """将档案与病史转为证据项。"""
    items = [
        EvidenceItem(
            id="EV-03",
            type=EvidenceType.COW_PROFILE,
            source="MySQL (tb_cow_profile)",
            metric_name="牛只档案",
            value=f"牛舍:{profile_raw['barn_id']} | 胎次:{profile_raw['parity']} | 阶段:{profile_raw['lactation_stage']}",
            description="基本档案及产奶阶段",
        )
    ]
    if not profile_raw.get("history"):
        return items
    h_item = profile_raw["history"][0]
    items.append(
        EvidenceItem(
            id="EV-04",
            type=EvidenceType.MEDICAL_HISTORY,
            source="MySQL (tb_cow_medical_history)",
            metric_name="既往病史",
            value=f"患 {h_item['disease']} (用药:{h_item['treatment']})",
            timestamp=h_item["date"],
            description="历史就诊与用药记录",
        )
    )
    return items


def collector_agent_node(state: AgentState) -> AgentState:
    """Collector Worker：采集证据并清空已处理缺口。"""
    session_id = state["session_id"]
    cow_id = state["cow_id"]
    loop_count = state.get("loop_count", 0) + 1
    state["loop_count"] = loop_count
    get_tools_for_role(COLLECTOR)

    log_agent_step(session_id, cow_id, "CollectorAgent", f"Fetching IoT+profile loop #{loop_count}")
    iot_raw, profile_raw = _fetch_bundle(cow_id, state.get("time_window", "24h"))
    evidences = list(state.get("collected_evidences") or [])
    evidences.extend(_iot_evidences(iot_raw))
    evidences.extend(_profile_evidences(profile_raw))
    state["collected_evidences"] = evidences
    state["missing_slots"] = []
    pad = state.get("agent_scratchpad") or {}
    pad["collector"] = f"evidences={len(evidences)} sensor={iot_raw.get('sensor_status')}"
    state["agent_scratchpad"] = pad
    return summarize_evidence_node(state)
