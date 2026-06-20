"""
工具辅助模块（简化版）
日期由 orchestrator 一次性获取并传入各 agent，不再需要工具调用
"""
from datetime import datetime


def get_current_date_str():
    """返回结构化日期字符串（供 orchestrator 入口处一次性调用）"""
    now = datetime.now()
    weekdays_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return "%s（%s）" % (now.strftime("%Y年%m月%d日"), weekdays_cn[now.weekday()])
