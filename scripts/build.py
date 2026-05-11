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
import json
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

    # Images ![alt](url)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)",
                  lambda m: f'<img src="{html.escape(m.group(2))}" alt="{html.escape(m.group(1))}">',
                  text)
    # Links [text](url)
    text = re.sub(r"(?<!\!)\[([^\]]+)\]\(([^)]+)\)",
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


THAI_MONTHS_ABBR = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
                    "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]


def format_date_label(iso):
    try:
        d = datetime.date.fromisoformat(iso)
    except Exception:
        return iso
    return f"{d.day} {THAI_MONTHS_ABBR[d.month - 1]} {d.year + 543}"


TAG_CLASS_MAP = {
    "AI":            "tag-ai",
    "รังสีวิทยา":    "tag-radiology",
    "กฎหมาย":         "tag-law",
    "NLP":           "tag-nlp",
    "คลินิก":        "tag-clinical",
}


def tag_class(tag):
    return TAG_CLASS_MAP.get(tag.strip(), "tag-default")


def parse_tags(value):
    if not value:
        return []
    return [t.strip() for t in value.split(",") if t.strip()]


def member_photo_html(m):
    photo = m.get("photo", "")
    if photo:
        return f'<img src="/static/img/members/{html.escape(photo)}" alt="{html.escape(m.get("name",""))}" onerror="this.style.display=\\\'none\\\'">'
    initials = (m.get("nickname") or m.get("name") or "").strip()[:2]
    return f'<div class="member-initials">{html.escape(initials)}</div>'


def load_members():
    members_dir = ROOT / "content" / "members"
    if not members_dir.exists():
        return []
    out = []
    for md in sorted(members_dir.glob("*.md")):
        if md.name.startswith("_"):
            continue
        meta, body = parse_frontmatter(md.read_text(encoding="utf-8"))
        slug = re.sub(r"^\d+[-_]", "", md.stem)
        meta["slug"] = slug
        meta["url"] = f"/members/{slug}/"
        meta["bio_html"] = render_markdown(body) if body.strip() else ""
        out.append(meta)
    return out


def find_member_by_author(author, members):
    a = (author or "").strip().lower()
    if not a:
        return None
    for m in members:
        if (m.get("nickname") or "").strip().lower() == a:
            return m
        if a and a in (m.get("name_en") or "").strip().lower():
            return m
        if a and a in (m.get("name") or "").strip().lower():
            return m
    return None


def render_members_section(members):
    if not members:
        return ""
    cards = []
    for m in members:
        nickname_th = m.get("nickname_th", "")
        role = m.get("role", "")
        interests = m.get("interests", "")
        nick_html = f'<div class="member-nick">{html.escape(nickname_th)}</div>' if nickname_th else ""
        role_html = f'<div class="member-role">{html.escape(role)}</div>' if role else ""
        interests_html = f'<div class="member-interests">{html.escape(interests)}</div>' if interests else ""
        cards.append(f'''
<a class="member-card" href="{m["url"]}">
  <div class="member-photo">{member_photo_html(m)}</div>
  <div class="member-body">
    {nick_html}
    <div class="member-name">{html.escape(m.get("name",""))}</div>
    {role_html}
    {interests_html}
  </div>
</a>''')
    return f'''
<h2>สมาชิก</h2>
<div class="members-grid">{"".join(cards)}</div>'''


def render_author_bio(member):
    if not member:
        return ""
    interests = member.get("interests", "")
    interests_html = f'<div class="author-bio-interests">{html.escape(interests)}</div>' if interests else ""
    email = member.get("email", "")
    email_html = f'<a class="author-bio-email" href="mailto:{html.escape(email)}">{html.escape(email)}</a>' if email else ""
    nickname_th = member.get("nickname_th", "")
    nick_html = f'<div class="author-bio-nick">{html.escape(nickname_th)}</div>' if nickname_th else ""
    return f'''
<aside class="author-bio">
  <div class="author-bio-label">เกี่ยวกับผู้เขียน</div>
  <div class="author-bio-card">
    <div class="author-bio-photo">{member_photo_html(member)}</div>
    <div class="author-bio-body">
      {nick_html}
      <a class="author-bio-name" href="{member["url"]}">{html.escape(member.get("name",""))}</a>
      <div class="author-bio-role">{html.escape(member.get("role",""))}</div>
      {interests_html}
      {email_html}
    </div>
  </div>
</aside>'''


def build_member_page(member, posts):
    own = [p for p in posts
           if (p["author"] or "").strip().lower() == (member.get("nickname") or "").strip().lower()]
    posts_html = ""
    if own:
        items = "".join(
            f'<li><a href="{p["url"]}?v={{{{build_time}}}}">{html.escape(p["title"])}</a><span class="member-post-date">{html.escape(p["date_label"])}</span></li>'
            for p in own
        )
        posts_html = f'<h2>บทความที่เขียน</h2><ul class="member-posts">{items}</ul>'
    interests = member.get("interests", "")
    interests_html = f'<p><strong>Research interests.</strong> {html.escape(interests)}</p>' if interests else ""
    email = member.get("email", "")
    email_html = f'<p><strong>Contact.</strong> <a href="mailto:{html.escape(email)}">{html.escape(email)}</a></p>' if email else ""
    nickname_th = member.get("nickname_th", "")
    nick_block = f'<div class="member-profile-nick">{html.escape(nickname_th)}</div>' if nickname_th else ""

    page_html = f'''
<div class="member-profile fade-up">
  <a class="article-back" href="/about/">← About</a>
  <div class="member-profile-head">
    <div class="member-profile-photo">{member_photo_html(member)}</div>
    <div class="member-profile-info">
      {nick_block}
      <h1>{html.escape(member.get("name",""))}</h1>
      <p class="member-profile-role">{html.escape(member.get("role",""))}</p>
    </div>
  </div>
  {member.get("bio_html","")}
  {interests_html}
  {email_html}
  {posts_html}
</div>'''

    full = render_layout(
        f'<div class="static-wrap">{page_html}</div>',
        title=f'{member.get("name","")} | RAMA G7 Club',
        description=f'Profile of {member.get("name","")} ({member.get("nickname","")}), {member.get("role","")}.',
        active_nav="about",
    )
    out_path = PUBLIC / "members" / member['slug'] / "index.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(full, encoding="utf-8")


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
    out = out.replace("{{build_time}}", str(int(datetime.datetime.now().timestamp())))
    for slot, key in [("{{nav_home}}", "home"),
                      ("{{nav_about}}", "about"),
                      ("{{nav_join}}", "join")]:
        out = out.replace(slot, "active" if active_nav == key else "")
    return out


def build_post(md_path, members=None):
    members = members or []
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

    member = find_member_by_author(meta["author"], members)
    if member:
        author_byline = (
            f'<p class="article-byline">By '
            f'<a class="author-name" href="{member["url"]}">{html.escape(meta["author"])}</a>'
            f', RAMA G7</p>'
        )
        author_bio = render_author_bio(member)
    else:
        author_byline = (
            f'<p class="article-byline">By '
            f'<span class="author-name">{html.escape(meta["author"])}</span>'
            f', RAMA G7</p>'
        )
        author_bio = ""

    page = post_template
    page = page.replace("{{title}}", html.escape(meta["title"]))
    page = page.replace("{{lede}}", html.escape(meta["lede"]))
    page = page.replace("{{date_label}}", format_date_label(meta["date"]))
    page = page.replace("{{author_byline}}", author_byline)
    page = page.replace("{{author_bio}}", author_bio)
    page = page.replace("{{category}}", html.escape(meta["category"]))
    page = page.replace("{{reading_time}}", str(rt))
    page = page.replace("{{body}}", html_body)
    page = page.replace("{{references_block}}", refs_block)

    full_html = render_layout(
        page,
        title=f'{meta["title"]} | RAMA G7 Club',
        description=meta.get("description", meta["lede"]),
        og_type="article",
        active_nav="home",
    )

    slug = md_path.stem
    out_path = PUBLIC / "posts" / slug / "index.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(full_html, encoding="utf-8")

    return {
        "slug": slug,
        "title": meta["title"],
        "subtitle": meta.get("subtitle", ""),
        "lede": meta["lede"],
        "date": meta["date"],
        "date_label": format_date_label(meta["date"]),
        "author": meta["author"],
        "category": meta["category"],
        "tags": parse_tags(meta.get("tags", "")),
        "summary": meta.get("summary", meta["lede"]),
        "description": meta.get("description", meta["lede"]),
        "url": f"/posts/{slug}/",
        "body_html": html_body,
        "refs_block": refs_block,
    }


def build_index(posts):
    posts = sorted(posts, key=lambda p: p["date"], reverse=True)

    cards = []
    for i, p in enumerate(posts, 1):
        tag_html = "".join(
            f'<span class="tag {tag_class(t)}">{html.escape(t)}</span>'
            for t in p["tags"]
        )
        thumb_class = f"t{(i - 1) % 3}"
        
        img_match = re.search(r'<img\s+src="([^"]+)"', p["body_html"])
        if img_match:
            img_src = img_match.group(1)
            thumb_html = f'''
    <img src="{img_src}" alt="{html.escape(p["title"])}" style="width: 100%; height: 100%; object-fit: cover; display: block;">
    <div class="post-card-thumb-fade"></div>'''
        else:
            thumb_html = f'''
    <div class="post-card-thumb-grad {thumb_class}">
      <svg width="40" height="40" viewBox="0 0 44 44" fill="none" style="opacity:0.25">
        <rect x="8" y="4" width="28" height="36" rx="2" stroke="white" stroke-width="1.5"/>
        <circle cx="22" cy="22" r="9" stroke="white" stroke-width="1.5"/>
        <line x1="22" y1="4" x2="22" y2="40" stroke="white" stroke-width="0.75" stroke-dasharray="2 2"/>
      </svg>
    </div>
    <div class="post-card-thumb-fade"></div>'''

        cards.append(f'''
<a class="post-card" href="{p["url"]}?v={{{{build_time}}}}">
  <div class="post-card-content">
    <div class="post-card-toprow">
      <span class="post-card-num">{i:02d}</span>
      <span class="post-card-dot">·</span>
      <span class="post-card-meta">{html.escape(p["date_label"])}</span>
      <span class="post-card-dot">·</span>
      <span class="post-card-meta">{html.escape(p["category"])}</span>
      {tag_html}
    </div>
    <div class="post-card-title">{html.escape(p["title"])}</div>
    <div class="post-card-summary">{html.escape(p["summary"])}</div>
    <div class="post-card-author">{html.escape(p["author"])}, RAMA G7</div>
  </div>
  <div class="post-card-thumb">
    {thumb_html}
  </div>
</a>''')

    index_template = read_template("index.html")
    page = index_template.replace("{{post_cards}}", "\n".join(cards))

    full = render_layout(
        page,
        title="RAMA G7 Club | Editorial",
        description="Editorial writing on medical AI and innovation by medical students at Ramathibodi Hospital.",
        active_nav="home",
    )
    (PUBLIC / "index.html").write_text(full, encoding="utf-8")


def build_static_page(slug, title, content_html, description, nav_key):
    page = f'<div class="static-wrap"><div class="static-page fade-up">{content_html}</div></div>'
    full = render_layout(
        page, title=f"{title} | RAMA G7 Club",
        description=description, active_nav=nav_key,
    )
    out_dir = PUBLIC / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(full, encoding="utf-8")


def build_ig_generator(posts, members):
    template = read_template("ig_generator.html")
    # Convert lists to JSON to inject into script
    posts_json = json.dumps(posts, ensure_ascii=False)
    # For members we only need basic info
    members_min = [{"nickname": m.get("nickname"), "name": m.get("name"), "name_en": m.get("name_en"), "photo": m.get("photo"), "role": m.get("role")} for m in members]
    members_json = json.dumps(members_min, ensure_ascii=False)
    
    page = template.replace("{{posts_json}}", posts_json).replace("{{members_json}}", members_json)
    
    out_dir = PUBLIC / "tools" / "ig"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(page, encoding="utf-8")


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

    members = load_members()

    posts = []
    for md in sorted(CONTENT.glob("*.md")):
        if md.name.startswith("_"):
            continue
        try:
            posts.append(build_post(md, members))
            print(f"  built post  {md.name}")
        except Exception as e:
            print(f"  FAILED      {md.name}: {e}", file=sys.stderr)
            sys.exit(1)

    build_index(posts)
    print(f"  built index ({len(posts)} posts)")

    for m in members:
        build_member_page(m, posts)
    if members:
        print(f"  built profiles ({len(members)} members)")

    members_section = render_members_section(members)
    about_html = '''
<h1>RAMA G7</h1>
<p class="lede">ชมรมแพทย์นวัตกรรามาธิบดี</p>

<p>กลุ่มนักศึกษาแพทย์รามาฯ ที่สนใจการสร้าง ประเมิน และเขียนเรื่องเทคโนโลยีทางการแพทย์ เว็บไซต์นี้รวบรวมงานเขียนด้าน เทคโนโลยีสุขภาพ แบบเน้นข้อมูลเฉพาะเจาะจงและตัวเลขที่จับต้องได้</p>

<h2>งานของชมรม</h2>
<ul>
  <li><strong>บทความบนเว็บ.</strong> งานเขียนด้านเทคโนโลยีสุขภาพโดยสมาชิกชมรม</li>
  <li><strong>ข่าวสาร.</strong> สรุปประเด็นงานวิจัยด้านเทคโนโลยีสุขภาพ และเผยแพร่ผ่าน Instagram และ Facebook</li>
  <li><strong>พื้นที่สมาชิก.</strong> Workshop, Project Journal และ Member Spotlight</li>
</ul>

<h2>การแก้ไขข้อมูล</h2>
<p>หากพบจุดที่ผิดพลาด เราจะแก้ไขข้อมูลอย่างเปิดเผยเพื่อให้ทราบจุดที่ปรับปรุง</p>

<h2>Team &amp; Contact</h2>
<ul>
  <li><strong>President.</strong> บิ๊ก, ปรเมศวร์ วัฒนประสาน. <a href="mailto:porames.vat@student.mahidol.edu">porames.vat@student.mahidol.edu</a></li>
  <li><strong>Vice President / Editor.</strong> สมาร์ท, ประวีร์ สินวีรุทัย. <a href="mailto:prawee.sin@student.mahidol.edu">prawee.sin@student.mahidol.edu</a></li>
  <li><strong>Club Email.</strong> <a href="mailto:rama.g7.club@gmail.com">rama.g7.club@gmail.com</a></li>
</ul>
''' + members_section
    build_static_page("about", "About", about_html,
                      "About RAMA G7 Club at Ramathibodi Hospital, Mahidol University.",
                      "about")
    print("  built about")

    join_html = '''
<h1>Join Us</h1>
<p class="lede">เรามองหานักศึกษาแพทย์รามาฯ ที่สนใจอ่าน เขียน สร้าง หรือประเมินเทคโนโลยีไปด้วยกัน ไม่ต้องมีโปรไฟล์ แค่มีความอยากรู้อยากเห็นก็พอครับ</p>

<iframe src="https://docs.google.com/forms/d/e/1FAIpQLSdbymtuncNgKSiL3Rf2HMG5sdu5mdd2hibjqhF-H8-yMkIIiQ/viewform?embedded=true" width="100%" height="1000" frameborder="0" marginheight="0" marginwidth="0">Loading…</iframe>

<p>For any inquiries, contact us at IG, FB, or <a href="mailto:rama.g7.club@gmail.com">rama.g7.club@gmail.com</a></p>
'''
    build_static_page("join", "Join", join_html,
                      "Join RAMA G7 Club.",
                      "join")
    print("  built join")

    # 404
    notfound = '<div class="static-page"><h1>ไม่พบหน้านี้</h1><p>ลองกลับไปที่ <a href="/">หน้ารวมบทความ</a></p></div>'
    full404 = render_layout(notfound, "Not found | RAMA G7 Club",
                             "Page not found.", active_nav="")
    (PUBLIC / "404.html").write_text(full404, encoding="utf-8")

    build_ig_generator(posts, members)
    print("  built IG generator (secret)")

    print(f"\nbuild ok. output is in public/")


if __name__ == "__main__":
    main()
