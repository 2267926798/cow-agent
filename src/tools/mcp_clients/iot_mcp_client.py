"""TDengine 时序数据库 MCP 客户端适配器。

通过 MCP 协议拉取并封装远程 IoT 时序查询工具。
"""

from src.tools.mcp_clients.base_mcp_client import BaseMCPClient
from src.tools.iot_tools import query_cow_iot_metrics


class IoTMCPClient(BaseMCPClient):
    """IoT 时序专用 MCP 客户端。"""

    def __init__(self, server_url: str):
        """初始化 IoT MCP 客户端。

        形参 1 个，符合规范约束。
        """
        super().__init__(server_url, "TDengine-IoT-MCP")

    def get_tool(self):
        """获取封装后的 LangChain Tool 对象。"""
        self.connect()
        return query_cow_iot_metrics
