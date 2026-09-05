"""Vector RAG 兽医 SOP 知识库 MCP 客户端适配器。
"""

from src.tools.mcp_clients.base_mcp_client import BaseMCPClient
from src.tools.rag_tools import search_veterinary_knowledge_base


class RAGMCPClient(BaseMCPClient):
    """Milvus Vector RAG 专用 MCP 客户端。"""

    def __init__(self, server_url: str):
        """初始化 RAG MCP 客户端。

        形参 1 个，符合规范约束。
        """
        super().__init__(server_url, "Milvus-RAG-MCP")

    def get_tool(self):
        """获取封装后的 LangChain Tool 对象。"""
        self.connect()
        return search_veterinary_knowledge_base
