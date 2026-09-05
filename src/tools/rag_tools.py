"""兽医 SOP 与向量知识库检索工具 (本地模式)。

根据症状关键字匹配兽医诊疗 SOP 与用药规程。
"""

import time
from typing import List, Dict, Any
from langchain_core.tools import tool
from src.utils.logger import log_tool_execution


def search_vector_kb_mock(query_tags: str) -> List[Dict[str, Any]]:
    """模拟向量数据库 (Milvus/Qdrant) 混合检索与重排。

    入参 1 个，符合规范约束。
    """
    results = [
        {
            "kb_id": "KB-01",
            "title": "《牧场隐性乳房炎 SOP 诊疗规程》",
            "section": "第 3.2 节 诊断与隔离",
            "content": "当牛只直肠体温 > 39.5℃ 且 24 小时反刍时间下降 > 30% 时，需优先进行 CMT (隐性乳房炎) 检测试剂盘核查。若 CMT 显阳性，立即隔离至观察舍，使用头孢噻呋钠悬浮剂进行乳房灌注。",
            "score": 0.92
        },
        {
            "kb_id": "KB-02",
            "title": "《奶牛热应激与急救标准 SOP》",
            "section": "第 1.4 节 物理降温规程",
            "content": "夏季体温升至 39.5℃ 以上但反刍无明显剧烈下降时，应排查喷淋风扇故障与热应激。处置：启用强力喷淋降温。",
            "score": 0.75
        }
    ]
    return results


@tool
def search_veterinary_knowledge_base(query_tags: str) -> str:
    """根据提取的症状关键字与异常指标，检索兽医 SOP 诊疗规程与用药标准指南。"""
    start_time = time.time()
    items = search_vector_kb_mock(query_tags)
    latency_ms = (time.time() - start_time) * 1000
    log_tool_execution("sess_mock", "search_veterinary_knowledge_base", "SUCCESS", latency_ms)

    output = []
    for item in items:
        output.append(f"[{item['kb_id']}] {item['title']} ({item['section']})\n匹配内容: {item['content']}")
    
    return "\n\n".join(output)
