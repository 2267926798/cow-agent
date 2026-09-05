"""工具注册与数据采集单元测试。
"""

import pytest
from src.tools.iot_tools import fetch_iot_metrics_mock, query_cow_iot_metrics
from src.tools.cow_profile_tools import fetch_cow_profile_mock, query_cow_profile_and_history
from src.tools.rag_tools import search_vector_kb_mock
from src.tools.registry import get_all_registered_tools


def test_fetch_iot_metrics_mock():
    """测试 8892 号牛 IoT 时序数据 Mock 查询。"""
    res = fetch_iot_metrics_mock("8892", "24h")
    assert res["max_temperature"] == 39.8
    assert res["rumination_minutes"] == 280
    assert res["rumination_drop_rate"] == 0.348


def test_fetch_cow_profile_mock():
    """测试牛只档案与病理查询。"""
    res = fetch_cow_profile_mock("8892")
    assert res["barn_id"] == "BARN-03"
    assert len(res["history"]) == 1
    assert res["history"][0]["disease"] == "右后乳区乳房炎"


def test_search_vector_kb_mock():
    """测试兽医 SOP 向量检索。"""
    res = search_vector_kb_mock("fever rumination_drop")
    assert len(res) >= 1
    assert "KB-01" in res[0]["kb_id"]


def test_get_all_registered_tools():
    """测试工具注册中心加载。"""
    tools = get_all_registered_tools()
    assert len(tools) == 3
