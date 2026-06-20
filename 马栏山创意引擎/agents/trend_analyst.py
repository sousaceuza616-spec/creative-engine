"""
热点分析师 Agent
基于预置数据集分析竞品趋势，提炼爆款逻辑
"""
import json
import os
import logging
from config import get_client, DEEPSEEK_MODEL

logger = logging.getLogger(__name__)
client = get_client()


def _load_data(data_source_name):
    """加载预置数据集"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    file_map = {
        "小红书": os.path.join(data_dir, "xiaohongshu.json"),
        "B站": os.path.join(data_dir, "bilibili.json"),
        "抖音": os.path.join(data_dir, "douyin.json"),
    }
    fp = file_map.get(data_source_name)
    if not fp or not os.path.exists(fp):
        return None
    with open(fp, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def analyze_trend(brief, data_source_name, date_str=None):
    """基于指定数据源分析趋势（date_str 由 orchestrator 传入，避免重复工具调用）"""
    data = _load_data(data_source_name)
    if not data:
        return {"source": data_source_name, "error": "未找到" + data_source_name + "数据"}

    posts_summary = "\n".join([
        "- 《%s》| 互动量:%s | 主题:%s | 洞察:%s" % (
            p["title"],
            p.get("likes", p.get("plays", "N/A")),
            p["theme"],
            p["key_insight"]
        )
        for p in data["posts"]
    ])

    date_hint = ("当前日期：%s。" % date_str) if date_str else ""
    system_prompt = ("你是专业的文创行业热点分析师。\n"
                     "数据源是%s，分析角度是%s。\n"
                     "%s基于数据进行分析，确保方案时效性。"
                     ) % (data_source_name, data["angle"], date_hint)

    user_prompt = ("【策划需求】\n%s\n\n"
                   "【数据源】\n%s - %s\n\n"
                   "【数据内容】\n%s\n\n"
                   "【任务】\n"
                   "基于以上数据源中的真实内容，请：\n"
                   "1. 总结该数据源的核心趋势特征\n"
                   "2. 提炼2-3个可借鉴的爆款逻辑\n"
                   "3. 针对策划需求给出具体的策创建议\n"
                   "4. 指出这个角度最适合什么样的品牌调性\n\n"
                   "输出格式：\n"
                   "## 数据源分析：%s\n"
                   "### 核心趋势\n...\n"
                   "### 爆款逻辑提炼\n...\n"
                   "### 策创建议\n...\n"
                   "### 适合的品牌调性\n..."
                   ) % (brief, data_source_name, data["angle"], posts_summary, data_source_name)

    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        analysis = response.choices[0].message.content
    except Exception as e:
        logger.exception("analyze_trend failed for source: %s", data_source_name)
        fallback_insight = data["posts"][0]["key_insight"] if data.get("posts") else "无"
        analysis = ("（API调用失败，使用本地预置数据兜底）\n\n"
                    "数据源：%s\n数据量：%d条\n核心洞察：%s") % (
            data_source_name, len(data.get("posts", [])),
            fallback_insight)

    return {
        "source": data_source_name,
        "angle": data["angle"],
        "analysis": analysis,
        "posts_count": len(data["posts"])
    }
