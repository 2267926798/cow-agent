"""系统环境与模型服务配置文件。

包含应用配置、LLM 密钥、数据库连接及 MCP 服务节点地址。
"""

import os
from typing import Optional
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """应用全局配置管理类。"""

    APP_NAME: str = "Smart-Dairy-Farm-Agent"
    APP_ENV: str = Field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    DEBUG: bool = Field(default_factory=lambda: os.getenv("DEBUG", "true").lower() == "true")
    PORT: int = Field(default_factory=lambda: int(os.getenv("PORT", "8000")))
    HOST: str = Field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))

    # 大模型 API 配置
    OPENAI_API_KEY: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", "mock-openai-key"))
    OPENAI_API_BASE: str = Field(default_factory=lambda: os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"))
    MODEL_NAME: str = Field(default_factory=lambda: os.getenv("MODEL_NAME", "gpt-4o"))
    LIGHT_MODEL_NAME: str = Field(default_factory=lambda: os.getenv("LIGHT_MODEL_NAME", "gpt-4o-mini"))
    TEMPERATURE: float = 0.2

    # Redis 配置 (状态 Checkpoint 持久化)
    REDIS_HOST: str = Field(default_factory=lambda: os.getenv("REDIS_HOST", "127.0.0.1"))
    REDIS_PORT: int = Field(default_factory=lambda: int(os.getenv("REDIS_PORT", "6379")))
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # MCP (Model Context Protocol) 模式开关与节点地址
    USE_MCP_SERVICES: bool = Field(default_factory=lambda: os.getenv("USE_MCP_SERVICES", "false").lower() == "true")
    MCP_IOT_SERVER_URL: str = "http://127.0.0.1:9001/sse"
    MCP_MYSQL_SERVER_URL: str = "http://127.0.0.1:9002/sse"
    MCP_RAG_SERVER_URL: str = "http://127.0.0.1:9003/sse"

    # 状态机与安全限额
    MAX_LOOP_COUNT: int = 3
    RECURSION_LIMIT: int = 16
    MAX_HANDOFF_COUNT: int = 6


# 实例化全局单例配置
settings = Settings()
