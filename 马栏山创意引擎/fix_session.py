import os

PATH = r"E:\19563\Documents\ruantong\马栏山创意引擎\app.py"
with open(PATH, "r", encoding="utf-8") as f:
    c = f.read()

# Find the session state section and replace it
marker = "# 初始化 session state"
old_block = 'if "brief_val" not in st.session_state:\n    st.session_state.brief_val = "'
new_block = 'if "brief_val" not in st.session_state:\n    st.session_state.brief_val = "\u8336\u989c\u60a6\u8272 2026 \u7aef\u5348\u8282\u793e\u4ea4\u5a92\u4f53\u63a8\u5e7f\u65b9\u6848"'

# Find all lines with brief_val and replace them with the correct block
lines = c.split("\n")
new_lines = []
skip_next = False
for i, line in enumerate(lines):
    if skip_next:
        skip_next = False
        continue
    if 'if "brief_val" not in st.session_state:' in line:
        # Already correct, skip
        new_lines.append('if "brief_val" not in st.session_state:')
        # Find the next st.session_state line and use it
        if i+1 < len(lines) and "st.session_state.brief_val" in lines[i+1]:
            new_lines.append('    st.session_state.brief_val = "\u8336\u989c\u60a6\u8272 2026 \u7aef\u5348\u8282\u793e\u4ea4\u5a92\u4f53\u63a8\u5e7f\u65b9\u6848"')
            skip_next = True
        continue
    if "st.session_state.brief_val" in line:
        if i > 0 and 'if "brief_val" not in st.session_state:' in lines[i-1]:
            new_lines.append('    st.session_state.brief_val = "\u8336\u989c\u60a6\u8272 2026 \u7aef\u5348\u8282\u793e\u4ea4\u5a92\u4f53\u63a8\u5e7f\u65b9\u6848"')
        else:
            # This line has brief_val but no preceding if - add the if
            new_lines.append('if "brief_val" not in st.session_state:')
            new_lines.append('    st.session_state.brief_val = "\u8336\u989c\u60a6\u8272 2026 \u7aef\u5348\u8282\u793e\u4ea4\u5a92\u4f53\u63a8\u5e7f\u65b9\u6848"')
        continue
    new_lines.append(line)

c = "\n".join(new_lines)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(c)

try:
    compile(c, PATH, "exec")
    print("Syntax: OK")
    print(f"Lines: {c.count(chr(10))}")
    # Verify key features
    checks = [
        ('\u65b9\u6848\u4e3b\u9898' in c, "Label: 方案主题"),
        ("cta_cols" in c, "CTA centered"),
        ('#MainMenu' in c, "Hidden elements"),
        ('input:focus' in c, "Focus state"),
        ('\u00b7' in c, "Separators"),
        ('\u2192' in c, "Workflow desc"),
        ('\u8f93\u5165\u521b\u610f\u9700\u6c42' in c, "Subtitle"),
        ('\u8336\u989c\u60a6\u8272' in c, "Chinese text"),
    ]
    for ok, label in checks:
        print(f"  {label}: {'OK' if ok else 'MISSING'}")
except SyntaxError as e:
    print(f"ERROR: {e}")
    # Show lines around the error
    for i in range(max(0, 9), min(len(lines), 14)):
        print(f"  Line {i+1}: {repr(lines[i])[:100]}")
