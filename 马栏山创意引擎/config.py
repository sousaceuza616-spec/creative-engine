import os
"""
马栏山创意引擎 - 配置文件
"""
import os
import threading
from openai import OpenAI

# DeepSeek API 配置
DEEPSEEK_API_KEY = "sk-72f679dd47c447bc986afa3e096eacd5"
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

# 全局共享 OpenAI client（线程安全）
_shared_client = None
_lock = threading.Lock()


def get_client():
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

# Agent 角色定义（用于 Prompt 构建）
AGENT_ROLES = {
    "trend_analyst": "你是一个专业的文创行业热点分析师。你的工作是基于特定数据源中的真实内容，为品牌策划提供洞察分析。你需要：1. 从数据源中找出与品牌/行业相关的爆款内容 2. 提炼每条内容的成功逻辑和可借鉴点 3. 给出针对性的策创建议 4. 输出格式要结构化、清晰、可直接用于提案。始终保持专业、客观、有洞察力。",

    "headline_master": "你是一个创意标题大师。你的工作是针对品牌推广需求，生成有吸引力、有传播力的标题。你需要：1. 理解品牌调性和推广目标 2. 生成多个不同风格的标题选项 3. 能够根据反馈意见调整和优化标题 4. 保持创意与品牌调性的平衡。标题风格包括：情感共鸣型、悬念好奇型、价值直给型、文化底蕴型等。",

    "editor_in_chief": "你是一个资深的品牌主编。你的工作是：1. 审核标题大师生成的内容是否符合品牌调性 2. 对不符合品牌调性的内容给出具体的、有深度的驳回理由 3. 指导标题大师朝正确的方向修改 4. 基于所有分析结果，生成完整的策创方案大纲。你的核心能力是对品牌调性的深刻理解，而不是机械的关键词过滤。"
}