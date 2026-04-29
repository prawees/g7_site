#!/usr/bin/env python3
"""
RAMA G7 site builder.

Converts content/posts/*.md into static HTML in public/.
Reads templates from templates/.
Copies static/ as-is.

Usage
    python3 scripts/build.py

Markdown front matter expected at top of each post, fenced by ---:

    ---
    title: The post title
    lede: One-sentence summary that appears under the title.
    date: 2026-04-29
    author: Smart
    category: Editorial
    description: Used for the index card and meta description.
    ---

Vancouver-style citations
    In the body, write inline as [1], [2], [3].
    At the end of the post, add a section starting with:

        ## References

        1. Author A, Author B. Title. Journal. 2024;12(3):456-78.
        2. Author C. ...

    The builder pulls that section out, formats it as a proper
    references block, and turns the inline [1] markers into
    superscript anchor links to the references.
"""

import os
import re
import sys
import shutil
import datetime
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "posts"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
PUBLIC = ROOT / "public"


def read_template(name):
    return (TEMPLATES / name).read_text(encoding="utf-8")


def parse_frontmatter(text):
    """Return (metadata dict, body str)."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        raise ValueError("Missing front matter")
    fm_block, body = m.group(1), m.group(2)
    meta = {}
    for line in fm_block.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()
    return meta, body


def split_references(body):
    """
    Split out a trailing '## References' section.
    Returns (body without references, list of reference strings).
    """
    parts = re.split(r"\n##\s+References\s*\n", body, maxsplit=1, flags=re.IGNORECASE)
    if len(parts) == 1:
        return body, []
    main, refs_block = parts
    refs = []
    for line in refs_block.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^(\d+)\.\s+(.*)$", line)
        if m:
            refs.append(m.group(2).strip())
    return main, refs


def render_inline_citations(body, num_refs):
    """
    Convert bare [n] markers in body text into <sup class="cite"><a href="#ref-n">n</a></sup>.
    Skips [n] inside code fences and inline code.
    """
    out = []
    in_fence = False
    for line in body.split("\n"):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue

        # Protect inline code
        chunks = re.split(r"(`[^`]+`)", line)
        for i, chunk in enumerate(chunks):
            if chunk.startswith("`"):
                continue

            def replace(m):
                inside = m.group(1)
                # Handles "1", "1,2", "1, 2, 5"
                if not re.fullmatch(r"\s*\d+(\s*,\s*\d+)*\s*", inside):
                    return m.group(0)
                nums = [int(x) for x in re.split(r"\s*,\s*", inside.strip())]
                if not all(1 <= n <= num_refs for n in nums):
                    return m.group(0)
                links = ",".join(
                    f'<a href="#ref-{n}">{n}</a>' for n in nums
                )
                return f'<sup class="cite">{links}</sup>'

            chunks[i] = re.sub(r"\[([\d,\s]+)\]", replace, chunk)
        out.append("".join(chunks))
    return "\n".join(out)


def render_markdown(md):
    """
    Minimal Markdown to HTML, just what we use in editorial pieces.
    Handles, in this order
        fenced code blocks
        h1/h2/h3 headings
        blockquotes
        ordered and unordered lists
        bold, italic, inline code
        links
        paragraph wrapping
    """
    # Fenced code blocks
    code_blocks = []
    def stash_code(m):
        code_blocks.append(m.group(1))
        return f"\x00CODE{len(code_blocks) - 1}\x00"
    md = re.sub(r"```(?:[\w-]+)?\n(.*?)```", stash_code, md, flags=re.DOTALL)

    lines = md.split("\n")
    html_lines = []
    para_buffer = []
    list_stack = []
    in_blockquote = False

    def flush_para():
        if para_buffer:
            text = " ".join(para_buffer).strip()
            if text:
                html_lines.append(f"<p>{render_inline(text)}</p>")
            para_buffer.clear()

    def flush_lists():
        while list_stack:
            tag = list_stack.pop()
            html_lines.append(f"</{tag}>")

    def flush_blockquote():
        nonlocal in_blockquote
        if in_blockquote:
            html_lines.append("</blockquote>")
            in_blockquote = False

    for line in lines:
        # Heading
        h = re.match(r"^(#{1,6})\s+(.+)$", line)
        if h:
            flush_para(); flush_lists(); flush_blockquote()
            level = len(h.group(1))
            html_lines.append(f"<h{level}>{render_inline(h.group(2))}</h{level}>")
            continue

        # Blockquote
        if line.startswith("> "):
            flush_para(); flush_lists()
            if not in_blockquote:
                html_lines.append("<blockquote>")
                in_blockquote = True
            html_lines.append(f"<p>{render_inline(line[2:])}</p>")
            continue
        else:
            flush_blockquote()

        # Unordered list
        ul = re.match(r"^[\-\*]\s+(.+)$", line)
        ol = re.match(r"^\d+\.\s+(.+)$", line)
        if ul or ol:
            flush_para()
            tag = "ul" if ul else "ol"
            if not list_stack or list_stack[-1] != tag:
                flush_lists()
                html_lines.append(f"<{tag}>")
                list_stack.append(tag)
            content = ul.group(1) if ul else ol.group(1)
            html_lines.append(f"<li>{render_inline(content)}</li>")
            continue
        else:
            flush_lists()

        # Horizontal rule
        if re.match(r"^---+$", line.strip()):
            flush_para()
            html_lines.append("<hr>")
            continue

        # Blank line ends paragraph
        if not line.strip():
            flush_para()
            continue

        para_buffer.append(line.strip())

    flush_para(); flush_lists(); flush_blockquote()
    out = "\n".join(html_lines)

    # Restore code blocks
    def unstash(m):
        idx = int(m.group(1))
        return f"<pre><code>{html.escape(code_blocks[idx])}</code></pre>"
    out = re.sub(r"\x00CODE(\d+)\x00", unstash, out)
    return out


def render_inline(text):
    """Inline markdown, bold italic code links."""
    # Inline code
    code_spans = []
    def stash_inline_code(m):
        code_spans.append(m.group(1))
        return f"\x01C{len(code_spans) - 1}\x01"
    text = re.sub(r"`([^`]+)`", stash_inline_code, text)

    # Links [text](url)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                  lambda m: f'<a href="{html.escape(m.group(2))}">{m.group(1)}</a>',
                  text)
    # Bold
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", text)

    # Restore inline code
    text = re.sub(r"\x01C(\d+)\x01",
                  lambda m: f"<code>{html.escape(code_spans[int(m.group(1))])}</code>",
                  text)
    return text


def reading_time_minutes(text):
    words = len(re.findall(r"\S+", text))
    return max(1, round(words / 220))


def format_date_label(iso):
    try:
        d = datetime.date.fromisoformat(iso)
    except Exception:
        return iso
    return d.strftime("%d %b %Y").upper()


def render_references_block(refs):
    if not refs:
        return ""
    items = []
    for i, ref in enumerate(refs, 1):
        items.append(f'<li id="ref-{i}">{render_inline(ref)}</li>')
    return f'''
<section class="references">
  <h3>References</h3>
  <ol>
    {"".join(items)}
  </ol>
</section>'''


def render_layout(content, title, description, og_type="website",
                  active_nav=""):
    base = read_template("base.html")
    out = base.replace("{{content}}", content)
    out = out.replace("{{title}}", html.escape(title))
    out = out.replace("{{description}}", html.escape(description))
    out = out.replace("{{og_type}}", og_type)
    out = out.replace("{{year}}", str(datetime.date.today().year))
    for slot, key in [("{{nav_home}}", "home"),
                      ("{{nav_about}}", "about"),
                      ("{{nav_join}}", "join")]:
        out = out.replace(slot, "active" if active_nav == key else "")
    return out


def build_post(md_path):
    raw = md_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(raw)

    required = ["title", "lede", "date", "author", "category"]
    for k in required:
        if k not in meta:
            raise ValueError(f"{md_path.name} missing front matter key: {k}")

    body_main, refs = split_references(body)
    body_with_cites = render_inline_citations(body_main, len(refs))
    html_body = render_markdown(body_with_cites)
    refs_block = render_references_block(refs)

    post_template = read_template("post.html")
    rt = reading_time_minutes(body_main)

    page = post_template
    page = page.replace("{{title}}", html.escape(meta["title"]))
    page = page.replace("{{lede}}", html.escape(meta["lede"]))
    page = page.replace("{{date_label}}", format_date_label(meta["date"]))
    page = page.replace("{{author}}", html.escape(meta["author"]))
    page = page.replace("{{category}}", html.escape(meta["category"]))
    page = page.replace("{{reading_time}}", str(rt))
    page = page.replace("{{body}}", html_body)
    page = page.replace("{{references_block}}", refs_block)

    full_html = render_layout(
        page,
        title=f'{meta["title"]} — RAMA G7 Club',
        description=meta.get("description", meta["lede"]),
        og_type="article",
    )

    slug = md_path.stem
    out_path = PUBLIC / "posts" / f"{slug}.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(full_html, encoding="utf-8")

    return {
        "slug": slug,
        "title": meta["title"],
        "lede": meta["lede"],
        "date": meta["date"],
        "date_label": format_date_label(meta["date"]),
        "author": meta["author"],
        "category": meta["category"],
        "description": meta.get("description", meta["lede"]),
        "url": f"/posts/{slug}.html",
    }


def build_index(posts):
    posts = sorted(posts, key=lambda p: p["date"], reverse=True)

    cards = []
    for i, p in enumerate(posts, 1):
        cards.append(f'''
<a class="post-card fade-up" href="{p["url"]}">
  <div class="post-card-num">№ {i:02d}</div>
  <div>
    <div class="post-card-meta">{html.escape(p["date_label"])} &nbsp;·&nbsp; {html.escape(p["category"])}</div>
    <div class="post-card-title">{html.escape(p["title"])}</div>
    <div class="post-card-summary">{html.escape(p["lede"])}</div>
    <div class="post-card-author">By {html.escape(p["author"])}</div>
  </div>
</a>''')

    index_template = read_template("index.html")
    page = index_template.replace("{{post_cards}}", "\n".join(cards))

    full = render_layout(
        page,
        title="RAMA G7 Club — Editorial",
        description="Editorial writing on medical AI and innovation by medical students at Ramathibodi Hospital.",
        active_nav="home",
    )
    (PUBLIC / "index.html").write_text(full, encoding="utf-8")


def build_static_page(slug, title, content_html, description, nav_key):
    page = f'<div class="static-page fade-up">{content_html}</div>'
    full = render_layout(
        page, title=f"{title} — RAMA G7 Club",
        description=description, active_nav=nav_key,
    )
    (PUBLIC / f"{slug}.html").write_text(full, encoding="utf-8")


def copy_static():
    dst = PUBLIC / "static"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(STATIC, dst)


def main():
    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    PUBLIC.mkdir()

    copy_static()

    posts = []
    for md in sorted(CONTENT.glob("*.md")):
        if md.name.startswith("_"):
            continue
        try:
            posts.append(build_post(md))
            print(f"  built post  {md.name}")
        except Exception as e:
            print(f"  FAILED      {md.name}: {e}", file=sys.stderr)
            sys.exit(1)

    build_index(posts)
    print(f"  built index ({len(posts)} posts)")

    about_html = '''
<h1>เกี่ยวกับ RAMA G7</h1>
<p class="lede" style="font-size: 1.2rem; line-height: 1.55; color: var(--muted); font-family: var(--font-display); font-style: italic; margin-bottom: var(--s-6);">ชมรมนวัตกรรมทางการแพทย์ที่ดำเนินโดยนักศึกษาที่อยากสร้างมากกว่ารวบรวม</p>

<p>RAMA G7 คือชมรมแพทย์นวัตกรรามา ที่โรงพยาบาลรามาธิบดี มหาวิทยาลัยมหิดล เราเป็นนักศึกษาแพทย์ที่สนใจ medical AI และ biomedical engineering และคิดว่าวงการนี้ต้องการการเขียนที่รอบคอบมากกว่าการโฆษณา</p>

<p>เว็บนี้รวมงานเขียนและบันทึกจากสมาชิก ทุกชิ้นลงชื่อผู้เขียน อ้างอิงสไตล์ Vancouver เราพยายามบอกว่างานวิจัยแต่ละชิ้นพิสูจน์อะไรไม่ได้ ควบคู่ไปกับสิ่งที่พิสูจน์ได้</p>

<h2>คณะกรรมการ</h2>
<ul>
  <li><strong>Big</strong>, ประธาน สนใจ robotics และ neurosurgery</li>
  <li><strong>Smart</strong>, รองประธาน สนใจ PM&amp;R, biosensor research, AI tooling</li>
</ul>

<h2>ติดต่อ</h2>
<p>คำถามด้านบทความ ข้อเสนอแนะ paper หรือความร่วมมือ <a href="mailto:rama.g7.club@gmail.com">rama.g7.club@gmail.com</a></p>
'''
    build_static_page("about", "About", about_html,
                      "About RAMA G7 Club at Ramathibodi Hospital, Mahidol University.",
                      "about")
    print("  built about")

    join_html = '''
<h1>สมัครเข้า RAMA G7</h1>
<p class="lede" style="font-size: 1.2rem; line-height: 1.55; color: var(--muted); font-family: var(--font-display); font-style: italic; margin-bottom: var(--s-6);">เรารับสมาชิกใหม่ปีละครั้ง</p>

<p>เปิดรับสมาชิกรุ่น 2026 แล้ว เรามองหานักศึกษาแพทย์ทุกชั้นปีที่อยาก <em>สร้าง</em> งานนวัตกรรมการแพทย์ ไม่ใช่แค่อ่าน</p>

<h2>เรามองหาใคร</h2>
<p>เราสนใจนักศึกษาที่เคยเริ่มโปรเจกต์ที่ยังไม่จบ อ่าน paper อย่างวิจารณ์ได้ หรือยินดีจะใช้เวลาเดือนละไม่กี่ชั่วโมงทำอะไรเป็นรูปธรรมออกมา ไม่จำเป็นต้องมีพื้นฐานเทคนิคแน่น แต่ต้องพร้อมเขียนงานในชื่อตัวเอง</p>

<h2>วิธีสมัคร</h2>
<p>แบบฟอร์มสมัคร <a href="https://forms.gle/ps8oq7SiBsEVEcjK8" target="_blank" rel="noopener">forms.gle/ps8oq7SiBsEVEcjK8</a></p>
<p>คำถามก่อนสมัคร <a href="mailto:rama.g7.club@gmail.com">rama.g7.club@gmail.com</a></p>
'''
    build_static_page("join", "Join", join_html,
                      "Join RAMA G7 Club. Application open for the 2026 cohort.",
                      "join")
    print("  built join")

    # 404
    notfound = '<div class="static-page"><h1>ไม่พบหน้านี้</h1><p>ลองกลับไปที่ <a href="/">หน้ารวมบทความ</a></p></div>'
    full404 = render_layout(notfound, "Not found — RAMA G7 Club",
                             "Page not found.", active_nav="")
    (PUBLIC / "404.html").write_text(full404, encoding="utf-8")

    print(f"\nbuild ok. output is in public/")


if __name__ == "__main__":
    main()
