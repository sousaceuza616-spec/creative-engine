"""
数据加载模块 — 集中管理预置数据集的加载与缓存
"""
import json
import os
from functools import lru_cache
from typing import Any, Optional

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

_FILE_MAP: dict[str, str] = {
    "小红书": os.path.join(_DATA_DIR, "xiaohongshu.json"),
    "B站": os.path.join(_DATA_DIR, "bilibili.json"),
    "抖音": os.path.join(_DATA_DIR, "douyin.json"),
}


@lru_cache(maxsize=8)
def load_data(data_source_name: str) -> Optional[dict[str, Any]]:
    """加载指定数据源的预置数据集，结果被缓存以避免重复 I/O

    Args:
        data_source_name: "小红书" / "B站" / "抖音"

    Returns:
        解析后的 JSON dict，或 None（数据源不存在时）
    """
    fp = _FILE_MAP.get(data_source_name)
    if not fp or not os.path.exists(fp):
        return None
    with open(fp, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def clear_cache() -> None:
    """清除数据加载缓存（测试用 / 数据文件更新后调用）"""
    load_data.cache_clear()


def available_sources() -> list[str]:
    """返回实际存在数据文件的可用数据源列表"""
    return [name for name, fp in _FILE_MAP.items() if os.path.exists(fp)]
