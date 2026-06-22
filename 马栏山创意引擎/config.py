"""
马栏山创意引擎 - 配置文件
"""
import os
import random
import time
import logging
import threading
from typing import Any, Callable
from openai import OpenAI

logger = logging.getLogger(__name__)

# DeepSeek API 配置
DEEPSEEK_API_KEY = "sk-72f679dd47c447bc986afa3e096eacd5"
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

# 全局共享 OpenAI client（线程安全）
_shared_client = None
_lock = threading.Lock()


def get_client() -> OpenAI:
    """获取共享的 OpenAI client 实例（线程安全）"""
    global _shared_client
    if not DEEPSEEK_API_KEY:
        raise RuntimeError(
            "DEEPSEEK_API_KEY 未设置！\n"
            "请将 .env.example 复制为 .env 并填入你的 API Key，\n"
            "或在运行前执行: export DEEPSEEK_API_KEY=你的Key"
        )
    if _shared_client is None:
        with _lock:
            if _shared_client is None:
                _shared_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    return _shared_client


def api_call_with_retry(
    call_fn: Callable[[], Any],
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> Any:
    """以指数退避重试方式调用 API

    区分"临时错误"（网络波动、超时）和"永久错误"（认证失败、模型不存在）：
    - 临时错误：重试最多 max_retries 次
    - 永久错误：立即抛出，不浪费重试次数

    Args:
        call_fn: API 调用函数（无参）
        max_retries: 最大重试次数（默认 3）
        base_delay: 基础等待秒数，每轮翻倍（默认 1 秒）

    Returns:
        API 响应对象

    Raises:
        RuntimeError: 永久错误或所有重试耗尽后包装抛出
    """
    permanent_error_keywords = (
        "authentication", "auth_error", "invalid_api_key", "permission",
        "model_not_found", "insufficient_quota", "rate_limit_exceeded",
        "invalid_request_error",
    )

    for attempt in range(max_retries + 1):
        try:
            return call_fn()
        except Exception as e:
            err_str = str(e).lower()

            # 检查是否为永久错误 → 立即抛出
            if any(kw in err_str for kw in permanent_error_keywords):
                logger.error("Permanent API error, not retrying: %s", e)
                raise RuntimeError(f"API 调用遇到不可恢复错误: {e}") from e

            # 最后一次尝试仍失败 → 抛出
            if attempt >= max_retries:
                logger.error("API call failed after %d retries: %s", max_retries, e)
                raise RuntimeError(f"API 调用在 {max_retries} 次重试后仍失败: {e}") from e

            # 指数退避 + 随机抖动
            delay = base_delay * (2 ** attempt) + random.uniform(0, 0.5)
            logger.warning(
                "API call attempt %d/%d failed (%s), retrying in %.1fs...",
                attempt + 1, max_retries + 1, e, delay,
            )
            time.sleep(delay)
