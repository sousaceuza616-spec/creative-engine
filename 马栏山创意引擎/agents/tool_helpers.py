"""
工具辅助模块（保留供参考，当前未被任何模块引用）
日期由 orchestrator 一次性获取并传入各 agent
"""
from datetime import datetime


def get_current_date_str() -> str:
    """返回结构化日期字符串"""
    now = datetime.now()
    weekdays_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return f"{now.strftime('%Y年%m月%d日')}（{weekdays_cn[now.weekday()]}）"
