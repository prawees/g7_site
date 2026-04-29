I am Smart, vice president of RAMA G7, ชมรมแพทย์นวัตกรรามา, the
medical innovation club at Ramathibodi Hospital, Mahidol
University. President is Big, neurosurgery and robotics interest.
I am 5th to 6th year medical student, PM&R interested.

You are working in the repository for our editorial website
g7club.org. Read the README.md before doing anything else,
it is the operating manual for this codebase.

ARCHITECTURE 
The site is a static site. Markdown files in content/posts/ are
built by scripts/build.py into HTML in public/, deployed to
Hostinger via FTP through GitHub Actions on push to main. No
frameworks, no npm, just Python standard library. We use
clean URLs (generating `index.html` inside folders). The build
script also generates a secret IG Carousel generator at `/tools/ig/`
using client-side JS (`html2canvas`). The whole build script is 
around 700 lines and you should read it before making changes.

THREE CONTENT STREAMS
1. Auto-curated medical AI news, Facebook only, daily, low signal
2. Editorial pieces, IG and FB and the website, 1 to 2 a week,
   default author Smart 
3. Member content like workshops and project journals, 2 to 4
   a month, on the website

Only streams 2 and 3 live on the website. Stream 1 is FB only.

EDITORIAL VOICE RULES, STRICTLY ENFORCED
- No colons in body text, restructure the sentence
- No em-dashes or long hyphens, use commas or periods
- One emoji maximum, never at the start
- Vancouver citations inline as [1] or [1,2], references at
  the end of the post under a "## References" heading
- Always state at least one limitation per piece
- Banned hype words include ก้าวสำคัญ, breakthrough, revolutionize,
  น่าทึ่ง, เปลี่ยนวงการ, ปฏิวัติ, อนาคตของการแพทย์
- Default author is Smart unless explicitly assigned otherwise
- Code-switch English jargon naturally, do not awkwardly
  translate things like deep learning or ROC-AUC
- Specificity over hype, use numbers when available

BRAND
Colors as CSS variables in static/css/style.css
  --ink         #030F27  navy, primary dark surface
  --paper       #F4EFE6  warm cream, primary light surface
  --accent      #14B59D  logo teal, decorative use only
  --accent-deep #0E8A78  legible teal for text on cream

Typography
  Display, Source Serif 4 plus Noto Serif Thai
  Body, Source Serif 4 plus Sarabun
  UI, IBM Plex Sans plus Sarabun

This pairing matches my Ongsa AI project for cross-brand
consistency.

WRITING A NEW POST
Create content/posts/YYYY-MM-DD-slug.md with front matter

  ---
  title: Sentence-case title without a colon
  subtitle: Optional flavor heading or subtitle
  lede: One or two sentences, what the piece is about
  date: 2026-04-29
  author: Smart
  category: Paper Notes
  tags: AI, รังสีวิทยา
  description: Optional, used for SEO if provided
  ---

Then body in Markdown (supports headers, lists, quotes, inline 
formatting, and images `![alt](/static/img/...png)`). Then ## References 
at the end with numbered Vancouver entries. Build script handles inline 
citation linking.

DEPLOY
Push to main, GitHub Actions builds and deploys via FTP to
Hostinger in about 60 to 90 seconds. Four secrets are configured,
FTP_HOST, FTP_USER, FTP_PASSWORD, FTP_SERVER_DIR. Do not commit
the public/ directory, it is gitignored and rebuilt on every
deploy.

WHAT I MAY ASK YOU TO DO
Common requests
- Write a new editorial piece on topic X, in the voice
- Translate or rewrite an English draft into the editorial
  Thai voice
- Add a new page to the site like /projects or /workshops
- Tweak the CSS to fix a layout issue
- Add a new content category
- Build a new feature into scripts/build.py
- Enhance or debug the IG Carousel Generator in `templates/ig_generator.html`

WHAT NOT TO DO
- Do not introduce npm, Node, or any JS framework, the site is
  intentionally dependency-free
- Do not auto-publish content, all editorial pieces require
  human review before they get committed
- Do not break the no-colons no-em-dashes voice rules in any
  prose meant for publication, even if I forget to ask
- Do not change brand colors or fonts without checking with me
  first, they are intentional
- Do not commit anything that contains hype words from the
  banned list

Read README.md, then tell me what you understand the project to
be and what you would do for the task I am about to give you.