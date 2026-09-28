"""Agent 工具注册中心模块。

按 Supervisor 角色隔离工具面，并可在本地直连与 MCP 之间切换。
"""

from typing import List
from langchain_core.tools import BaseTool
from config.settings import settings
from src.agents.roles import COLLECTOR, KNOWLEDGE
from src.tools.iot_tools import query_cow_iot_metrics
from src.tools.cow_profile_tools import query_cow_profile_and_history
from src.tools.rag_tools import search_veterinary_knowledge_base
from src.tools.mcp_clients.iot_mcp_client import IoTMCPClient
from src.tools.mcp_clients.mysql_mcp_client import MySQLMCPClient
from src.tools.mcp_clients.rag_mcp_client import RAGMCPClient
from src.utils.logger import logger


def _local_collector_tools() -> List[BaseTool]:
    """本地采集工具子集。"""
    return [query_cow_iot_metrics, query_cow_profile_and_history]


def _local_knowledge_tools() -> List[BaseTool]:
    """本地知识检索工具子集。"""
    return [search_veterinary_knowledge_base]


def _mcp_collector_tools() -> List[BaseTool]:
    """MCP 采集工具子集。"""
    return [
        IoTMCPClient(settings.MCP_IOT_SERVER_URL).get_tool(),
        MySQLMCPClient(settings.MCP_MYSQL_SERVER_URL).get_tool(),
    ]


def _mcp_knowledge_tools() -> List[BaseTool]:
    """MCP 知识检索工具子集。"""
    return [RAGMCPClient(settings.MCP_RAG_SERVER_URL).get_tool()]


def get_tools_for_role(role: str) -> List[BaseTool]:
    """按角色返回允许调用的工具列表。"""
    use_mcp = settings.USE_MCP_SERVICES
    if use_mcp:
        logger.info("Initializing tools via MCP for role={}", role)
        collector = _mcp_collector_tools()
        knowledge = _mcp_knowledge_tools()
    else:
        logger.info("Initializing tools via Local Direct for role={}", role)
        collector = _local_collector_tools()
        knowledge = _local_knowledge_tools()

    mapping = {
        COLLECTOR: collector,
        KNOWLEDGE: knowledge,
    }
    return mapping.get(role, [])


def get_all_registered_tools() -> List[BaseTool]:
    """返回采集+知识工具并集（兼容旧测试与全局曝光）。"""
    return get_tools_for_role(COLLECTOR) + get_tools_for_role(KNOWLEDGE)
