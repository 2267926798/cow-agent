"""Agent 工具注册中心模块。

根据配置切换加载本地直连工具还是远程 MCP 客户端适配器。
"""

from typing import List
from langchain_core.tools import BaseTool
from config.settings import settings
from src.tools.iot_tools import query_cow_iot_metrics
from src.tools.cow_profile_tools import query_cow_profile_and_history
from src.tools.rag_tools import search_veterinary_knowledge_base
from src.tools.mcp_clients.iot_mcp_client import IoTMCPClient
from src.tools.mcp_clients.mysql_mcp_client import MySQLMCPClient
from src.tools.mcp_clients.rag_mcp_client import RAGMCPClient
from src.utils.logger import logger


def get_all_registered_tools() -> List[BaseTool]:
    """根据 settings.USE_MCP_SERVICES 获取曝光给 Agent 状态机调用的工具集合。

    无形参，符合规范要求。
    """
    tools = []

    if settings.USE_MCP_SERVICES:
        logger.info("Initializing Agent Tools via MCP Clients mode...")
        tools.append(IoTMCPClient(settings.MCP_IOT_SERVER_URL).get_tool())
        tools.append(MySQLMCPClient(settings.MCP_MYSQL_SERVER_URL).get_tool())
        tools.append(RAGMCPClient(settings.MCP_RAG_SERVER_URL).get_tool())
    else:
        logger.info("Initializing Agent Tools via Local Direct mode...")
        tools.append(query_cow_iot_metrics)
        tools.append(query_cow_profile_and_history)
        tools.append(search_veterinary_knowledge_base)

    return tools
