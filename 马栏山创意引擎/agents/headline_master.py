"""
标题大师 Agent
多风格标题生成 + 自适应迭代优化
日期由 orchestrator 传入，避免重复工具调用
"""
import logging
from config import get_client, DEEPSEEK_MODEL

logger = logging.getLogger(__name__)
client = get_client()


def generate_headlines(brief, angle, date_str=None, count=2):
    """生成多个创意标题（date_str 由 orchestrator 传入）"""
    date_hint = ("当前日期：%s。" % date_str) if date_str else ""
    user_prompt = ("【策划需求】\n%s\n\n"
                   "【创意方向】\n%s\n\n"
                   "【任务】\n"
                   "请为以上策划需求生成%d个标题，要求：\n"
                   "1. 符合品牌调性\n"
                   "2. 有传播力、吸引力\n"
                   "3. 不同风格（情感型、悬念型、直给型、文化型等）\n\n"
                   "输出格式（每行一个，不要序号）：\n"
                   "标题1\n标题2"
                   ) % (brief, angle, count)

    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": "你是创意标题大师，擅长为品牌策划生成有传播力的标题。" + date_hint},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )
        result = response.choices[0].message.content
        headlines = result.strip().split("\n")
        result_list = []
        for h in headlines:
            h = h.strip()
            h = h.lstrip("0123456789.-   ")
            if h and h not in result_list:
                result_list.append(h)
        return result_list[:count]
    except Exception as e:
        logger.exception("generate_headlines failed for angle: %s", angle)
        fallback_titles = {
            "情感向": ["一键心动，治愈心灵的温暖角落", "情感共鸣，触动人心的品牌故事"],
            "科技向": ["颠覆想象，未来已来的智能生活", "科技赋能，创新引领的行业变革"],
            "国潮向": ["千年传承，东方美学的当代演绎", "国潮崛起，传统文化的全新表达"],
        }
        fb_list = fallback_titles.get(angle, ["创意标题 A", "创意标题 B"])
        return fb_list[:count]


def refine_headline(feedback, original_headline, brief, angle, date_str=None):
    """根据主编意见优化标题（date_str 由 orchestrator 传入）"""
    date_hint = ("当前日期：%s。" % date_str) if date_str else ""
    user_prompt = ("【策划需求】\n%s\n\n"
                   "【创意方向】\n%s\n\n"
                   "【原标题】\n%s\n\n"
                   "【主编意见】\n%s\n\n"
                   "【任务】\n"
                   "请根据主编的意见重新生成一个更好的标题。\n"
                   "只输出标题本身，不要多余内容。"
                   ) % (brief, angle, original_headline, feedback)

    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": "你是创意标题大师，擅长根据反馈优化标题。" + date_hint},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.exception("refine_headline failed for: %s", original_headline[:50])
        return original_headline
