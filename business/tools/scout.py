#!/usr/bin/env python3
"""Scout: finds people asking for what we sell on Reddit and Upwork, and drafts
the reply or proposal. You post it yourself.

    python scout.py run                 # everything below, then drafts into the outbox
    python scout.py inbox [--days 2]    # read Upwork + F5Bot alert emails (read-only)
    python scout.py reddit [--recency week]   # search reddit.com via Perplexity or Claude
    python scout.py inbox --eml-dir ../data/scout/eml   # parse saved .eml files instead of IMAP

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

DATA = C.HERE.parent / "data"
TODAY = date.today().isoformat()
PROMPTS = C.HERE / "prompts"
QUERIES = C.HERE / "scout_queries.txt"

REDDIT_THREAD = re.compile(r"https?://(?:www\.|old\.|new\.)?reddit\.com/r/([A-Za-z0-9_]+)/comments/([a-z0-9]+)[^\s\"'<>)]*", re.I)
UPWORK_JOB = re.compile(r"https?://(?:www\.)?upwork\.com/(?:jobs/|freelance-jobs/apply/)[^\s\"'<>)]*~0[0-9a-z]+[^\s\"'<>)]*", re.I)
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
    for pat in (REDDIT_THREAD, UPWORK_JOB):
        m = pat.search(url)
        if m:
            return m.group(0)
    try:
        for values in parse_qs(urlsplit(url).query).values():
            for v in values:
                inner = unwrap(v) if v != url else ""
                if inner and (REDDIT_THREAD.search(inner) or UPWORK_JOB.search(inner)):
                    return inner
    except ValueError:
        pass
    return url


def canonical(url: str) -> str:
    """One key per thread or job, whatever tracking parameters the link carried."""
    m = REDDIT_THREAD.search(url)
    if m:
        return f"https://www.reddit.com/r/{m.group(1)}/comments/{m.group(2)}/"
    m = UPWORK_JOB.search(url)
    if m:
        jid = re.search(r"~0[0-9a-z]+", m.group(0), re.I).group(0)
        return f"https://www.upwork.com/jobs/{jid}"
    return url.split("?")[0]


def items_from_message(msg: email.message.Message) -> list[dict]:
    """Every Reddit thread or Upwork job linked in one alert email."""
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
            url = unwrap(it["href"])
            kind = "reddit" if REDDIT_THREAD.search(url) else "upwork" if UPWORK_JOB.search(url) else None
            if not kind:
                continue
            key = canonical(url)
            after = " ".join(" ".join(it["after"]).split())[:600]
            title = it["anchor"] if it["anchor"] and not GENERIC_ANCHOR.match(it["anchor"]) and len(it["anchor"]) > 8 else ""
            prev = found.get(key)
            if prev:  # the same job is often linked twice (title and a "view job" button)
                prev["title"] = prev["title"] or title
                prev["snippet"] = prev["snippet"] or after
                continue
            found[key] = {"kind": kind, "url": key, "title": title, "snippet": after}

    if text_part is not None:
        try:
            lines = [l.strip() for l in text_part.get_content().splitlines()]
        except (LookupError, UnicodeError):
            lines = []
        for i, line in enumerate(lines):
            for m in re.finditer(r"https?://\S+", line):
                url = unwrap(m.group(0))
                kind = "reddit" if REDDIT_THREAD.search(url) else "upwork" if UPWORK_JOB.search(url) else None
                if not kind:
                    continue
                key = canonical(url)
                if key in found:
                    continue
                before = next((l for l in reversed(lines[max(0, i - 3):i]) if l and not l.startswith("http")), "")
                after = " ".join(l for l in lines[i + 1:i + 4] if l and not l.startswith("http"))[:600]
                found[key] = {"kind": kind, "url": key, "title": before[:200], "snippet": after}

    for it in found.values():
        it["source"] = "f5bot" if "f5bot" in sender else "upwork-alert" if "upwork" in sender else sender or "email"
        if it["kind"] == "reddit":
            it["subreddit"] = REDDIT_THREAD.search(it["url"]).group(1)
    return list(found.values())


def read_imap(days: int) -> list[email.message.Message]:
    host = os.getenv("IMAP_HOST", "imap.gmail.com")
    user, password = os.getenv("IMAP_USER"), os.getenv("IMAP_PASSWORD")
    if not (user and password):
        raise C.Unavailable("IMAP_USER / IMAP_PASSWORD not set in .env (use a Gmail app password)")
    senders = [s.strip() for s in os.getenv("ALERT_SENDERS", "upwork.com,f5bot.com").split(",") if s.strip()]
    since = (date.today() - timedelta(days=days)).strftime("%d-%b-%Y")
    msgs = []
    with imaplib.IMAP4_SSL(host) as box:
        box.login(user, password)
        box.select(os.getenv("IMAP_FOLDER", "INBOX"), readonly=True)  # read-only: nothing is marked or moved
        for s in senders:
            status, data = box.search(None, "FROM", f'"{s}"', "SINCE", since)
            if status != "OK":
                continue
            for num in data[0].split():
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
                                   "subreddit": REDDIT_THREAD.search(key).group(1), "query": query})
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
        f"Source: {item['kind']} ({item.get('subreddit') or item.get('source')})\nTitle: {item.get('title', '')}\n"
        f"Text: {item.get('snippet', '')}\n\n"
        "Classify:\n- intent: 'buyer' (a business that has this problem or wants this done), 'peer' (a marketer or "
        "freelancer discussing the topic), or 'irrelevant'\n- fit: 'high', 'medium' or 'low' for us specifically\n"
        "- reason: one short sentence"
    ), SCORE_SCHEMA)
    if not data:
        return {"intent": "unknown", "fit": "unknown", "reason": "couldn't score; read it yourself"}
    return {k: str(data[k]).strip().lower() if k != "reason" else data[k] for k in SCORE_SCHEMA["required"]}


def draft(item: dict, model: str | None) -> str:
    template = (PROMPTS / ("reddit_reply.txt" if item["kind"] == "reddit" else "upwork_proposal.txt")).read_text(encoding="utf-8")
    filled = template.format_map({**{k: "" for k in C.template_fields(template)},
                                  "post": f"{item.get('title', '')}\n{item.get('snippet', '')}",
                                  "subreddit": item.get("subreddit", ""), "title": item.get("title", ""),
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
    print(f"Inbox: {len(msgs)} alert emails, {len(items)} links "
          f"({sum(i['kind'] == 'reddit' for i in items)} Reddit, {sum(i['kind'] == 'upwork' for i in items)} Upwork)",
          file=sys.stderr)
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
        where = f"r/{it['subreddit']}" if it["kind"] == "reddit" else "Upwork"
        how = ("Post it yourself from your own Reddit account after reading the subreddit's rules. Edit it into your "
               "own words first." if it["kind"] == "reddit" else
               "Open the job, check it's fixed-price and still open, edit, and submit by hand.")
        (outbox / f"scout-{n:03d}-{it['kind']}.txt").write_text(
            f"WHERE: {where}\nURL: {it['url']}\nTITLE: {it.get('title', '')}\n"
            f"SCORE: {it['intent']} / fit {it['fit']}: {it['reason']}\nHOW: {how}\n\n"
            f"----- their post (as the alert/search showed it) -----\n{it.get('snippet', '')}\n\n"
            f"----- draft -----\n{text}\n", encoding="utf-8")
    # Everything scored counts as seen, so tomorrow's run only shows new posts.
    save_seen(seen | {it["url"] for it in fresh})
    print(f"Wrote {len(pairs)} drafts to {outbox}", file=sys.stderr)


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
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
