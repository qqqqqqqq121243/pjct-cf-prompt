# -*- coding: utf-8 -*-
"""将 H3-prompt/skills 下的所有 SKILL.cn.md 整合为一个带样式的 HTML 阅读文档。"""
import re
import glob
import markdown

SRC_DIR = r"o:\project\pjct-cf-prompt\H3-prompt\skills"
OUT_FILE = r"o:\project\pjct-cf-prompt\H3-prompt\中文Skills合集.html"

FILES = sorted(glob.glob(SRC_DIR + r"\**\SKILL.cn.md", recursive=True))


def parse_list_lines(lines):
    """把 '- item' 列表行解析为字符串列表。"""
    items = []
    for ln in lines:
        m = re.match(r"^-\s+(.*)$", ln)
        if m and m.group(1).strip():
            items.append(m.group(1).strip())
    return items


def parse_nested(key, lines):
    """解析嵌套块：metadata 内的 key:value；其他块视为列表或文本。"""
    if key == "metadata":
        out = {}
        for ln in lines:
            mm = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", ln)
            if mm:
                out[mm.group(1)] = mm.group(2).strip()
        return out
    items = parse_list_lines(lines)
    if items:
        return {key: " | ".join(items)}
    return {key: " ".join(lines).strip()}


def parse_frontmatter(lines):
    """解析 YAML frontmatter，返回 (meta_dict, body_lines)。"""
    if not lines or lines[0].strip() != "---":
        return {}, lines
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, lines

    meta = {}
    block_key = None
    block_lines = []
    for raw in lines[1:end]:
        line = raw.rstrip()
        if block_key is not None:
            # 缩进行，或非 key:value 行（如无缩进的 YAML 列表项 "- item"），都属于当前块内容
            if line[:1] in (" ", "\t") or not re.match(r"^[A-Za-z0-9_-]+:", line):
                block_lines.append(line.strip())
                continue
            meta.update(parse_nested(block_key, block_lines))
            block_key = None
            block_lines = []
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if not val or val == "|":
                block_key = key
            else:
                meta[key] = val
    if block_key is not None:
        meta.update(parse_nested(block_key, block_lines))
    return meta, lines[end + 1:]


def prettify_triggers(raw):
    """把 [a, b, c] 数组字符串美化为 a、b、c。"""
    s = raw.strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    parts = [p.strip() for p in s.split(",") if p.strip()]
    return "、".join(parts) if parts else raw


def extract_title(body_text, fallback):
    m = re.search(r"^#\s+(.+)$", body_text, re.M)
    return m.group(1).strip() if m else fallback


CSS = """
:root {
  --sidebar-w: 300px;
  --accent1: #4f46e5; --accent2: #7c3aed; --accent3: #db2777;
  --bg: #f3f4f8; --card: #ffffff; --ink: #1f2430; --muted: #5c6270;
  --line: #e5e7ef;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  font-family: "Segoe UI", "Microsoft YaHei", "PingFang SC", sans-serif;
  background: var(--bg); color: var(--ink); line-height: 1.75;
}
/* 阅读进度条 */
#progress {
  position: fixed; top: 0; left: 0; height: 4px; width: 0; z-index: 100;
  background: linear-gradient(90deg, #6366f1, #a855f7, #db2777);
  transition: width .1s linear;
}
/* 侧边栏 */
.sidebar {
  position: fixed; top: 0; left: 0; width: var(--sidebar-w); height: 100vh;
  background: linear-gradient(180deg, #23263b, #191b2e);
  color: #e8e9f2; padding: 28px 20px; overflow-y: auto; z-index: 10;
}
.sidebar h1 {
  font-size: 18px; letter-spacing: 1px; margin-bottom: 4px;
  background: linear-gradient(90deg, #a5b4fc, #f0abfc);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.sidebar .sub { font-size: 12px; color: #8b90ab; margin-bottom: 22px; }
.sidebar nav a {
  display: block; color: #c6c9dc; text-decoration: none; font-size: 14px;
  padding: 9px 12px; border-radius: 8px; margin-bottom: 4px; transition: all .15s;
}
.sidebar nav a:hover { background: rgba(255,255,255,.08); color: #fff; padding-left: 16px; }
.sidebar nav a .idx {
  display: inline-block; width: 22px; height: 22px; line-height: 22px;
  text-align: center; font-size: 12px; font-weight: 700; border-radius: 50%;
  background: rgba(255,255,255,.12); margin-right: 8px; color: #c4b5fd;
}
.sidebar nav a.active { background: rgba(165,180,252,.18); color: #fff; }
/* 主区 */
.main { margin-left: var(--sidebar-w); padding: 0 32px 80px; }
.hero {
  background: linear-gradient(120deg, #4f46e5, #7c3aed 55%, #db2777);
  color: #fff; border-radius: 0 0 20px 20px; padding: 46px 40px; margin: 0 -32px 36px;
}
.hero h2 { font-size: 30px; letter-spacing: 1px; }
.hero p { margin-top: 10px; opacity: .92; font-size: 15px; max-width: 860px; }
.hero .chips { margin-top: 16px; display: flex; flex-wrap: wrap; gap: 8px; }
.hero .chips span {
  background: rgba(255,255,255,.18); border: 1px solid rgba(255,255,255,.35);
  padding: 3px 12px; border-radius: 999px; font-size: 12.5px;
}
/* Skill 卡片 */
.skill-card {
  background: var(--card); border-radius: 16px; box-shadow: 0 6px 24px rgba(31,36,48,.08);
  margin-bottom: 40px; overflow: hidden; border: 1px solid var(--line);
  scroll-margin-top: 24px;
}
.skill-head { padding: 26px 34px 20px; color: #fff; }
.skill-head h2 { font-size: 24px; display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.skill-head h2 .badge {
  font-size: 13px; font-weight: 700; padding: 3px 12px; border-radius: 999px;
  background: rgba(255,255,255,.22); letter-spacing: .5px;
}
.skill-head .words { font-size: 12.5px; opacity: .85; font-weight: 400; }
.skill-desc {
  margin-top: 12px; padding: 14px 18px; border-radius: 10px; font-size: 14px;
  background: rgba(255,255,255,.14); border-left: 4px solid rgba(255,255,255,.85);
}
.skill-meta { margin-top: 10px; font-size: 12.5px; opacity: .92; display: flex; flex-wrap: wrap; gap: 6px 14px; align-items: center; }
.skill-meta b { opacity: 1; }
.skill-meta code { background: rgba(255,255,255,.2); color: #fff; padding: 1px 8px; border-radius: 5px; }
.pill {
  display: inline-block; background: rgba(255,255,255,.2); border: 1px solid rgba(255,255,255,.4);
  padding: 1px 10px; border-radius: 999px; font-size: 12px; margin: 1px 2px;
}
.skill-body { padding: 26px 34px 34px; }
/* 正文排版 */
.skill-body h1 { display: none; }
.skill-body h2 {
  font-size: 20px; margin: 30px 0 12px; padding-bottom: 8px;
  border-bottom: 2px solid var(--line); color: var(--accent1);
}
.skill-body h2::after {
  content: ""; display: block; width: 48px; height: 3px; margin-top: 6px;
  border-radius: 2px; background: linear-gradient(90deg, var(--accent1), var(--accent3));
}
.skill-body h3 { font-size: 16.5px; margin: 22px 0 10px; color: var(--accent2); }
.skill-body h4 { font-size: 15px; margin: 18px 0 8px; color: var(--accent3); }
.skill-body p { margin: 8px 0; }
.skill-body ul, .skill-body ol { margin: 8px 0 8px 26px; }
.skill-body li { margin: 4px 0; }
.skill-body li::marker { color: var(--accent2); font-weight: 700; }
.skill-body strong { color: #b91c48; }
.skill-body a { color: var(--accent1); }
/* 表格 */
.skill-body table {
  border-collapse: collapse; width: 100%; margin: 14px 0; font-size: 14px;
  box-shadow: 0 2px 10px rgba(31,36,48,.06); border-radius: 10px;
}
.skill-body thead, .skill-body tbody { display: table; width: 100%; table-layout: fixed; }
.skill-body table-wrap { display: block; overflow-x: auto; }
.skill-body th {
  background: linear-gradient(120deg, #4f46e5, #7c3aed); color: #fff;
  padding: 10px 12px; text-align: left; font-weight: 600; font-size: 13.5px;
}
.skill-body td { padding: 9px 12px; border-bottom: 1px solid var(--line); vertical-align: top; }
.skill-body tr:nth-child(even) td { background: #f7f7fb; }
.skill-body tr:hover td { background: #eef0ff; }
/* 代码 */
.skill-body code {
  background: #eef0ff; color: #4f46e5; padding: 2px 6px; border-radius: 5px;
  font-family: "Cascadia Code", Consolas, monospace; font-size: 13px;
}
.skill-body pre {
  background: #1e2233; color: #dbe2ff; padding: 16px 18px; border-radius: 10px;
  overflow-x: auto; margin: 12px 0; font-size: 13px; line-height: 1.6;
}
.skill-body pre code { background: none; color: inherit; padding: 0; }
/* 引用 = 重点提示 */
.skill-body blockquote {
  margin: 14px 0; padding: 12px 16px; border-radius: 8px; font-size: 14px;
  background: #fff7ed; border-left: 4px solid #f97316;
}
.skill-body blockquote p { margin: 4px 0; }
.footer { text-align: center; color: var(--muted); font-size: 13px; margin-top: 20px; }
/* 响应式 */
@media (max-width: 900px) {
  .sidebar { position: static; width: 100%; height: auto; }
  .main { margin-left: 0; padding: 0 16px 60px; }
  .hero { margin: 0 -16px 24px; padding: 30px 22px; }
  .skill-body table { display: block; overflow-x: auto; }
}
"""

ACCENTS = [
    ("#6366f1", "#a855f7"),
    ("#0891b2", "#4f46e5"),
    ("#0d9488", "#6366f1"),
    ("#db2777", "#9333ea"),
    ("#ea580c", "#db2777"),
    ("#7c3aed", "#2563eb"),
    ("#16a34a", "#0891b2"),
    ("#c026d3", "#7c3aed"),
]

JS = """
window.addEventListener('scroll', function () {
  var h = document.documentElement;
  var p = h.scrollTop / (h.scrollHeight - h.clientHeight) * 100;
  document.getElementById('progress').style.width = p + '%';
});
"""


def main():
    md = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists"])
    sections = []
    nav_items = []
    all_names = []

    for n, path in enumerate(FILES, 1):
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
        meta, body = parse_frontmatter(raw.splitlines())
        body_text = "\n".join(body)
        title = extract_title(body_text, meta.get("name", f"Skill {n}"))
        word_count = len(re.sub(r"\s", "", body_text))

        md.reset()
        html = md.convert(body_text)

        name = meta.get("name", "")
        desc = meta.get("description", "")
        all_names.append(name)

        # 触发词：顶层或嵌套 metadata 内
        triggers = ""
        if "trigger-words" in meta:
            triggers = prettify_triggers(meta["trigger-words"])
        if not triggers and "metadata" in meta and isinstance(meta["metadata"], dict):
            tw = meta["metadata"].get("trigger-words", "")
            if tw:
                triggers = prettify_triggers(tw)

        tools = meta.get("allowed-tools", "")

        meta_html = f'<b>name:</b> <code>{name}</code>'
        if triggers:
            meta_html += f'<span><b>触发词:</b></span>'
            for t in triggers.split("、"):  # 每个触发词做成 pill
                meta_html += f'<span class="pill">{t}</span>'
        if tools:
            meta_html += f'<span><b>可用工具:</b></span>'
            for t in tools.split(" | "):
                meta_html += f'<span class="pill">{t}</span>'

        g1, g2 = ACCENTS[(n - 1) % len(ACCENTS)]
        head = f"""
<div class="skill-head" style="background:linear-gradient(120deg,{g1},{g2})">
  <h2><span class="badge">SKILL {n:02d}</span>{title}<span class="words">约 {word_count} 字</span></h2>
  <div class="skill-desc">{desc}</div>
  <div class="skill-meta">{meta_html}</div>
</div>"""
        sections.append(f'<section class="skill-card" id="skill-{n}">\n{head}\n<div class="skill-body">\n{html}\n</div>\n</section>')
        nav_items.append(f'<a href="#skill-{n}"><span class="idx">{n:02d}</span>{title}</a>')

    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>H3 Prompt Skills 中文文档合集</title>
<style>{CSS}</style>
</head>
<body>
<div id="progress"></div>
<aside class="sidebar">
  <h1>H3 Skills 合集</h1>
  <div class="sub">中文版 SKILL 文档 · 共 {len(sections)} 篇</div>
  <nav>
    {chr(10).join(nav_items)}
  </nav>
</aside>
<main class="main">
  <div class="hero">
    <h2>H3 Prompt Skills 中文文档合集</h2>
    <p>本页面整合了 H3-prompt/skills 目录下全部 {len(sections)} 份中文 Skill 文档，覆盖 3D 动画、品牌宣传、游戏开场、手绘实拍、MV 字幕、产品广告、纸拼贴科普与纸艺定格科普等方向。左侧导航快速跳转，表格、代码与重点提示均已高亮，便于阅读。</p>
    <div class="chips">{''.join(f'<span>{t}</span>' for t in all_names)}</div>
  </div>
  {chr(10).join(sections)}
  <div class="footer">由 SKILL.cn.md 自动整合生成 · 共 {len(sections)} 篇</div>
</main>
<script>{JS}</script>
</body>
</html>"""

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"OK -> {OUT_FILE}  ({len(sections)} skills)")


if __name__ == "__main__":
    main()
