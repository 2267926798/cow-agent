"""IoT 传感器时序数据查询工具 (本地模式)。

提供体温、反刍、步数及设备状态查询。
"""

import time
from typing import Dict, Any
from langchain_core.tools import tool
from src.schemas.evidence import EvidenceItem, EvidenceType
from src.utils.logger import log_tool_execution


def fetch_iot_metrics_mock(cow_id: str, time_window: str) -> Dict[str, Any]:
    """模拟底层 TDengine 时序数据库查询与前置降采样聚合。

    入参 2 个，符合规范约束。
    """
    # 模拟传感器离线，无法形成 IoT 证据
    if cow_id == "9999":
        return {
            "cow_id": cow_id,
            "window": time_window,
            "max_temperature": None,
            "avg_temperature": None,
            "normal_temp_range": "38.5-39.2℃",
            "rumination_minutes": None,
            "rumination_drop_rate": None,
            "activity_steps": None,
            "sensor_status": "OFFLINE",
            "device_id": f"TS-{cow_id}",
            "timestamp": "2026-09-05 10:00:00",
        }

    # 模拟 8892 号牛存在明显体温偏高与反刍下降异常
    if cow_id == "8892":
        return {
            "cow_id": cow_id,
            "window": time_window,
            "max_temperature": 39.8,
            "avg_temperature": 39.5,
            "normal_temp_range": "38.5-39.2℃",
            "rumination_minutes": 280,
            "rumination_drop_rate": 0.348,
            "activity_steps": 1200,
            "sensor_status": "ONLINE",
            "device_id": f"TS-{cow_id}",
            "timestamp": "2026-09-05 10:00:00",
        }
    
    # 默认正常牛只数据
    return {
        "cow_id": cow_id,
        "window": time_window,
        "max_temperature": 38.8,
        "avg_temperature": 38.6,
        "normal_temp_range": "38.5-39.2℃",
        "rumination_minutes": 440,
        "rumination_drop_rate": 0.02,
        "activity_steps": 2100,
        "sensor_status": "ONLINE",
        "device_id": f"TS-{cow_id}",
        "timestamp": "2026-09-05 10:00:00",
    }


@tool
def query_cow_iot_metrics(cow_id: str, time_window: str = "24h") -> str:
    """查询牛只最近一段时间的 IoT 传感器数据 (体温、反刍分钟数、步数趋势)。"""
    start_time = time.time()
    data = fetch_iot_metrics_mock(cow_id, time_window)
    latency_ms = (time.time() - start_time) * 1000
    log_tool_execution("sess_mock", "query_cow_iot_metrics", "SUCCESS", latency_ms)

    drop = data["rumination_drop_rate"]
    drop_pct = int(drop * 100) if drop is not None else 0
    return (
        f"【IoT 时序数据】牛只:{cow_id} | 最高体温:{data['max_temperature']}℃"
        f"(正常{data['normal_temp_range']}) | 24h反刍:{data['rumination_minutes']}min"
        f"(同比下降{drop_pct}%) | 设备:{data['device_id']}({data['sensor_status']})"
    )
