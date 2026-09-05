"""牛只基本档案与历史病历查询工具 (本地模式)。

提供牛只档案、胎次、泌乳期及历史诊疗记录查询。
"""

import time
from typing import Dict, Any
from langchain_core.tools import tool
from src.utils.logger import log_tool_execution


def fetch_cow_profile_mock(cow_id: str) -> Dict[str, Any]:
    """模拟查询 MySQL 数据库获取牛只档案与历史病例。

    入参 1 个，符合规范约束。
    """
    if cow_id == "8892":
        return {
            "cow_id": cow_id,
            "barn_id": "BARN-03",
            "parity": 2,
            "lactation_stage": "EARLY",
            "days_in_milk": 45,
            "history": [
                {
                    "date": "2026-07-10",
                    "disease": "右后乳区乳房炎",
                    "treatment": "青霉素灌注与头孢噻呋全身给药",
                    "veterinarian": "VET-002",
                    "status": "CURED"
                }
            ]
        }
    
    return {
        "cow_id": cow_id,
        "barn_id": "BARN-01",
        "parity": 1,
        "lactation_stage": "MID",
        "days_in_milk": 120,
        "history": []
    }


@tool
def query_cow_profile_and_history(cow_id: str) -> str:
    """查询牛只的基本档案 (胎次、泌乳期、牛舍) 及过往历史发病与诊疗记录。"""
    start_time = time.time()
    data = fetch_cow_profile_mock(cow_id)
    latency_ms = (time.time() - start_time) * 1000
    log_tool_execution("sess_mock", "query_cow_profile_and_history", "SUCCESS", latency_ms)

    history_str = "无既往病史"
    if data["history"]:
        item = data["history"][0]
        history_str = f"曾于 {item['date']} 患 [{item['disease']}] (方案:{item['treatment']})"

    return f"【牛只档案&病历】耳标:{cow_id} | 牛舍:{data['barn_id']} | 胎次:{data['parity']} | 泌乳阶段:{data['lactation_stage']}(产后{data['days_in_milk']}天) | 历史病理:{history_str}"
