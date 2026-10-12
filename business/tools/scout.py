#!/usr/bin/env python3
"""Scout: finds people asking for what we sell on Reddit and Upwork, and drafts
the reply or proposal. You post it yourself.

    python scout.py run                 # everything below, then drafts into the outbox
    python scout.py inbox [--days 2]    # read Upwork + F5Bot alert emails (read-only)
    python scout.py reddit [--recency week]   # search reddit.com via Perplexity or Claude
    python scout.py inbox --eml-dir ../data/scout/eml   # parse saved .eml files instead of IMAP
    python scout.py posts               # a week of posts for your own LinkedIn profile, to schedule once

Every run also writes business/data/outbox/<date>/today.html: one page with every
draft, a link to where it goes, and a copy button.

Why it works this way (details in business/04-outreach/reddit.md):
- Reddit requires approval for API access (since Nov 2025) and its RSS feeds are
  reported to end on Nov 13, 2026. So we never call Reddit directly. We read
  F5Bot's free keyword-alert emails and search reddit.com through Perplexity
  (or Claude web search).
- Upwork removed its RSS feeds in 2024. Its saved-search email alerts are the
  official way to hear about new jobs, so we read those emails.
- Nothing here posts anything. Reddit treats automated promotional posting as
  spam and Upwork bans bots that submit proposals. You post every reply and
  submit every proposal by hand, from your own account.

Email access is read-only: the inbox is opened with readonly=True, only messages
from the alert senders are fetched, nothing is marked read, moved or deleted.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import statistics
from collections import Counter
import email
import email.policy
import imaplib
import json
import os
import re
import sys
from datetime import date, timedelta
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

import council as C
from outbox import write_digest

DATA = C.HERE.parent / "data"
TODAY = date.today().isoformat()
PROMPTS = C.HERE / "prompts"
QUERIES = C.HERE / "scout_queries.txt"

REDDIT_THREAD = re.compile(r"https?://(?:www\.|old\.|new\.)?reddit\.com/r/([A-Za-z0-9_]+)/comments/([a-z0-9]+)[^\s\"'<>)]*", re.I)
UPWORK_JOB = re.compile(r"https?://(?:www\.)?upwork\.com/(?:jobs/|freelance-jobs/apply/)[^\s\"'<>)]*~0[0-9a-z]+[^\s\"'<>)]*", re.I)
# Every community link the alert emails can carry: kind, pattern, canonical URL, where it is.
SITES = [
    ("reddit", REDDIT_THREAD,
     lambda m: f"https://www.reddit.com/r/{m.group(1)}/comments/{m.group(2)}/", lambda m: f"r/{m.group(1)}"),
    ("upwork", UPWORK_JOB,
     lambda m: "https://www.upwork.com/jobs/" + re.search(r"~0[0-9a-z]+", m.group(0), re.I).group(0), lambda m: "Upwork"),
    ("hn", re.compile(r"https?://news\.ycombinator\.com/item\?id=(\d+)", re.I),
     lambda m: f"https://news.ycombinator.com/item?id={m.group(1)}", lambda m: "Hacker News"),
    ("x", re.compile(r"https?://(?:www\.|mobile\.)?(?:x|twitter)\.com/([A-Za-z0-9_]{1,15})/status/(\d+)", re.I),
     lambda m: f"https://x.com/{m.group(1)}/status/{m.group(2)}", lambda m: "X"),
    ("bluesky", re.compile(r"https?://bsky\.app/profile/([^/\s\"'<>]+)/post/([a-z0-9]+)", re.I),
     lambda m: f"https://bsky.app/profile/{m.group(1)}/post/{m.group(2)}", lambda m: "Bluesky"),
    ("stackexchange", re.compile(r"https?://((?:[a-z]+\.)?(?:stackexchange|stackoverflow|serverfault|superuser)\.com)/questions/(\d+)", re.I),
     lambda m: f"https://{m.group(1)}/questions/{m.group(2)}", lambda m: m.group(1)),
    ("indiehackers", re.compile(r"https?://(?:www\.)?indiehackers\.com/post/([A-Za-z0-9_-]+)", re.I),
     lambda m: f"https://www.indiehackers.com/post/{m.group(1)}", lambda m: "Indie Hackers"),
]

HOW = {
    "upwork": "Open the job, check it's fixed-price and still open, edit, and submit by hand.",
    "stackexchange": "Many Stack Exchange sites ban AI-written answers. Use the draft as notes only and write your own answer.",
    "x": "Reply yourself from your own account (X blocks automated replies). Keep it short; rewrite it in your own words.",
}
HOW_DEFAULT = "Post it yourself from your own account after reading the community's rules. Rewrite it in your own words first."


def classify(url: str) -> tuple[str, str, str] | None:
    """(kind, canonical url, where) for a link we know how to handle, else None."""
    for kind, pat, canon, where in SITES:
        m = pat.search(url or "")
        if m:
            return kind, canon(m), where(m)
    return None


GENERIC_ANCHOR = re.compile(r"^(view|see|open|apply|read|click|unsubscribe|manage|here|more|job details|view job|reply|settings)\b", re.I)


# --------------------------------------------------------------------------- email parsing

class _Links(HTMLParser):
    """Collects (href, anchor text, text that follows the link) from an HTML email."""

    def __init__(self):
        super().__init__()
        self.items: list[dict] = []
        self._href, self._anchor, self._skip = None, [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script"):
            self._skip += 1
        if tag == "a":
            self._href = dict(attrs).get("href") or ""
            self._anchor = []

    def handle_endtag(self, tag):
        if tag in ("style", "script") and self._skip:
            self._skip -= 1
        if tag == "a" and self._href is not None:
            self.items.append({"href": self._href, "anchor": " ".join(" ".join(self._anchor).split()), "after": []})
            self._href = None

    def handle_data(self, data):
        if self._skip:
            return
        if self._href is not None:
            self._anchor.append(data)
        elif self.items:
            self.items[-1]["after"].append(data)


def unwrap(url: str) -> str:
    """Tracking links often carry the real URL in a query parameter; dig it out."""
    url = unquote(url or "")
    for _, pat, _, _ in SITES:
        m = pat.search(url)
        if m:
            return m.group(0)
    try:
        for values in parse_qs(urlsplit(url).query).values():
            for v in values:
                inner = unwrap(v) if v != url else ""
                if inner and classify(inner):
                    return inner
    except ValueError:
        pass
    return url


def canonical(url: str) -> str:
    """One key per thread or job, whatever tracking parameters the link carried."""
    c = classify(url)
    return c[1] if c else url.split("?")[0]


def items_from_message(msg: email.message.Message) -> list[dict]:
    """Every community thread or Upwork job linked in one alert email (Upwork, F5Bot, Syften)."""
    sender = (msg.get("From") or "").lower()
    found: dict[str, dict] = {}
    html_part = msg.get_body(preferencelist=("html",)) if hasattr(msg, "get_body") else None
    text_part = msg.get_body(preferencelist=("plain",)) if hasattr(msg, "get_body") else None

    if html_part is not None:
        p = _Links()
        try:
            p.feed(html_part.get_content())
        except (LookupError, UnicodeError):  # unknown charset: fall back to the plain-text part
            p.items = []
        for it in p.items:
            c = classify(unwrap(it["href"]))
            if not c:
                continue
            kind, key, where = c
            after = " ".join(" ".join(it["after"]).split())[:600]
            title = it["anchor"] if it["anchor"] and not GENERIC_ANCHOR.match(it["anchor"]) and len(it["anchor"]) > 8 else ""
            prev = found.get(key)
            if prev:  # the same job is often linked twice (title and a "view job" button)
                prev["title"] = prev["title"] or title
                prev["snippet"] = prev["snippet"] or after
                continue
            found[key] = {"kind": kind, "url": key, "where": where, "title": title, "snippet": after}

    if text_part is not None:
        try:
            lines = [l.strip() for l in text_part.get_content().splitlines()]
        except (LookupError, UnicodeError):
            lines = []
        for i, line in enumerate(lines):
            for m in re.finditer(r"https?://\S+", line):
                c = classify(unwrap(m.group(0)))
                if not c:
                    continue
                kind, key, where = c
                if key in found:
                    continue
                before = next((l for l in reversed(lines[max(0, i - 3):i]) if l and not l.startswith("http")), "")
                after = " ".join(l for l in lines[i + 1:i + 4] if l and not l.startswith("http"))[:600]
                found[key] = {"kind": kind, "url": key, "where": where, "title": before[:200], "snippet": after}

    for it in found.values():
        it["source"] = next((name for name in ("f5bot", "syften", "upwork") if name in sender), sender or "email")
        if it["kind"] == "reddit":
            it["subreddit"] = REDDIT_THREAD.search(it["url"]).group(1)
    return list(found.values())


def read_imap(days: int) -> list[email.message.Message]:
    host = os.getenv("IMAP_HOST", "imap.gmail.com")
    user, password = os.getenv("IMAP_USER"), os.getenv("IMAP_PASSWORD")
    if not (user and password):
        raise C.Unavailable("IMAP_USER / IMAP_PASSWORD not set in .env (use a Gmail app password)")
    senders = [s.strip() for s in os.getenv("ALERT_SENDERS", "upwork.com,f5bot.com,syften.com").split(",") if s.strip()]
    since = (date.today() - timedelta(days=days)).strftime("%d-%b-%Y")
    msgs = []
    with imaplib.IMAP4_SSL(host) as box:
        box.login(user, password)
        box.select(os.getenv("IMAP_FOLDER", "INBOX"), readonly=True)  # read-only: nothing is marked or moved
        nums: list[bytes] = []
        for s in senders:
            status, data = box.search(None, "FROM", f'"{s}"', "SINCE", since)
            if status == "OK":
                nums += [n for n in data[0].split() if n not in nums]  # one fetch per email, even if two filters match
        for num in nums:
            status, parts = box.fetch(num, "(BODY.PEEK[])")  # PEEK: don't mark as read
            for part in parts:
                if isinstance(part, tuple):
                    msgs.append(email.message_from_bytes(part[1], policy=email.policy.default))
    return msgs


def read_eml_dir(folder: str) -> list[email.message.Message]:
    return [email.message_from_bytes(p.read_bytes(), policy=email.policy.default)
            for p in sorted(Path(folder).glob("*.eml"))]


# --------------------------------------------------------------------------- reddit search

THREADS_SCHEMA = {
    "type": "object",
    "properties": {"threads": {"type": "array", "items": {
        "type": "object",
        "properties": {"url": {"type": "string"}, "title": {"type": "string"}, "why": {"type": "string"}},
        "required": ["url", "title", "why"], "additionalProperties": False}}},
    "required": ["threads"],
    "additionalProperties": False,
}


def search_reddit(query: str, recency: str) -> list[dict]:
    """Recent reddit.com threads for one query, via Perplexity (domain-filtered) or Claude web search."""
    ask = (f"Find Reddit threads from the past {recency} where someone is asking about this, or clearly has this "
           f"problem: {query}\nReturn JSON {{\"threads\": [{{\"url\", \"title\", \"why\"}}]}} with up to 8 threads. "
           "Only real reddit.com thread URLs you found in search results. 'why' is one sentence on what they need.")
    urls_seen: list[dict] = []
    if os.getenv("PERPLEXITY_API_KEY"):
        text, resp = C._openai_compatible(*C.ENDPOINTS["perplexity"], ask, "",
                                          extra_body={"search_domain_filter": ["reddit.com"],
                                                      "search_recency_filter": recency})
        extra = getattr(resp, "model_extra", None) or {}
        for r in extra.get("search_results") or []:
            urls_seen.append({"url": r.get("url", ""), "title": r.get("title", ""), "why": r.get("snippet", "") or ""})
        for u in extra.get("citations") or []:
            urls_seen.append({"url": u, "title": "", "why": ""})
    elif os.getenv("ANTHROPIC_API_KEY"):
        found: list[str] = []
        text = C.call_claude(ask, web=True, effort="low", sources=found, web_domains=["reddit.com"])
        urls_seen += [{"url": u, "title": "", "why": ""} for u in found]
    else:
        raise C.Unavailable("Reddit search needs PERPLEXITY_API_KEY or ANTHROPIC_API_KEY")

    data = C.parse_json(text)
    listed = data.get("threads", []) if isinstance(data, dict) else []
    # Only keep URLs that the search itself returned: the model can't add a thread that doesn't exist.
    real = {canonical(t["url"]) for t in urls_seen if REDDIT_THREAD.search(t.get("url", ""))}
    out: dict[str, dict] = {}
    for t in [*listed, *urls_seen]:
        if not isinstance(t, dict) or not REDDIT_THREAD.search(t.get("url", "")):
            continue
        key = canonical(t["url"])
        if key not in real:
            continue
        cur = out.setdefault(key, {"kind": "reddit", "url": key, "title": "", "snippet": "", "source": "search",
                                   "subreddit": REDDIT_THREAD.search(key).group(1),
                                   "where": f"r/{REDDIT_THREAD.search(key).group(1)}", "query": query})
        cur["title"] = cur["title"] or (t.get("title") or "")[:200]
        cur["snippet"] = cur["snippet"] or (t.get("why") or "")[:600]
    return list(out.values())


# --------------------------------------------------------------------------- scoring and drafting

SCORE_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {"type": "string"},
        "fit": {"type": "string"},
        "reason": {"type": "string"},
    },
    "required": ["intent", "fit", "reason"],
    "additionalProperties": False,
}


def score(item: dict, model: str) -> dict:
    data = C.call_json(model, (
        "We sell 'AI Visibility': we measure whether ChatGPT, Gemini, Perplexity and Claude recommend a B2B company "
        "when its buyers ask, and do the work to improve it (pages, listings, structured data), for $490 once or "
        "$1,500/month.\n\n"
        f"Source: {item.get('where') or item['kind']} (via {item.get('source', '')})\nTitle: {item.get('title', '')}\n"
        f"Text: {item.get('snippet', '')}\n\n"
        "Classify:\n- intent: 'buyer' (a business that has this problem or wants this done), 'peer' (a marketer or "
        "freelancer discussing the topic), or 'irrelevant'\n- fit: 'high', 'medium' or 'low' for us specifically\n"
        "- reason: one short sentence"
    ), SCORE_SCHEMA)
    if not data:
        return {"intent": "unknown", "fit": "unknown", "reason": "couldn't score; read it yourself"}
    return {k: str(data[k]).strip().lower() if k != "reason" else data[k] for k in SCORE_SCHEMA["required"]}


def draft(item: dict, model: str | None) -> str:
    template = (PROMPTS / ("upwork_proposal.txt" if item["kind"] == "upwork" else "community_reply.txt")).read_text(encoding="utf-8")
    filled = template.format_map({**{k: "" for k in C.template_fields(template)},
                                  "post": f"{item.get('title', '')}\n{item.get('snippet', '')}",
                                  "where": item.get("where", item["kind"]), "title": item.get("title", ""),
                                  "snippet": item.get("snippet", ""), "probe": ""})
    if not model:
        return "[No writing model ready. Add ANTHROPIC_API_KEY.]"
    try:
        return C.strict_call(model, filled, C.ROLE_BRIEF["Chair"]).strip()
    except Exception as ex:
        return f"[Draft failed ({type(ex).__name__}). Write this one by hand.]"


# --------------------------------------------------------------------------- state and commands

SEEN = DATA / "scout_seen.json"


def load_seen() -> set[str]:
    try:
        return set(json.loads(SEEN.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError):
        return set()


def save_seen(seen: set[str]) -> None:
    SEEN.parent.mkdir(parents=True, exist_ok=True)
    SEEN.write_text(json.dumps(sorted(seen), indent=0), encoding="utf-8")


def gather_inbox(args) -> list[dict]:
    try:
        msgs = read_eml_dir(args.eml_dir) if args.eml_dir else read_imap(args.days)
    except C.Unavailable as ex:
        print(f"Inbox skipped: {ex}", file=sys.stderr)
        return []
    except imaplib.IMAP4.error as ex:
        print(f"Inbox login failed: {ex}. Check IMAP_USER and the app password.", file=sys.stderr)
        return []
    items = [it for m in msgs for it in items_from_message(m)]
    kinds = Counter(i["where"] if i["kind"] != "reddit" else "Reddit" for i in items)
    print(f"Inbox: {len(msgs)} alert emails, {len(items)} links "
          f"({', '.join(f'{v} {k}' for k, v in kinds.most_common()) or 'none'})", file=sys.stderr)
    return items


def gather_reddit(args) -> list[dict]:
    try:
        queries = [q.strip() for q in QUERIES.read_text(encoding="utf-8").splitlines()
                   if q.strip() and not q.startswith("#")]
    except OSError:
        sys.exit(f"Missing {QUERIES}")
    items: list[dict] = []
    for q in queries[: args.max_queries]:
        try:
            got = search_reddit(q, args.recency)
        except C.Unavailable as ex:
            print(f"Reddit search skipped: {ex}", file=sys.stderr)
            return []
        except Exception as ex:
            print(f"  search failed for '{q[:40]}...': {type(ex).__name__}: {ex}", file=sys.stderr)
            continue
        items += got
    print(f"Reddit search: {len(queries[: args.max_queries])} queries, {len(items)} threads", file=sys.stderr)
    return items


def process(items: list[dict], args) -> None:
    seen = load_seen()
    fresh, keys = [], set()
    for it in items:
        if it["url"] in seen or it["url"] in keys:
            continue
        keys.add(it["url"])
        fresh.append(it)
    print(f"{len(fresh)} new (skipped {len(items) - len(fresh)} already seen)", file=sys.stderr)
    if not fresh:
        return
    stat = C.available()
    worker = next((n for n in ("local", "gemini", "claude", "chatgpt") if stat.get(n) == "ready"), None)
    if not worker:
        sys.exit("No model ready to score posts. Run `python council.py status`.")

    with cf.ThreadPoolExecutor(4) as pool:
        scores = list(pool.map(lambda it: score(it, worker), fresh))
    for it, sc in zip(fresh, scores):
        it.update(sc)

    keep = [it for it in fresh if it["kind"] == "upwork" or it["intent"] in ("buyer", "unknown")
            or (it["intent"] == "peer" and it["fit"] == "high")]
    keep = [it for it in keep if it["fit"] != "low" or it["kind"] == "upwork"]
    print(f"{len(keep)} worth answering; drafting with the Chair", file=sys.stderr)
    writer = next((n for n in ("claude", "chatgpt", "gemini") if stat.get(n) == "ready"), None)
    with cf.ThreadPoolExecutor(4) as pool:
        drafts = list(pool.map(lambda it: draft(it, writer), keep))
    pairs = [(it, d) for it, d in zip(keep, drafts) if d.strip().upper() != "SKIP"]
    if len(pairs) < len(keep):
        print(f"  the writer judged {len(keep) - len(pairs)} post(s) not worth a reply", file=sys.stderr)

    outbox = DATA / "outbox" / TODAY
    outbox.mkdir(parents=True, exist_ok=True)
    start = len(list(outbox.glob("scout-*.txt")))
    for n, (it, text) in enumerate(pairs, start + 1):
        where = it.get("where") or it["kind"]
        how = HOW.get(it["kind"], HOW_DEFAULT)
        (outbox / f"scout-{n:03d}-{it['kind']}.txt").write_text(
            f"WHERE: {where}\nURL: {it['url']}\nTITLE: {it.get('title', '')}\n"
            f"SCORE: {it['intent']} / fit {it['fit']}: {it['reason']}\nHOW: {how}\n\n"
            f"----- their post (as the alert/search showed it) -----\n{it.get('snippet', '')}\n\n"
            f"----- draft -----\n{text}\n", encoding="utf-8")
    # Everything scored counts as seen, so tomorrow's run only shows new posts.
    save_seen(seen | {it["url"] for it in fresh})
    log_items(fresh)
    print(f"Wrote {len(pairs)} drafts to {outbox}", file=sys.stderr)
    page = write_digest(outbox)
    if page:
        print(f"Open this page to work through them: {page}")


LOG = DATA / "scout_log.jsonl"


def log_items(items: list[dict]) -> None:
    """What the scout saw and how it scored it, for the weekly posts and the Monday review."""
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps({"date": TODAY, "where": it.get("where", it["kind"]), "kind": it["kind"],
                                "title": it.get("title", ""), "intent": it.get("intent", ""),
                                "fit": it.get("fit", "")}, ensure_ascii=False) + "\n")


POSTS_SCHEMA = {
    "type": "object",
    "properties": {"posts": {"type": "array", "items": {
        "type": "object",
        "properties": {"type": {"type": "string"}, "text": {"type": "string"}},
        "required": ["type", "text"], "additionalProperties": False}}},
    "required": ["posts"],
    "additionalProperties": False,
}


def report_stats(days: int = 30) -> dict | None:
    """Anonymous totals from recent reports. No company names or domains leave this function."""
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    rates, competitors = [], Counter()
    for raw in (DATA / "reports").glob("*/*/raw.json"):
        try:
            data = json.loads(raw.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        meta, summ = data.get("meta", {}), data.get("summary")
        if not summ or meta.get("date", "") < cutoff or not summ.get("answers"):
            continue
        rates.append(summ["rate"])
        for b in summ.get("top_brands", [])[:3]:
            if not b.get("is_you"):
                competitors[b["name"]] += 1  # public names that AI assistants recommended, not our prospects
    if not rates:
        return None
    return {"companies_checked": len(rates), "median_rate_pct": statistics.median(rates),
            "named_in_under_20pct": sum(r < 20 for r in rates),
            "most_recommended_across_reports": [n for n, _ in competitors.most_common(5)]}


def recent_questions(days: int = 14, limit: int = 25) -> list[str]:
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    out = []
    try:
        for line in LOG.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row.get("date", "") >= cutoff and row.get("intent") in ("buyer", "peer") and row.get("title"):
                out.append(row["title"])
    except (OSError, json.JSONDecodeError):
        pass
    return out[-limit:]


def cmd_posts(args):
    """A week of posts for your own LinkedIn profile. You schedule them once (LinkedIn's
    built-in scheduler or Buffer), and they publish on their own."""
    stats, questions = report_stats(), recent_questions()
    if C.available().get("claude") != "ready":
        sys.exit("Weekly posts are written by Claude. Add ANTHROPIC_API_KEY.")
    prompt = (
        f"Write {args.n} LinkedIn posts for Kaleb Confer's personal profile. Kaleb runs Rank and Reply, a small "
        "service that measures whether ChatGPT, Gemini, Perplexity and Claude recommend a B2B company when its buyers "
        "ask, and does the work to improve it. Audience: founders and marketing leads at B2B software and service "
        "companies.\n\n"
        f"Real numbers from his reports in the last 30 days (anonymous; may be empty): {json.dumps(stats)}\n"
        f"Questions people asked online in the last 2 weeks (paraphrase them, never quote or name anyone): "
        f"{json.dumps(questions)}\n\n"
        "Mix: one post built on the real numbers above (skip it if the numbers are empty; never invent a number), one "
        "practical how-to (for example how to check what ChatGPT says about your company yourself), and one post "
        "answering a question people are asking right now.\n"
        "Rules: 120-220 words each. Plain, specific, first person. No invented clients, results or statistics. Never "
        "name or hint at which companies were checked; brands that AI assistants recommended may be named, since those "
        "answers are public. No engagement bait ('comment YES'), at most 3 hashtags, no emojis. End with one soft line, "
        "for example: 'If you want me to run this check for your company, send me a message.'\n"
        'Return JSON {"posts": [{"type": "data|how-to|question", "text": "..."}]}.'
    )
    try:
        data = json.loads(C.call_claude(prompt, effort="medium", schema=POSTS_SCHEMA))
    except Exception as ex:
        sys.exit(f"Couldn't write the posts: {type(ex).__name__}: {ex}")
    posts = [p for p in data.get("posts", []) if p.get("text", "").strip()]
    outbox = DATA / "outbox" / TODAY
    outbox.mkdir(parents=True, exist_ok=True)
    days = ["Monday", "Wednesday", "Friday", "Tuesday", "Thursday"]
    for i, post in enumerate(posts):
        (outbox / f"posts-{i + 1:02d}-linkedin.txt").write_text(
            f"WHERE: LinkedIn (your profile)\nWHEN: {days[i % len(days)]}, 8:00 am\nTITLE: {post['type']} post\n"
            "HOW: Schedule it once: LinkedIn > Start a post > paste > clock icon (desktop), or in Buffer. It then "
            "publishes on its own. Read it first and change anything that doesn't sound like you.\n\n"
            f"----- draft -----\n{post['text'].strip()}\n", encoding="utf-8")
    note = "with your real report numbers" if stats else "(no reports in the last 30 days, so no data post)"
    print(f"Wrote {len(posts)} posts {note} to {outbox}", file=sys.stderr)
    page = write_digest(outbox)
    if page:
        print(f"Open this page to schedule them: {page}")


def cmd_inbox(args):
    process(gather_inbox(args), args)


def cmd_reddit(args):
    process(gather_reddit(args), args)


def cmd_run(args):
    process(gather_inbox(args) + gather_reddit(args), args)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn, hlp in (("run", cmd_run, "inbox + reddit search, then drafts"),
                          ("inbox", cmd_inbox, "Upwork and F5Bot alert emails only"),
                          ("reddit", cmd_reddit, "reddit.com search only")):
        sp = sub.add_parser(name, help=hlp)
        sp.set_defaults(fn=fn)
        sp.add_argument("--days", type=int, default=2, help="how far back to read alert emails")
        sp.add_argument("--eml-dir", help="parse saved .eml files instead of logging in to the inbox")
        sp.add_argument("--recency", default="week", choices=["day", "week", "month"])
        sp.add_argument("--max-queries", type=int, default=8, help="reddit search queries per run (each is a paid call)")
    pp = sub.add_parser("posts", help="a week of posts for your own LinkedIn profile, to schedule once")
    pp.set_defaults(fn=cmd_posts)
    pp.add_argument("--n", type=int, default=3)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
