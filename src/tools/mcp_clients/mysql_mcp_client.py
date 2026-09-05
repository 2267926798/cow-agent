"""MySQL 牛只档案与病历库 MCP 客户端适配器。
"""

from src.tools.mcp_clients.base_mcp_client import BaseMCPClient
from src.tools.cow_profile_tools import query_cow_profile_and_history


class MySQLMCPClient(BaseMCPClient):
    """MySQL 档案病历专用 MCP 客户端。"""

    def __init__(self, server_url: str):
        """初始化 MySQL MCP 客户端。

        形参 1 个，符合规范约束。
        """
        super().__init__(server_url, "MySQL-Profile-MCP")

    def get_tool(self):
        """获取封装后的 LangChain Tool 对象。"""
        self.connect()
        return query_cow_profile_and_history
