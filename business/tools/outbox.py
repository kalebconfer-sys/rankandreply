"""Turns a day's outbox folder into one page: what to post or send, where, and a copy button.

Every tool writes plain .txt files into business/data/outbox/<date>/. This builds
business/data/outbox/<date>/today.html from them, so the daily routine is: open one
page, click the link, copy the draft, paste, edit, post.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

MARKER = re.compile(r"^-{3,}\s*(.+?)\s*-{3,}\s*$")


def parse(path: Path) -> dict:
    """Header lines ('KEY: value') until the first blank line, then sections split by '----- name -----'."""
    text = path.read_text(encoding="utf-8")
    head, _, rest = text.partition("\n\n")
    headers = {}
    for line in head.splitlines():
        k, sep, v = line.partition(":")
        if sep and k.strip().isupper():
            headers[k.strip()] = v.strip()
        else:  # not a header block after all
            rest = text
            headers = {}
            break
    sections, current, buf = {}, "main", []
    for line in rest.splitlines():
        m = MARKER.match(line)
        if m:
            sections[current] = "\n".join(buf).strip()
            current, buf = m.group(1).lower(), []
        else:
            buf.append(line)
    sections[current] = "\n".join(buf).strip()
    draft = sections.get("draft") or sections.get("main", "")
    theirs = next((v for k, v in sections.items() if k.startswith("their")), "")
    return {"file": path.name, "headers": headers, "draft": draft, "theirs": theirs}


def kind_of(item: dict) -> str:
    name = item["file"]
    if name.startswith("posts-"):
        return "Your own posts"
    if name.startswith("scout-"):
        return "Replies and proposals"
    return "Email replies"


def write_digest(folder: Path) -> Path | None:
    files = sorted(p for p in folder.glob("*.txt"))
    if not files:
        return None
    items = [parse(p) for p in files]
    groups: dict[str, list[dict]] = {}
    for it in items:
        groups.setdefault(kind_of(it), []).append(it)
    e = html.escape
    cards = []
    n = 0
    for group in ("Email replies", "Replies and proposals", "Your own posts"):
        if group not in groups:
            continue
        cards.append(f"<h2>{e(group)} <span class='count'>{len(groups[group])}</span></h2>")
        for it in groups[group]:
            n += 1
            h = it["headers"]
            where = h.get("WHERE") or h.get("TO") or h.get("FOR") or it["file"]
            url = h.get("URL", "")
            link = (f"<a class='btn' href='{e(url)}' target='_blank' rel='noopener'>Open</a>"
                    if url.startswith("https://") else "")
            meta = " · ".join(e(f"{k.title()}: {v}") for k, v in h.items()
                              if k in ("TITLE", "SCORE", "LABEL", "ATTACH", "WHEN") and v and v != "-")
            how = f"<p class='how'>{e(h['HOW'])}</p>" if h.get("HOW") else ""
            theirs = (f"<details><summary>Their post</summary><pre>{e(it['theirs'])}</pre></details>"
                      if it["theirs"] else "")
            cards.append(f"""<section class="card">
<div class="top"><strong>{e(where)}</strong>{link}<label class="done"><input type="checkbox"> done</label></div>
<p class="meta">{meta}</p>{how}{theirs}
<textarea id="d{n}" rows="{min(18, max(5, it['draft'].count(chr(10)) + 3))}">{e(it['draft'])}</textarea>
<button class="btn copy" data-target="d{n}">Copy</button>
</section>""")
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Today: {e(folder.name)}</title>
<style>
:root{{--ink:#14181d;--body:#4a5562;--muted:#8a949f;--line:#e4e0d9;--bg:#fff;--card:#f7f5f1;--accent:#e2670a}}
@media (prefers-color-scheme: dark){{:root{{--ink:#f1efe9;--body:#c9cdd2;--muted:#8a949f;--line:#3a3f46;--bg:#15181c;--card:#1e2227}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--body);font:16px/1.55 system-ui,-apple-system,'Segoe UI',sans-serif}}
.wrap{{max-width:860px;margin:0 auto;padding:28px 16px 60px}}h1,h2{{color:var(--ink)}}h1{{font-size:1.6rem;margin:0 0 4px}}
h2{{font-size:1.1rem;margin:28px 0 10px}}.count{{color:var(--muted);font-weight:400}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;margin:12px 0}}
.top{{display:flex;gap:10px;align-items:center;flex-wrap:wrap}}.top strong{{color:var(--ink);flex:1;min-width:0;overflow-wrap:anywhere}}
.meta,.how{{font-size:.88rem;margin:6px 0;overflow-wrap:anywhere}}.how{{color:var(--ink)}}
textarea{{width:100%;font:inherit;font-size:.95rem;padding:10px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--ink);resize:vertical}}
pre{{white-space:pre-wrap;font:inherit;font-size:.9rem;margin:6px 0}}details{{margin:6px 0}}
.btn{{display:inline-block;background:var(--accent);color:#fff;border:0;border-radius:8px;padding:7px 14px;font-weight:600;text-decoration:none;cursor:pointer;font-size:.9rem}}
.copy{{margin-top:8px}}.done{{font-size:.85rem;color:var(--muted)}}.card.is-done{{opacity:.45}}
</style></head><body><div class="wrap">
<h1>Today: {e(folder.name)}</h1>
<p>Open each link, read the whole post, copy the draft, <strong>rewrite it in your own words</strong>, and post it yourself. Nothing on this page posts anything.</p>
{''.join(cards)}
</div>
<script>
document.querySelectorAll('.copy').forEach(b => b.addEventListener('click', async () => {{
  const t = document.getElementById(b.dataset.target);
  try {{ await navigator.clipboard.writeText(t.value); }}
  catch (_) {{ t.select(); document.execCommand('copy'); }}
  b.textContent = 'Copied'; setTimeout(() => b.textContent = 'Copy', 1500);
}}));
document.querySelectorAll('.done input').forEach(c => c.addEventListener('change', () =>
  c.closest('.card').classList.toggle('is-done', c.checked)));
</script></body></html>"""
    out = folder / "today.html"
    out.write_text(page, encoding="utf-8")
    return out
