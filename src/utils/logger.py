"""结构化日志记录模块。

基于 loguru 提供统一的日志输出格式，自动注入上下文与关键参数。
"""

import sys
from loguru import logger

# 移除默认的 handler
logger.remove()

# 添加控制台结构化输出 handler
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level:<=8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
    level="INFO",
    enqueue=True,
)


def log_agent_step(session_id: str, cow_id: str, node_name: str, message: str) -> None:
    """记录 Agent 状态机节点关键步骤日志。

    入参控制在 4 个以内，符合代码规范要求。
    """
    logger.info(
        "[Session: {}] [Cow: {}] [Node: {}] - {}",
        session_id,
        cow_id,
        node_name,
        message,
    )


def log_tool_execution(session_id: str, tool_name: str, status: str, latency_ms: float) -> None:
    """记录 Tool 调用耗时与结果日志。

    入参控制在 4 个以内。
    """
    logger.info(
        "[Session: {}] [Tool: {}] Status: {} | Latency: {:.2f}ms",
        session_id,
        tool_name,
        status,
        latency_ms,
    )


def log_guardrail_alert(session_id: str, cow_id: str, alert_type: str, detail: str) -> None:
    """记录护栏拦截与告警日志。

    入参控制在 4 个以内。
    """
    logger.warning(
        "[Session: {}] [Cow: {}] [Guardrail: {}] - {}",
        session_id,
        cow_id,
        alert_type,
        detail,
    )
