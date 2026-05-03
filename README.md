# g7club.org

The RAMA G7 Club editorial site. A static site generated from Markdown, deployed to Hostinger.

This README is the operating manual. If something looks confusing, open this file first.

## What this is, and is not

This site holds **Stream 2 (editorial pieces)** and **Stream 3 (member content)** from the RAMA G7 master plan. Stream 1 (auto-curated news) does not appear here. That stream lives on Facebook only.

The reasoning is that auto-curated news has no archive value. Editorial pieces do.

## Repository layout

```
g7_site/
  content/
    posts/
      YYYY-MM-DD-slug.md     One Markdown file per editorial piece
  templates/
    base.html                Outer page layout, masthead, footer
    index.html               Editorial index fragment
    post.html                Article page fragment
  static/
    css/style.css            All site styling
    img/logo.png             Club logo, used in masthead
    img/favicon.png
  scripts/
    build.py                 Static site builder
  public/                    Generated. Do not commit. .gitignored.
  .github/workflows/
    deploy.yml               Auto-deploy to Hostinger on push to main
  .gitignore
  README.md                  This file
```

## Local development

Requires Python 3.10 or newer. No other dependencies.

```
git clone https://github.com/<your-handle>/rama-g7-site.git
cd rama-g7-site
python3 scripts/build.py
cd public && python3 -m http.server 8000
```

Then open http://localhost:8000 in a browser.

Every change to a Markdown file or template requires a rebuild. There is no hot reload by design. The build is fast enough that this is fine.

## Writing a new post

1. Create a file in `content/posts/` named `YYYY-MM-DD-slug.md`. The date in the filename is just for ordering, the date in front matter is what shows on the page.
2. Add front matter at the top, fenced by `---`.
3. Write the body in Markdown.
4. Add a `## References` section at the end if the piece has citations.
5. Use `[1]`, `[2]`, or combined like `[1,2]` inline. The build script turns these into superscript links.

### Front matter template

```
---
title: The post title goes here, sentence case usually
lede: One or two sentences. This appears under the title and on the index card.
date: 2026-04-29
author: Smart
category: Editorial
description: Used for SEO and social previews. If omitted, the lede is used.
---
```

The five required keys are `title`, `lede`, `date`, `author`, `category`. The build will fail with a clear error if any are missing.

### Vancouver citations, the way this site does them

In the body, write inline citations as bracketed numbers.

```
The model performs below specialized CXR models on findings that
matter clinically [1,2].
```

At the end of the post, add a References section. Each entry must start with a number, a period, then the reference.

```
## References

1. Liu Y, Wang H, Zhao K. Multimodal large language models for medical image interpretation. NEJM AI. 2024;1(8).
2. Brodsky V, Ullman A, Kim J. Evaluating GPT-4V on chest radiograph interpretation. Radiology. 2024;312(1).
```

The build script does the rest. Inline `[1]` becomes a superscript link to `#ref-1`. The references block is rendered with a heavy top rule and Vancouver styling.

### Style rules, enforced by editorial discipline not by the script

- No colons in body text.
- No em-dashes or long hyphens.
- One emoji maximum, never at the start.
- Banned hype words. See the editorial style guide for the list.
- Always state at least one limitation per piece.
- Default author is Smart. Other authors should be named explicitly in front matter.

The build script does not enforce these. The author and editor do.

## Categories

We use a small fixed set of categories to keep the index scannable.

- `Paper Notes`. A short piece about a single paper or finding.
- `Commentary`. A meta or critical piece about how the field talks about itself.
- `Tool Evaluation`. Hands-on test of a medical AI product.
- `Build Log`. Project journal pieces.
- `Member Spotlight`. Profile of a club member or alum.

Add a new category only when there is a real reason to. More categories means more cognitive load for the reader.

## Deployment to g7club.org via Hostinger

Two pieces. First the one-time setup. Then the per-push flow.


```
cd /path/to/g7_site
git init
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin git@github.com:<your-handle>/rama-g7-site.git
git push -u origin main
```

First deploy

Push to main, or trigger the workflow manually from the **Actions** tab. The first run takes about a minute. If it succeeds, visit https://g7club.org to confirm.

If it fails, check the action logs. The most common failures are listed in the troubleshooting section below.

#### 6. Enable HTTPS

In Hostinger control panel, go to the subdomain SSL settings and enable the free Let's Encrypt SSL for `g7club.org`. This is a one-click toggle on most plans. Wait a few minutes for issuance.

### Per-push flow

After the one-time setup, the entire workflow is

1. Write a new post in `content/posts/`.
2. Test locally with `python3 scripts/build.py` and the local HTTP server.
3. `git add . && git commit -m "post, gpt4 chest xray" && git push`.
4. GitHub Actions builds and deploys. Live within 60 to 90 seconds.

That is it. There is no CMS, no admin panel, no database to back up. The Markdown files in git are the canonical source.

## Integrating with the n8n editorial workflow

The auto-curation n8n workflow writes post candidates to a Google Sheet queue. When you, as editor, decide a candidate deserves to live on the site rather than just on Facebook, the flow is

1. Open the Google Sheet, find the row.
2. Copy the post text into a new Markdown file in `content/posts/`.
3. Rewrite it in your own voice using the editorial style guide. The auto-generated text is a starting draft, never a final post.
4. Add Vancouver references manually. The auto-curated drafts do not produce these properly.
5. Commit and push.

This is intentionally a manual bridge. Auto-published content tends to be lower quality than human-edited content, and the website is the long-lived record of what RAMA G7 thinks. A clean separation protects the archive from drift.

If after six months of editing this turns out to be too slow, we can write a small n8n node that drops a Markdown stub into the repository via the GitHub API. We are not building that yet. The bottleneck is editorial time, not file creation.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Build fails with "missing front matter key" | One of title, lede, date, author, category is missing | Add it. The error message names the missing key. |
| Inline `[1]` not turned into a link | Either no References section, or the number is out of range | Add a `## References` section, ensure the number maps to a real ref. |
| FTP deploy fails with auth error | Wrong credentials or IP block | Double check the secrets. Hostinger sometimes blocks new IPs, in which case enable FTP from anywhere in the FTP account settings. |
| Site loads but CSS is missing | Wrong server-dir, files landed in the wrong folder | Confirm `FTP_SERVER_DIR` ends in `/` and points to the subdomain root. |
| New post not showing | Browser cache, or build did not pick up the file | Hard reload, or rebuild and redeploy. |
| Thai characters render as boxes | Browser font fallback issue | The site loads Noto Serif Thai and Sarabun from Google Fonts. If the network blocks Google Fonts, fall back to system Thai fonts. |

## Performance

The site is intentionally tiny. A typical article page is about 30 KB of HTML, 7 KB of CSS, plus Google Fonts. Total page weight is around 100 KB excluding fonts. There is no JavaScript on the public site.

If page weight grows above 500 KB, something has gone wrong. Audit recent commits.

## Accessibility notes

- Color contrast of body text on cream background is checked at WCAG AA.
- All images need alt text. The current logo has empty alt because it is decorative next to the wordmark.
- Reduced motion is respected via the `prefers-reduced-motion` media query.

## License and editorial responsibility

All editorial content is the work of named authors. Authors retain credit. The club retains the right to edit for clarity and accuracy after publication. Substantial edits should be noted at the bottom of the affected post with a date and a one-line description of the change.

Inaccurate posts get corrected, not deleted. A correction note at the bottom is the standard.

## Maintenance schedule

- **Monthly.** Skim the site for broken links and typos.
- **Quarterly.** Audit the editorial style guide against what the lived voice has become. Update the guide.
- **Annually.** Review the categories. Drop ones that have not been used. Consider adding ones that should be.

## Contact

Editorial questions and bug reports go to rama.g7.club@gmail.com.
