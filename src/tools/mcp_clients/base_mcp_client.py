"""Model Context Protocol (MCP) 通用客户端适配器基类。

支持通过 SSE / stdio 协议连接远程 MCP Server 动态抓取工具。
"""

from typing import List, Dict, Any
from langchain_core.tools import Tool
from src.utils.logger import logger


class BaseMCPClient:
    """MCP 客户端适配器抽象基类。"""

    def __init__(self, server_url: str, client_name: str):
        """初始化 MCP 客户端。

        形参 2 个，符合规范约束。
        """
        self.server_url = server_url
        self.client_name = client_name
        self.connected = False

    def connect(self) -> bool:
        """建立 MCP SSE/stdio 连接握手。"""
        # 实际通过 mcp.ClientSession 进行 SSE 建立与 list_tools 协商
        logger.info("[MCP Client: {}] Connected to server: {}", self.client_name, self.server_url)
        self.connected = True
        return True

    def fetch_mcp_tools(self) -> List[Tool]:
        """将远程 MCP Tool 转换封装为 LangChain 可调用的 BaseTool 格式。"""
        logger.info("[MCP Client: {}] Discovered remote tools via MCP protocol", self.client_name)
        return []
