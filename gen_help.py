#!/usr/bin/env python3
"""Emit help.html from the app's HELP.md.

HELP.md in the StopMotion repo is the one copy of the help; this turns it into
the site's help page. Run from the repo root whenever HELP.md changes:

    python3 gen_help.py [path/to/HELP.md]     # default ../StopMotion/HELP.md

The site header (brand + menu bar) is defined here in NAV and stamped into the
page; index.html and privacy.html carry a hand-pasted copy, so update those
when NAV changes.

Only the Markdown HELP.md uses is understood: # and ## headings, paragraphs,
- and 1. lists nested by indentation, pipe tables, **bold**, `code` and
[links](url).
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / "StopMotion" / "HELP.md"
OUT = ROOT / "help.html"

NAV = [("index.html", "Support"), ("help.html", "Help"), ("privacy.html", "Privacy")]

ITEM = re.compile(r"^( *)([-*]|\d+\.) +(.*)$")
TABLE_RULE = re.compile(r"^\|[\s:|-]+\|$")


def site_header(current):
    links = "\n".join(
        f'    <a href="{href}"{" aria-current=\"page\"" if href == current else ""}>{html.escape(label)}</a>'
        for href, label in NAV)
    return f"""<header class="site">
  <a class="brand" href="index.html"><img class="mark" src="icon.png" alt="" width="32" height="32">Stutter Shot Studio</a>
  <nav>
{links}
  </nav>
  <script>document.querySelector('.site nav [aria-current]').scrollIntoView({{inline: "center", block: "nearest"}})</script>
</header>"""


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', text)


def indent(line):
    return len(line) - len(line.lstrip(" "))


def is_table(line):
    return line.lstrip().startswith("|")


def skip_blank(lines, i):
    while i < len(lines) and not lines[i].strip():
        i += 1
    return i


def parse(lines, i, min_indent):
    """Blocks from lines[i] on, while they're indented at least min_indent.
    Returns (html, index of the first line not used)."""
    out = []
    while True:
        i = skip_blank(lines, i)
        if i >= len(lines) or indent(lines[i]) < min_indent:
            return "\n".join(out), i
        if ITEM.match(lines[i]):
            block, i = parse_list(lines, i)
        elif is_table(lines[i]):
            block, i = parse_table(lines, i)
        else:
            para = []
            while (i < len(lines) and lines[i].strip() and indent(lines[i]) >= min_indent
                   and not ITEM.match(lines[i]) and not is_table(lines[i])):
                para.append(lines[i].strip())
                i += 1
            block = f"<p>{inline(' '.join(para))}</p>"
        out.append(block)


def parse_list(lines, i):
    first = ITEM.match(lines[i])
    base, ordered = len(first[1]), first[2][-1] == "."
    items = []
    while True:
        m = ITEM.match(lines[i]) if i < len(lines) else None
        if not m or len(m[1]) != base or (m[2][-1] == ".") != ordered:
            break
        text = [m[3]]
        i += 1
        # Lines that carry on the item's first paragraph.
        while (i < len(lines) and lines[i].strip() and indent(lines[i]) > base
               and not ITEM.match(lines[i]) and not is_table(lines[i])):
            text.append(lines[i].strip())
            i += 1
        # Anything indented under the item: nested lists, later paragraphs.
        rest, i = parse(lines, i, base + 1)
        items.append(f"<li>{inline(' '.join(text))}{rest}</li>")
        j = skip_blank(lines, i)
        if j < len(lines) and ITEM.match(lines[j]) and indent(lines[j]) == base:
            i = j
    tag = "ol" if ordered else "ul"
    return f"<{tag}>\n" + "\n".join(items) + f"\n</{tag}>", i


def parse_table(lines, i):
    rows = []
    while i < len(lines) and is_table(lines[i]):
        line = lines[i].strip()
        if not TABLE_RULE.match(line):
            rows.append([c.strip() for c in line.strip("|").split("|")])
        i += 1
    head, body = rows[0], rows[1:]
    th = "".join(f"<th>{inline(c)}</th>" for c in head)
    trs = "\n".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
    return f"<table>\n<thead><tr>{th}</tr></thead>\n<tbody>\n{trs}\n</tbody>\n</table>", i


def slug(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def main():
    lines = SOURCE.read_text().splitlines()
    # Split into the intro (before the first ##) and the sections.
    sections, intro = [], []
    for line in lines:
        if line.startswith("## "):
            sections.append((line[3:].strip(), []))
        elif line.startswith("# "):
            continue
        elif sections:
            sections[-1][1].append(line)
        else:
            intro.append(line)

    lede = " ".join(l.strip() for l in intro if l.strip())
    toc = "\n".join(f'  <li><a href="#{slug(t)}">{inline(t)}</a></li>' for t, _ in sections)
    body = "\n\n".join(
        f'<h2 id="{slug(t)}">{inline(t)}</h2>\n{parse(ls, 0, 0)[0]}' for t, ls in sections)

    OUT.write_text(f"""<!DOCTYPE html>
<!-- Generated by gen_help.py from the app's HELP.md. Edit HELP.md, not this file. -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Stutter Shot Studio — Help</title>
<meta name="description" content="How to use Stutter Shot Studio, a stop-motion animation studio for iPhone, iPad and Mac.">
<link rel="icon" href="icon.png">
<link rel="stylesheet" href="style.css">
</head>
<body>
<main class="help">

{site_header("help.html")}

<div class="title">
  <div class="mark" aria-hidden="true">🎬</div>
  <div>
    <h1>Help</h1>
    <p>How to use Stutter Shot Studio</p>
  </div>
</div>

<p class="lede">{inline(lede)}</p>

<nav class="toc" aria-label="On this page">
<ol>
{toc}
</ol>
</nav>

{body}

<hr>
<footer>© 2026 Rafeek Rahamut</footer>

</main>
</body>
</html>
""")
    print(f"wrote {OUT.name}: {len(sections)} sections from {SOURCE}")


if __name__ == "__main__":
    main()
