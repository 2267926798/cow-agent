"""按角色绑定轻量/重量聊天模型。

无真实 API Key 时返回 None，Worker 走确定性 mock 路径。
"""

from typing import Optional
from config.settings import settings
from src.utils.logger import logger

_MOCK_KEYS = {"", "mock-openai-key"}


def is_mock_llm_mode() -> bool:
    """判断当前是否应跳过真实 LLM 调用。"""
    return settings.OPENAI_API_KEY in _MOCK_KEYS


def get_chat_model(tier: str = "light"):
    """按 tier 返回 ChatOpenAI 或 None。

    tier: light 使用 LIGHT_MODEL_NAME，heavy 使用 MODEL_NAME。
    """
    if is_mock_llm_mode():
        logger.info("LLM factory: mock mode, skip ChatOpenAI (tier={})", tier)
        return None

    from langchain_openai import ChatOpenAI

    model_name = settings.LIGHT_MODEL_NAME if tier == "light" else settings.MODEL_NAME
    return ChatOpenAI(
        model=model_name,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_API_BASE,
        temperature=settings.TEMPERATURE,
    )
