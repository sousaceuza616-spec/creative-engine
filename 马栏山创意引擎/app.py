# -*- coding: utf-8 -*-
"""
马栏山创意引擎 - Streamlit 前端应用
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from orchestrator import run_full_pipeline

# 初始化 session state
if "brief_val" not in st.session_state:
    st.session_state.brief_val = "茶颜悦色 2026 端午节社交媒体推广方案"
def render_outline(text):
    """将 LLM 输出的 Markdown 渲染为 HTML（支持表格、标题层级、列表等）"""
    import re, html
    if not text:
        return ""
    lines = text.split("\n")
    parts = []
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith("|") and s.endswith("|"):
            table_rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_rows.append(lines[i].strip())
                i += 1
            if len(table_rows) >= 2 and "---" in table_rows[1]:
                header_cells = [c.strip() for c in table_rows[0].split("|")[1:-1]]
                data_rows = table_rows[2:]
                tbl = "<table style=\"width:100%;border-collapse:collapse;margin:0.8rem 0;font-size:0.9rem;\">"
                tbl += "<thead><tr>"
                for h in header_cells:
                    tbl += "<th style=\"background:#2b6cb0;color:white;padding:0.6rem 0.8rem;text-align:left;font-weight:600;border:1px solid #2b6cb0;\">" + html.escape(h) + "</th>"
                tbl += "</tr></thead><tbody>"
                for row in data_rows:
                    cells = [c.strip() for c in row.split("|")[1:-1]]
                    tbl += "<tr>"
                    for c in cells:
                        tbl += "<td style=\"padding:0.5rem 0.8rem;border:1px solid #e2e8f0;color:#4a5568;line-height:1.5;\">" + html.escape(c) + "</td>"
                    tbl += "</tr>"
                tbl += "</tbody></table>"
                parts.append(tbl)
            else:
                for row in table_rows:
                    parts.append("<p style=\"margin:0.3rem 0;color:#4a5568\">" + html.escape(row) + "</p>")
            continue
        if not s:
            parts.append('<div style="height:0.6rem"></div>')
        elif s.startswith("### "):
            parts.append("<h3 style=\"font-size:1.15rem;color:#2b6cb0;margin:1rem 0 0.4rem;font-weight:600\">" + html.escape(s[4:]) + "</h3>")
        elif s.startswith("## "):
            parts.append("<h2 style=\"font-size:1.3rem;color:#1a365d;margin:1.2rem 0 0.5rem;font-weight:700;padding-bottom:0.3rem;border-bottom:2px solid #e2e8f0\">" + html.escape(s[3:]) + "</h2>")
        elif s.startswith("# "):
            parts.append("<h1 style=\"font-size:1.5rem;color:#1a365d;margin:1.5rem 0 0.5rem;font-weight:700\">" + html.escape(s[2:]) + "</h1>")
        elif s.startswith("- ") or s.startswith("* "):
            parts.append("<li style=\"margin:0.25rem 0;color:#4a5568;line-height:1.7;padding-left:0.5rem\">" + html.escape(s[2:]) + "</li>")
        elif len(s) > 2 and s[0].isdigit() and s[1] in (".", "、", ")"):
            parts.append("<li style=\"margin:0.25rem 0;color:#4a5568;line-height:1.7\">" + html.escape(s) + "</li>")
        elif s.startswith(">"):
            parts.append("<blockquote style=\"margin:0.5rem 0;padding:0.5rem 1rem;border-left:3px solid #2b6cb0;background:#f7fafc;color:#4a5568;border-radius:0 6px 6px 0;\">" + html.escape(s[1:].strip()) + "</blockquote>")
        else:
            safe = html.escape(s)
            formatted = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe)
            formatted = re.sub(r"\*(.+?)\*", r"<em>\1</em>", formatted)
            parts.append("<p style=\"margin:0.4rem 0;line-height:1.8;color:#4a5568\">" + formatted + "</p>")
        i += 1
    content = "\n".join(parts)
    return "<div style=\"background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:1.5rem 2rem;box-shadow:0 1px 3px rgba(0,0,0,0.04)\">" + content + "</div>"

st.set_page_config(page_title="马栏山创意引擎", page_icon="", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""<style>
    @import url("https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&family=Noto+Sans+SC:wght@300;400;500;600&display=swap");

    html, body, [class*="css"] { font-family: "Noto Sans SC", sans-serif; }
    .main-header { font-family: "Noto Serif SC", serif; font-size: 2.5rem; font-weight: 700; color: #1a365d; margin-bottom: 0.3rem; line-height: 1.3; }
    .sub-header { font-size: 1rem; color: #555; margin-bottom: 2rem; }
    .wow-moment { background: linear-gradient(135deg, #fffaf0, #fefcbf); border: 2px solid #dd6b20; border-radius: 12px; padding: 1.5rem; margin: 1.5rem 0; }
    .wow-title { font-size: 1.3rem; font-weight: 700; color: #c05621; margin-bottom: 0.8rem; }
    .rejection-box { background: #fff5f5; border-left: 4px solid #e53935; padding: 0.8rem 1rem; margin: 0.5rem 0; border-radius: 0 6px 6px 0; }
    .refined-box { background: #f0faf0; border-left: 4px solid #43a047; padding: 0.8rem 1rem; margin: 0.5rem 0; border-radius: 0 6px 6px 0; }
    .footer-note { font-size: 0.85rem; color: #999; text-align: center; margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #eee; }
    .stButton > button { background: linear-gradient(135deg, #1a365d, #2b6cb0); color: white; font-weight: 600; padding: 0.5rem 2.5rem; border: none; border-radius: 8px; font-size: 1rem; }
    .stButton > button:hover { background: #1a365d; color: white; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} .stDeployButton {display: none !important;}
    .stTextInput label {display: none !important;} .stTextInput input:focus {border-color: #2b6cb0 !important;box-shadow: 0 0 0 2px rgba(43,108,176,0.2) !important;}
</style>""", unsafe_allow_html=True)

st.markdown('<div class="main-header">马栏山创意引擎</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">输入创意需求，3 大 AI 智能体自动生成完整文创策划方案</div>', unsafe_allow_html=True)

agent_cards = """<div style="display:flex;gap:0.8rem;margin-bottom:1.5rem;flex-wrap:wrap;">
  <div style="flex:1;min-width:150px;background:#f0f4ff;border-radius:10px;padding:0.8rem;text-align:center;">
    <div style="font-size:1.8rem;margin-bottom:0.2rem;">🔍</div>
    <div style="font-weight:600;color:#1a1a2e;font-size:0.95rem;">热点分析师</div>
    <div style="font-size:0.75rem;color:#666;margin-top:0.2rem;">三路数据源分析 · 爆款逻辑提炼</div>
  </div>
  <div style="flex:1;min-width:150px;background:#f0faf0;border-radius:10px;padding:0.8rem;text-align:center;">
    <div style="font-size:1.8rem;margin-bottom:0.2rem;">✏️</div>
    <div style="font-weight:600;color:#1a1a2e;font-size:0.95rem;">标题大师</div>
    <div style="font-size:0.75rem;color:#666;margin-top:0.2rem;">多风格标题生成 · 自适应优化</div>
  </div>
  <div style="flex:1;min-width:150px;background:#fff8e1;border-radius:10px;padding:0.8rem;text-align:center;">
    <div style="font-size:1.8rem;margin-bottom:0.2rem;">📝</div>
    <div style="font-weight:600;color:#1a1a2e;font-size:0.95rem;">主编 Agent</div>
    <div style="font-size:0.75rem;color:#666;margin-top:0.2rem;">品牌调性审核 · 策创方案编排</div>
  </div>
</div>"""
st.markdown(agent_cards, unsafe_allow_html=True)

st.markdown("""<div style="font-size:0.9rem;color:#4a5568;background:#f7fafc;padding:0.8rem 1rem;border-radius:8px;margin-bottom:1.2rem;border-left:3px solid #2b6cb0;">
📋 输入需求后，3 个智能体将依次完成：<b>热点分析</b>(多平台趋势洞察)→ <b>标题生成</b>(多风格创意标题)→ <b>方案编排</b>(完整策创方案)，自动输出结果
</div>""", unsafe_allow_html=True)

st.markdown('### 输入策创需求')
st.markdown('<div style="font-size:0.85rem;font-weight:500;color:#4a5568;margin-bottom:0.3rem;">方案主题</div>', unsafe_allow_html=True)

ex_cols = st.columns(3)
examples = [
    ("🥩 茶颜悦色端午推广", "茶颜悦色 2026 端午节社交媒体推广方案"),
    ("🎪 超级文和友国潮营销", "超级文和友夏季国潮定位营销策划"),
    ("🎯 长沙城市文旅推广", "长沙城市文旅推广方案"),
]
for i, (col, (label, val)) in enumerate(zip(ex_cols, examples)):
    with col:
        if st.button(label, use_container_width=True, type='secondary'):
            st.session_state.brief_val = val
            st.rerun()

with st.container():
    brief = st.text_input('请输入策划需求', value=st.session_state.brief_val, key='brief_input', label_visibility='collapsed', max_chars=500)
    st.markdown('<div style="font-size:0.85rem;font-weight:500;color:#4a5568;margin-bottom:0.3rem;">调性 / 补充要求（可选）</div>', unsafe_allow_html=True)
    brand_tone = st.text_input('品牌调性（可选，留空将根据 brief 自动推导）', value='', placeholder='可填写品牌调性、风格偏好、重点方向等补充要求', key='brand_tone_input', label_visibility='collapsed')
    cta_cols = st.columns([1,2,1])
    with cta_cols[1]:
        run_button = st.button('开始策划', type='primary', use_container_width=True)

if run_button and brief:
    if not brand_tone.strip():
        if '茶颜' in brief or '国潮' in brief or '传统' in brief:
            brand_tone = '内敛雅致、东方美学、文化底蕴'
        elif '科技' in brief or 'AI' in brief or '智能' in brief:
            brand_tone = '创新前沿、科技感、未来感'
        elif '年轻' in brief or '潮流' in brief or '社交' in brief:
            brand_tone = '年轻活力、时尚潮流、社交属性'
        else:
            brand_tone = '内敛雅致、东方美学、文化底蕴'

    status = st.status('🚀 马栏山创意引擎启动中...', expanded=True)
    def on_progress(step, msg):
        status.update(label=msg, state='running')
    result = run_full_pipeline(brief, brand_tone, progress_callback=on_progress)
    status.update(label='✅ 策创完成！', state='complete')
    status.container().markdown('### 策创结果')

    st.markdown('---')
    st.markdown('## 策创流程')

    st.markdown('### Step 1 : 热点分析')
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        with st.expander('情感向 - 小红书分析', expanded=False):
            detail = result["steps"]["analysis"]["detail"].get("小红书", {})
            analysis = detail.get("analysis", "分析中...")
            count = detail.get("posts_count", 0)
            st.markdown(f"数据量: {count} 条爆款内容")
            st.markdown(analysis)
    with col_b:
        with st.expander('科技向 - B站分析', expanded=False):
            detail = result["steps"]["analysis"]["detail"].get("B站", {})
            analysis = detail.get("analysis", "分析中...")
            count = detail.get("posts_count", 0)
            st.markdown(f"数据量: {count} 条爆款内容")
            st.markdown(analysis)
    with col_c:
        with st.expander('国潮向 - 抖音分析', expanded=False):
            detail = result["steps"]["analysis"]["detail"].get("抖音", {})
            analysis = detail.get("analysis", "分析中...")
            count = detail.get("posts_count", 0)
            st.markdown(f"数据量: {count} 条爆款内容")
            st.markdown(analysis)

    st.markdown('### Step 2 : 创意标题生成')
    hl_cols = st.columns(3)
    sources = ['小红书', 'B站', '抖音']
    for i, ds in enumerate(sources):
        detail = result["steps"]["headlines"]["detail"].get(ds, {})
        headlines = detail.get("headlines", [])
        angle = detail.get("angle", ds)
        with hl_cols[i]:
            st.markdown(f"**{angle}标题**")
            for h in headlines:
                st.markdown(f"- {h}")

    st.markdown('### Step 3 : 主编语义级审核')
    rd = result.get("rejection_demo")
    if rd:
        st.markdown('<div class="wow-moment"><div class="wow-title">✨ 语义级审核 - WOW 时刻</div>', unsafe_allow_html=True)
        st.markdown(f'**角度：** {rd["angle"]}')
        st.markdown('**原标题：**')
        st.markdown(f'<div class="rejection-box">{rd["original_headline"]}</div>', unsafe_allow_html=True)
        st.markdown('**主编驳回意见：**')
        st.markdown(f'<div class="rejection-box">{rd["feedback"]}</div>', unsafe_allow_html=True)
        st.markdown('**标题大师重新生成：**')
        st.markdown(f'<div class="refined-box">{rd["refined_headline"]}</div>', unsafe_allow_html=True)
        st.markdown('<p style="color:#c05621;font-weight:500;margin-top:0.8rem;">💡 系统具备品牌调性理解能力，而非关键词过滤</p></div>', unsafe_allow_html=True)

    with st.expander('查看所有标题审核结果', expanded=False):
        for item in result.get("reviewed_headlines", []):
            rev = item.get("review", {})
            icon = '✅' if rev.get('approved') else '❌'
            st.markdown(f'{icon} **{item["headline"]}** ({item["angle"]})')
            if rev.get("result"):
                st.markdown(f'   {rev["result"]}')

    st.markdown('### Step 4 : 策创方案大纲')
    outline = result.get("outline", "生成中...")
    st.markdown(render_outline(outline), unsafe_allow_html=True)

    if st.button('🔄 重新策创', type='secondary'):
        st.rerun()

    st.markdown('<div class="footer-note">马栏山创意引擎 V2.5</div>', unsafe_allow_html=True)

elif run_button and not brief:
    st.warning('请输入策划需求后再开始。')