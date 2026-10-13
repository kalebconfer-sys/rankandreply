#!/usr/bin/env python3
"""AI search visibility engine.

Asks ChatGPT, Gemini, Perplexity and Claude the questions a company's buyers ask,
then measures who gets recommended. The same engine produces the cold-email hook,
the free report that closes the sale, and the monthly client report.

Prospecting (one line per lead):
    python visibility.py enrich    --in apollo.csv        --out leads_1.csv
    python visibility.py probe     --in leads_1.csv       --out leads_2.csv
    python visibility.py firstline --in leads_2.csv       --out leads_ready.csv

Reports (one company, thorough):
    python visibility.py questions --brand "Acme" --domain acme.com --n 40 --out q.txt
    python visibility.py snapshot  --brand "Acme" --domain acme.com --n 10 --runs 2 --pdf
    python visibility.py snapshot  --brand "Acme" --domain acme.com --questions q.txt --runs 3 --compare ../data/reports/acme/2026-10-12/raw.json

Everything is written under business/data/ (gitignored). Nothing is sent anywhere
except the AI APIs and a GET request to the company's own homepage.

How "named" is decided (the rule every number and every email line depends on):
    yes    the answer contains the company's full name, its domain, or a brand the
           extractor found in the answer that normalizes to the same name
           ("Acme Software, Inc." = "Acme" = "Acme Software")
    maybe  only a shortened form of the name appears; never counted, never claimed
    no     none of the above
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import datetime as dt
import html
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

import council as C

DATA = C.HERE.parent / "data"
TODAY = dt.date.today().isoformat()

ENGINE_LABEL = {"chatgpt": "ChatGPT", "gemini": "Gemini", "perplexity": "Perplexity", "claude": "Claude"}

# Hosts that aren't a company's own website. Grouping leads by these would merge strangers.
SOCIAL_HOSTS = {
    "facebook.com", "m.facebook.com", "linkedin.com", "instagram.com", "yelp.com", "linktr.ee",
    "sites.google.com", "google.com", "g.page", "business.site", "twitter.com", "x.com", "youtube.com",
    "tiktok.com", "yellowpages.com", "angi.com", "houzz.com", "nextdoor.com", "bbb.org", "thumbtack.com",
}


def _ssl_context() -> ssl.SSLContext:
    """System certificates plus certifi's, so Python.org installs on macOS work too."""
    ctx = ssl.create_default_context()
    try:
        import certifi
        ctx.load_verify_locations(certifi.where())
    except Exception:
        pass
    return ctx


SSL_CTX = _ssl_context()


# --------------------------------------------------------------------------- names and domains

LEGAL_SUFFIX = re.compile(r"[,.]?\s+(inc|llc|l\.l\.c|ltd|limited|corp|corporation|gmbh|plc|pty|llp|lp|bv)\.?$", re.I)
GENERIC_WORDS = {
    "inc", "llc", "ltd", "limited", "co", "company", "corp", "corporation", "gmbh", "plc", "pty", "llp", "lp",
    "software", "technologies", "technology", "tech", "solutions", "systems", "labs", "group", "holdings",
    "hq", "app", "apps", "ai", "io", "platform", "crm", "cloud", "online", "digital", "services", "consulting",
    "agency", "partners",
}


def clean_company(name: str) -> str:
    """'Acme Software, Inc.' -> 'Acme Software'. Only legal suffixes are removed, and never
    down to nothing ('The Limited' stays 'The Limited')."""
    original = " ".join((name or "").split())
    out = original
    while LEGAL_SUFFIX.search(out):
        shorter = LEGAL_SUFFIX.sub("", out).strip()
        if len(shorter) < 2 or shorter.casefold() in {"the", "a", "an"}:
            break
        out = shorter
    return out or original


def name_key(name: str) -> str:
    """Normalized identity for comparing names: 'HubSpot CRM' and 'HubSpot' -> 'hubspot'."""
    words = re.findall(r"[a-z0-9]+", (name or "").casefold())
    if words and words[0] == "the" and len(words) > 1:
        words = words[1:]
    while len(words) > 1 and words[-1] in GENERIC_WORDS:
        words.pop()
    return "".join(words)


def norm_domain(url: str) -> str:
    """'https://www.Acme.com/pricing?utm_source=x' -> 'acme.com'."""
    url = (url or "").strip()
    if not url:
        return ""
    if "://" not in url:
        url = "http://" + url
    try:
        host = urlsplit(url).hostname or ""
    except ValueError:
        return ""
    return host.lower().removeprefix("www.")


def domain_root(domain: str) -> str:
    labels = domain.split(".")
    if len(labels) >= 3 and labels[-2] in {"co", "com", "org", "net", "ac", "gov"}:
        return labels[-3]
    return labels[-2] if len(labels) >= 2 else domain


class Target:
    """Everything needed to decide whether an answer names one company."""

    def __init__(self, brand: str, domain: str = "", aliases: list[str] | None = None):
        self.name = clean_company(brand)
        self.domain = norm_domain(domain)
        self.keys = {k for k in [name_key(self.name), *(name_key(a) for a in aliases or [])] if len(k) >= 3}
        if self.domain and len(domain_root(self.domain)) >= 4:
            self.keys.add(domain_root(self.domain))
        self.strong = []
        for n in [self.name, *(aliases or [])]:
            if not n:
                continue
            # One-word names are matched case-sensitively, so "Close" isn't found in "close to budget".
            flags = 0 if len(n.split()) == 1 else re.I
            self.strong.append(re.compile(r"(?<![\w-])" + re.escape(n) + r"(?![\w-])", flags))
        if self.domain:
            self.strong.append(re.compile(r"(?<![\w.-])(?:www\.)?" + re.escape(self.domain) + r"(?![\w-])", re.I))
        words = [w for w in re.findall(r"\w+", self.name)]
        while len(words) > 1 and words[-1].casefold() in GENERIC_WORDS:
            words.pop()
        core = " ".join(words)
        self.weak = (re.compile(r"(?<![\w-])" + r"\s+".join(map(re.escape, words)) + r"(?![\w-])")
                     if core and core.casefold() != self.name.casefold() and len(core) >= 3 else None)

    def is_brand(self, brand: str) -> bool:
        return name_key(brand) in self.keys

    def mention(self, text: str, brands: list[str]) -> str:
        if any(p.search(text) for p in self.strong) or any(self.is_brand(b) for b in brands):
            return "yes"
        if self.weak and self.weak.search(text):
            return "maybe"
        return "no"


# --------------------------------------------------------------------------- engines
# Each returns (answer_text, source_urls). Web search is on wherever the API offers it,
# because that is how the consumer apps answer "best X for Y" questions today.

def ask_chatgpt(q: str) -> tuple[str, list[str]]:
    if not os.getenv("OPENAI_API_KEY"):
        raise C.Unavailable("OPENAI_API_KEY not set")
    import openai
    client = openai.OpenAI(timeout=600)
    try:
        r = client.responses.create(
            model=C.OPENAI_MODEL,
            tools=[{"type": os.getenv("OPENAI_WEB_TOOL", "web_search")}],
            input=q,
        )
        urls = []
        for item in r.output or []:
            for part in getattr(item, "content", None) or []:
                for ann in getattr(part, "annotations", None) or []:
                    if getattr(ann, "url", None):
                        urls.append(ann.url)
        return r.output_text, urls
    except openai.BadRequestError:
        return C.call_chatgpt(q), []  # model without web search: plain answer


def ask_gemini(q: str) -> tuple[str, list[str]]:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise C.Unavailable("GEMINI_API_KEY not set")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{C.GEMINI_MODEL}:generateContent"
    body = json.dumps({"contents": [{"role": "user", "parts": [{"text": q}]}], "tools": [{"google_search": {}}]}).encode()
    for attempt in range(4):
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", "x-goog-api-key": key})
        try:
            with urllib.request.urlopen(req, timeout=300, context=SSL_CTX) as resp:
                data = json.load(resp)
            break
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 503) and attempt < 3:
                time.sleep(2 ** (attempt + 1))
                continue
            raise
    cand = (data.get("candidates") or [{}])[0]
    text = "".join(p.get("text", "") for p in (cand.get("content") or {}).get("parts", []))
    chunks = (cand.get("groundingMetadata") or {}).get("groundingChunks", [])
    # Grounding URIs are redirect links; the title carries the real domain.
    urls = [c.get("web", {}).get("title", "") for c in chunks if c.get("web")]
    return text, urls


def ask_perplexity(q: str) -> tuple[str, list[str]]:
    text, resp = C._openai_compatible(*C.ENDPOINTS["perplexity"], q, "")
    extra = getattr(resp, "model_extra", None) or {}
    urls = extra.get("citations") or [r.get("url") for r in extra.get("search_results") or [] if r.get("url")]
    return text, urls


def ask_claude(q: str) -> tuple[str, list[str]]:
    urls: list[str] = []
    return C.call_claude(q, web=True, effort="medium", sources=urls), urls


ENGINES = {"chatgpt": ask_chatgpt, "gemini": ask_gemini, "perplexity": ask_perplexity, "claude": ask_claude}
ENGINE_KEYS = {"chatgpt": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY",
               "perplexity": "PERPLEXITY_API_KEY", "claude": "ANTHROPIC_API_KEY"}


def ask(engine: str, q: str) -> tuple[bool, str, list[str]]:
    """(ok, answer, source_urls). Never raises."""
    try:
        text, urls = ENGINES[engine](q)
        return bool((text or "").strip()), text or "", urls
    except Exception as ex:
        return False, f"{engine} {type(ex).__name__}: {ex}", []


def ready_engines(wanted: str | None) -> list[str]:
    names = [n.strip() for n in wanted.split(",")] if wanted else list(ENGINES)
    ready = [n for n in names if n in ENGINES and os.getenv(ENGINE_KEYS[n])]
    if not ready:
        sys.exit("No answer engine has a key. Add OPENAI / GEMINI / PERPLEXITY / ANTHROPIC keys to business/tools/.env")
    return ready


# --------------------------------------------------------------------------- helpers

def worker_name() -> str:
    """Cheapest ready model for small structured jobs (extraction, classification)."""
    stat = C.available()
    for n in ("local", "gemini", "claude", "chatgpt"):
        if stat.get(n) == "ready":
            return n
    sys.exit("No model ready. Start Ollama or add a key to business/tools/.env")


def chair_name() -> str:
    stat = C.available()
    for n in ("claude", "chatgpt", "gemini", "local"):
        if stat.get(n) == "ready":
            return n
    sys.exit("No model ready. Add a key to business/tools/.env")


COST_GUARD_EXIT = 3  # the .bat files look for this code and ask "run it anyway?"


def confirm_cost(calls: int, limit: int, yes: bool, what: str) -> None:
    print(f"About {calls} paid API calls for {what}.", file=sys.stderr)
    if calls > limit and not yes:
        print(f"That's over {limit}. Re-run with --yes to confirm, or make the job smaller.", file=sys.stderr)
        sys.exit(COST_GUARD_EXIT)


BRANDS_SCHEMA = {
    "type": "object",
    "properties": {"brands": {"type": "array", "items": {"type": "string"}}},
    "required": ["brands"],
    "additionalProperties": False,
}


def extract_brands(answer: str, model: str) -> list[str] | None:
    """Companies the answer recommends, in order. Only names that literally appear in the
    answer are kept, so a model can't add one. None means extraction failed."""
    if not answer.strip():
        return []
    data = C.call_json(model, (
        "List every company, product or service provider that this answer recommends or names as an option, "
        "in the order they first appear. Copy each name exactly as written. Exclude publications, review sites and "
        "the AI itself unless they are recommended as the solution.\n\n<answer>\n" + answer[:8000] + "\n</answer>"
    ), BRANDS_SCHEMA)
    if data is None:
        return None
    text = answer.casefold()
    seen, out = set(), []
    for b in data["brands"]:
        b = b.strip()
        if b and b.casefold() in text and name_key(b) not in seen:
            seen.add(name_key(b))
            out.append(b)
    return out[:25]


# --------------------------------------------------------------------------- website reading

class _SiteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title, self.desc, self.heads, self.text = "", "", [], []
        self._in, self._skip = None, 0

    def handle_starttag(self, tag, attrs):
        a = {k: v or "" for k, v in attrs}
        if tag in ("script", "style", "noscript", "svg"):
            self._skip += 1
        elif tag == "meta" and (a.get("name", "").lower() == "description" or a.get("property") == "og:description"):
            self.desc = self.desc or a.get("content", "")
        elif tag in ("title", "h1", "h2"):
            self._in = tag

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg") and self._skip:
            self._skip -= 1
        if tag == self._in:
            self._in = None

    def handle_data(self, data):
        if self._skip:
            return
        d = " ".join(data.split())
        if not d:
            return
        if self._in == "title":
            self.title += d
        elif self._in in ("h1", "h2"):
            self.heads.append(d)
        self.text.append(d)


def fetch_site(domain: str) -> dict:
    url = domain if domain.startswith("http") else f"https://{domain}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; RankAndReplyResearch/1.0)"})
    try:
        with urllib.request.urlopen(req, timeout=20, context=SSL_CTX) as r:
            raw = r.read(1_500_000).decode(r.headers.get_content_charset() or "utf-8", "replace")
        p = _SiteParser()
        p.feed(raw)
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}
    return {"ok": True, "title": p.title[:200], "description": p.desc[:500],
            "headings": p.heads[:15], "text": " ".join(p.text)[:4000]}


# --------------------------------------------------------------------------- questions

PROFILE_SCHEMA = {
    "type": "object",
    "properties": {
        "category": {"type": "string"},
        "buyer": {"type": "string"},
        "buyer_question": {"type": "string"},
        "competitors": {"type": "array", "items": {"type": "string"}},
        "questions": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["category", "buyer", "buyer_question", "competitors", "questions"],
    "additionalProperties": False,
}


def profile_company(brand: str, site: dict, n_questions: int, model: str, region: str = "") -> dict | None:
    region_line = f"The company serves {region}; include the region in questions where a buyer would.\n" if region else ""
    return C.call_json(model, (
        f"Company: {brand}\nWebsite title: {site.get('title', '')}\nMeta description: {site.get('description', '')}\n"
        f"Headings: {' | '.join(site.get('headings', []))}\nPage text: {site.get('text', '')[:2500]}\n\n"
        f"{region_line}"
        "From this, work out:\n"
        "- category: what they sell, in the plain words a buyer would type (e.g. 'field service management software')\n"
        "- buyer: who buys it (e.g. 'HVAC companies with 5-50 technicians')\n"
        "- buyer_question: the single most valuable question a buyer would ask ChatGPT when looking for this, "
        "phrased exactly as a buyer would ask it, WITHOUT naming this company or any competitor\n"
        "- competitors: up to 5 direct competitors you are confident exist\n"
        f"- questions: {n_questions} different questions real buyers ask an AI assistant at the shortlist stage "
        "(best X for Y, alternatives to a big competitor, X vs Y, which X for a specific situation or budget). "
        "Never name this company in a question."
    ), PROFILE_SCHEMA)


# --------------------------------------------------------------------------- snapshot

def run_matrix(questions: list[str], engines: list[str], runs: int, target: Target, extractor: str,
               workers: int) -> list[dict]:
    jobs = [(q, e, r) for q in questions for e in engines for r in range(runs)]

    def one(job):
        q, e, r = job
        ok, text, urls = ask(e, q)
        brands = extract_brands(text, extractor) if ok else []
        mention = target.mention(text, brands or []) if ok else "no"
        return {
            "question": q, "engine": e, "run": r, "answer": text, "sources": urls, "failed": not ok,
            "mention": mention, "mentioned": mention == "yes",
            "cited": ok and bool(target.domain) and any(norm_domain(u) == target.domain or
                                                         norm_domain(u).endswith("." + target.domain) for u in urls),
            "brands": brands or [], "brands_failed": ok and brands is None,
        }

    out = []
    with cf.ThreadPoolExecutor(workers) as pool:
        for i, res in enumerate(pool.map(one, jobs), 1):
            out.append(res)
            if i % 10 == 0 or i == len(jobs):
                print(f"  {i}/{len(jobs)} answers", file=sys.stderr)
    return out


def aggregate(rows: list[dict], target: Target) -> dict:
    ok = [r for r in rows if not r["failed"]]
    by_engine = {}
    for e in dict.fromkeys(r["engine"] for r in rows):
        er = [r for r in ok if r["engine"] == e]
        hits = sum(r["mentioned"] for r in er)
        by_engine[e] = {"answers": len(er), "mentioned": hits, "rate": round(100 * hits / len(er)) if er else None}

    # Competitors: variants of one name ('HubSpot', 'HubSpot CRM') count once per answer.
    counts, variants = Counter(), defaultdict(Counter)
    for r in ok:
        for k in {name_key(b) for b in r["brands"] if not target.is_brand(b)}:
            counts[k] += 1
        for b in r["brands"]:
            if not target.is_brand(b):
                variants[name_key(b)][b] += 1
    mentioned = sum(r["mentioned"] for r in ok)
    table = [{"name": variants[k].most_common(1)[0][0], "answers": c, "is_you": False} for k, c in counts.most_common(15)]
    table.append({"name": target.name, "answers": mentioned, "is_you": True})  # same number as the headline
    table.sort(key=lambda b: -b["answers"])
    for b in table:
        b["share"] = round(100 * b["answers"] / len(ok)) if ok else 0

    questions = {}
    for r in ok:
        questions.setdefault(r["question"], {}).setdefault(r["engine"], []).append(r["mentioned"])
    sources = Counter()
    for r in ok:
        for d in {norm_domain(u) for u in r["sources"] if u}:
            if d:
                sources[d] += 1
    return {
        "answers": len(ok), "failed": len(rows) - len(ok), "mentioned": mentioned,
        "rate": round(100 * mentioned / len(ok)) if ok else 0,
        "maybe": sum(r["mention"] == "maybe" for r in ok),
        "brands_failed": sum(r["brands_failed"] for r in ok),
        "by_engine": by_engine, "top_brands": table, "by_question": questions,
        "top_sources": [{"domain": d, "answers": c} for d, c in sources.most_common(15)],
    }


FIXES_SCHEMA = {
    "type": "object",
    "properties": {
        "headline": {"type": "string"},
        "summary": {"type": "string"},
        "fixes": {"type": "array", "items": {
            "type": "object",
            "properties": {"title": {"type": "string"}, "why": {"type": "string"}, "how": {"type": "string"}},
            "required": ["title", "why", "how"], "additionalProperties": False}},
    },
    "required": ["headline", "summary", "fixes"],
    "additionalProperties": False,
}


def write_findings(target: Target, site: dict, agg: dict, rows: list[dict]) -> dict:
    sample = [{"q": r["question"], "engine": r["engine"], "named": r["brands"][:6]} for r in rows if not r["failed"]][:40]
    data = C.call_json(chair_name(), (
        f"You are writing the findings section of an AI search visibility report for {target.name}.\n"
        f"Their site: {json.dumps({k: site.get(k) for k in ('title', 'description', 'headings')})}\n"
        f"Results: {json.dumps({k: agg[k] for k in ('answers', 'mentioned', 'rate', 'by_engine', 'top_brands')})}\n"
        f"Sites the AI engines cited most: {json.dumps(agg['top_sources'])}\n"
        f"Sample of who was named per question: {json.dumps(sample)}\n\n"
        "Write: a one-sentence headline stating the finding plainly with the real numbers above (don't round them "
        "differently); a 3-4 sentence summary a busy founder will read; and the 5 highest-impact fixes. Each fix needs "
        "a title, why it matters (tie it to the data above, e.g. a cited site they are missing from, or a competitor "
        "strength), and how to do it in concrete steps. Fixes should be things like: comparison and alternatives pages, "
        "getting listed on the review sites and lists the engines cite, clear category and use-case wording on the "
        "homepage, FAQ content that answers the buyer questions, structured data. Never promise rankings. Plain "
        "English, no hype."
    ), FIXES_SCHEMA)
    return data or {"headline": f"{target.name} was named in {agg['mentioned']} of {agg['answers']} AI answers.",
                    "summary": "", "fixes": []}


def render_html(target: Target, meta: dict, agg: dict, findings: dict, compare: dict | None,
                prepared_by: str = "Rank and Reply") -> str:
    e = html.escape
    eng_rows = "".join(
        f"<tr><td>{e(ENGINE_LABEL.get(k, k))}</td><td>{v['mentioned']} / {v['answers']}</td>"
        f"<td><div class='bar'><span style='width:{v['rate'] or 0}%'></span></div></td>"
        f"<td>{str(v['rate']) + '%' if v['rate'] is not None else 'failed'}</td></tr>"
        for k, v in agg["by_engine"].items())
    brand_rows = "".join(
        f"<tr class='{'you' if b['is_you'] else ''}'><td>{i}</td><td>{e(b['name'])}{' (you)' if b['is_you'] else ''}</td>"
        f"<td>{b['answers']}</td><td>{b['share']}%</td></tr>"
        for i, b in enumerate(agg["top_brands"], 1))
    engines = list(agg["by_engine"])
    answered = sum(1 for v in agg["by_engine"].values() if v["answers"])
    q_head = "".join(f"<th>{e(ENGINE_LABEL.get(x, x))}</th>" for x in engines)
    q_rows = ""
    for q, per in agg["by_question"].items():
        cells = ""
        for x in engines:
            hits = per.get(x, [])
            cells += f"<td class='{'yes' if any(hits) else 'no'}'>{sum(hits)}/{len(hits)}</td>" if hits else "<td>–</td>"
        q_rows += f"<tr><td>{e(q)}</td>{cells}</tr>"
    src_rows = "".join(f"<tr><td>{e(x['domain'])}</td><td>{x['answers']}</td></tr>" for x in agg.get("top_sources", []))
    src_block = ("<h2>Sites the AI engines cited most</h2><p>Being listed, reviewed or mentioned on these sites is often "
                 "what gets a company named.</p>"
                 f"<table><tr><th>Site</th><th>Answers citing it</th></tr>{src_rows}</table>") if src_rows else ""
    fixes = "".join(f"<li><strong>{e(f['title'])}</strong><p>{e(f['why'])}</p><p class='how'>{e(f['how'])}</p></li>"
                    for f in findings.get("fixes", []))
    fixes_block = f"<h2>The five fixes that matter most</h2><ol class='fixes'>{fixes}</ol>" if fixes else ""
    delta = ""
    if compare:
        d = agg["rate"] - compare.get("rate", 0)
        delta = (f"<p class='delta'>Last report ({e(compare.get('date', ''))}): {compare.get('rate', 0)}% "
                 f"&rarr; now {agg['rate']}% ({'+' if d >= 0 else ''}{d} points)</p>")
    notes = [f"{agg['failed']} request(s) failed and are excluded."]
    missing = [ENGINE_LABEL.get(k, k) for k, v in agg["by_engine"].items() if not v["answers"]]
    if missing:
        notes.append(f"No answers were collected from {', '.join(missing)}, so it is not included in the totals.")
    if agg.get("maybe"):
        notes.append(f"{agg['maybe']} answer(s) mentioned a shortened form of the name and were not counted as named.")
    if agg.get("brands_failed"):
        notes.append(f"Competitor names could not be read from {agg['brands_failed']} answer(s).")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Visibility Report: {e(target.name)}</title>
<style>
:root{{--ink:#14181d;--body:#4a5562;--muted:#8a949f;--line:#e4e0d9;--sand:#f7f5f1;--accent:#e2670a;--ok:#2f7d4f;--bad:#b4442c}}
*{{box-sizing:border-box}}body{{margin:0;background:#fff;color:var(--body);font:16px/1.6 system-ui,-apple-system,'Segoe UI',sans-serif}}
.wrap{{max-width:900px;margin:0 auto;padding:40px 20px}}h1,h2{{color:var(--ink);line-height:1.2}}h1{{font-size:2rem;margin:.2em 0}}
h2{{font-size:1.25rem;margin-top:2.2em;border-bottom:2px solid var(--line);padding-bottom:.3em}}
.eyebrow{{text-transform:uppercase;letter-spacing:.12em;font-size:.75rem;font-weight:700;color:var(--accent)}}
.big{{font-size:3.2rem;font-weight:800;color:var(--ink);line-height:1}}.kpi{{display:flex;gap:28px;flex-wrap:wrap;background:var(--sand);padding:22px;border-radius:10px;margin:22px 0}}
.kpi div{{min-width:140px}}.kpi small{{display:block;color:var(--muted)}}
table{{width:100%;border-collapse:collapse;font-size:.95rem}}th,td{{text-align:left;padding:8px 6px;border-bottom:1px solid var(--line);vertical-align:top}}
th{{color:var(--muted);font-weight:600;font-size:.8rem;text-transform:uppercase;letter-spacing:.05em}}
.bar{{background:#eee;height:10px;border-radius:5px;overflow:hidden;min-width:120px}}.bar span{{display:block;height:100%;background:var(--accent)}}
tr.you td{{font-weight:700;color:var(--ink);background:#fdf0e4}}td.yes{{color:var(--ok);font-weight:700}}td.no{{color:var(--bad)}}
ol.fixes li{{margin-bottom:1em}}ol.fixes p{{margin:.3em 0}}.how{{color:var(--ink)}}.delta{{font-weight:700;color:var(--ink)}}
.method{{font-size:.85rem;color:var(--muted);margin-top:3em;border-top:1px solid var(--line);padding-top:1em}}
@media print{{.wrap{{padding:0}}}}
</style></head><body><div class="wrap">
<span class="eyebrow">AI search visibility report &middot; {e(meta['date'])}</span>
<h1>{e(target.name)}</h1>
<p><strong>{e(findings.get('headline', ''))}</strong></p>
<p>{e(findings.get('summary', ''))}</p>
{delta}
<div class="kpi"><div><span class="big">{agg['rate']}%</span><small>of AI answers named {e(target.name)}</small></div>
<div><span class="big">{agg['answers']}</span><small>answers checked across {answered} AI engine{'s' if answered != 1 else ''}</small></div>
<div><span class="big">{len(agg['by_question'])}</span><small>buyer questions asked</small></div></div>
<h2>By AI engine</h2><table><tr><th>Engine</th><th>Named you</th><th></th><th>Rate</th></tr>{eng_rows}</table>
<h2>Who the AI engines recommend</h2>
<p>Share of answers that named each company, across every engine and question.</p>
<table><tr><th>#</th><th>Company</th><th>Answers</th><th>Share</th></tr>{brand_rows}</table>
<h2>Question by question</h2><p>How many runs named {e(target.name)}, per engine.</p>
<table><tr><th>Buyer question</th>{q_head}</tr>{q_rows}</table>
{src_block}
{fixes_block}
<p class="method">Method: each question was put to each engine {meta['runs']} time(s) through its official API on {e(meta['date'])}, with web search on where the API offers it. AI answers vary between runs, users and locations, so these are sampled percentages, not fixed rankings. A company counts as named when its name or domain appears in the answer. {' '.join(e(n) for n in notes)} Prepared by {e(prepared_by)}.</p>
</div></body></html>"""


def to_pdf(html_path: Path) -> str:
    """Print the report to PDF with Playwright if installed; otherwise say how to do it by hand."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return "skipped (pip install playwright && playwright install chromium), or open report.html in Chrome and Print > Save as PDF"
    pdf = html_path.with_suffix(".pdf")
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.goto(html_path.resolve().as_uri())
        page.pdf(path=str(pdf), format="Letter", print_background=True,
                 margin={"top": "0.5in", "bottom": "0.5in", "left": "0.4in", "right": "0.4in"})
        browser.close()
    return str(pdf)


def cmd_questions(args) -> None:
    site = fetch_site(norm_domain(args.domain))
    if not site.get("ok"):
        print(f"Warning: couldn't read the site: {site.get('error')}", file=sys.stderr)
    prof = profile_company(clean_company(args.brand), site, args.n, chair_name(), args.region or "")
    if not prof:
        sys.exit("Couldn't generate questions.")
    text = "\n".join(prof["questions"][: args.n]) + "\n"
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"Category: {prof['category']}\nBuyer: {prof['buyer']}\nCompetitors: {', '.join(prof['competitors'])}\n"
              f"Wrote {args.out}", file=sys.stderr)
    else:
        print(text, end="")


def cmd_snapshot(args) -> None:
    domain = norm_domain(args.domain)
    if domain in SOCIAL_HOSTS:
        sys.exit(f"{args.domain} is a social or directory page, not the company's own site. Pass the real website.")
    aliases = [a.strip() for a in (args.aliases or "").split(",") if a.strip()]
    target = Target(args.brand, domain, aliases)
    engines = ready_engines(args.engines)

    # Check everything that could fail cheaply BEFORE spending money.
    compare = None
    if args.compare:
        try:
            compare = json.loads(Path(args.compare).read_text(encoding="utf-8"))["summary"]
        except Exception as ex:
            sys.exit(f"Couldn't read --compare file {args.compare}: {ex}")
    if args.questions:
        try:
            questions = [l.strip() for l in Path(args.questions).read_text(encoding="utf-8-sig").splitlines() if l.strip()]
        except OSError as ex:
            sys.exit(f"Couldn't read --questions file: {ex}")
    else:
        questions = None
    slug = re.sub(r"[^a-z0-9]+", "-", target.name.lower()).strip("-") or "report"
    out = Path(args.out) if args.out else DATA / "reports" / slug / TODAY
    out.mkdir(parents=True, exist_ok=True)

    site = fetch_site(domain)
    if not site.get("ok"):
        print(f"Warning: couldn't read {domain}: {site.get('error')}", file=sys.stderr)
    if questions is None:
        prof = profile_company(target.name, site, args.n, chair_name(), args.region or "")
        if not prof or not prof.get("questions"):
            sys.exit("Couldn't generate questions. Pass --questions with a text file, one question per line.")
        questions = prof["questions"][: args.n]

    extractor = worker_name()
    answers = len(questions) * len(engines) * args.runs
    paid = answers + (0 if extractor == "local" else answers) + 2
    print(f"{len(questions)} questions x {len(engines)} engines ({', '.join(engines)}) x {args.runs} runs = {answers} answers",
          file=sys.stderr)
    confirm_cost(paid, 200, args.yes, "this report")

    rows = run_matrix(questions, engines, args.runs, target, extractor, args.workers)
    agg = aggregate(rows, target)
    meta = {"brand": target.name, "domain": domain, "date": TODAY, "runs": args.runs, "engines": engines}
    (out / "questions.txt").write_text("\n".join(questions) + "\n", encoding="utf-8")
    if agg["answers"] == 0:
        (out / "raw.json").write_text(json.dumps({"meta": meta, "rows": rows}, indent=2, ensure_ascii=False), encoding="utf-8")
        sys.exit(f"Every request failed, so no report was written. First error: {rows[0]['answer'] if rows else 'none'}\n"
                 f"Details: {out / 'raw.json'}")
    for k, v in agg["by_engine"].items():
        if not v["answers"]:
            print(f"Warning: {ENGINE_LABEL.get(k, k)} returned no answers. Check its key and model name.", file=sys.stderr)

    findings = write_findings(target, site, agg, rows)
    (out / "raw.json").write_text(json.dumps({"meta": meta, "summary": {**agg, "date": TODAY}, "findings": findings,
                                              "rows": rows}, indent=2, ensure_ascii=False), encoding="utf-8")
    html_path = out / "report.html"
    html_path.write_text(render_html(target, meta, agg, findings, compare, args.prepared_by), encoding="utf-8")
    print(f"\n{findings.get('headline', '')}\nReport: {html_path}")
    if args.pdf:
        print(f"PDF: {to_pdf(html_path)}")


# --------------------------------------------------------------------------- prospect pipeline

ALIASES = {
    "company": ["company name for emails", "company", "company name", "company_name", "organization",
                "organization name", "account name"],
    "website": ["website", "company website", "website url", "domain", "company domain", "url"],
    "first_name": ["first name", "first_name", "firstname"],
    "email": ["email", "email address", "work email"],
}


def pick(row: dict, field: str) -> str:
    low = {k.strip().lower(): v for k, v in row.items() if k}
    for a in ALIASES[field]:
        if low.get(a):
            return low[a].strip()
    return (row.get(field) or "").strip()


def read_rows(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        return [{k: v or "" for k, v in r.items() if k} for r in csv.DictReader(f)]


def write_rows(path: str, rows: list[dict]) -> None:
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def cmd_enrich(args) -> None:
    rows = read_rows(args.inp)
    model = args.ai or worker_name()
    todo = {}
    for row in rows:
        domain = norm_domain(pick(row, "website"))
        if domain and domain not in SOCIAL_HOSTS and not row.get("buyer_question"):
            todo.setdefault(domain, clean_company(pick(row, "company")))
    print(f"Enriching {len(rows)} leads ({len(todo)} websites) with {model}", file=sys.stderr)
    if model != "local":
        confirm_cost(len(todo), 300, args.yes, "enrichment")

    def profile(item):
        domain, company = item
        try:
            site = fetch_site(domain)
            if not site.get("ok"):
                return domain, {"enrich_status": f"site error: {site.get('error', '')[:80]}"}
            prof = profile_company(company, site, 3, model, args.region or "")
        except Exception as ex:  # one bad lead never stops the batch
            return domain, {"enrich_status": f"error: {type(ex).__name__}: {str(ex)[:80]}"}
        if not prof:
            return domain, {"enrich_status": "model error"}
        return domain, {"enrich_status": "ok", "domain": domain, "category": prof["category"], "buyer": prof["buyer"],
                        "buyer_question": prof["buyer_question"], "competitors": "; ".join(prof["competitors"][:5]),
                        "site_title": site.get("title", "")}

    with cf.ThreadPoolExecutor(args.workers) as pool:
        found = dict(pool.map(profile, todo.items()))
    out = []
    for row in rows:
        domain = norm_domain(pick(row, "website"))
        if row.get("buyer_question"):
            out.append(row)
        elif not domain:
            out.append({**row, "enrich_status": "no website"})
        elif domain in SOCIAL_HOSTS:
            out.append({**row, "enrich_status": "no own website (social or directory page)"})
        else:
            out.append({**row, **found[domain]})
    write_rows(args.out, out)
    ok = sum(r.get("enrich_status") == "ok" for r in out)
    print(f"Wrote {args.out}: {ok}/{len(out)} enriched", file=sys.stderr)


def cmd_probe(args) -> None:
    rows = read_rows(args.inp)
    engine = ready_engines(args.engine)[0]
    extractor = worker_name()
    jobs = sorted({(r["buyer_question"], run) for r in rows
                   if r.get("buyer_question") and not r.get("probe_engine") for run in range(args.runs)})
    distinct = len({q for q, _ in jobs})
    print(f"Probing {len(rows)} leads on {ENGINE_LABEL[engine]}: {distinct} distinct questions x {args.runs} runs",
          file=sys.stderr)
    confirm_cost(len(jobs) * (1 if extractor == "local" else 2), 300, args.yes, "probing")

    def run(job):
        q, _ = job
        ok, text, _ = ask(engine, q)
        return job, (ok, text, extract_brands(text, extractor) if ok else [])

    with cf.ThreadPoolExecutor(args.workers) as pool:
        answers = dict(pool.map(run, jobs))

    def one(row):
        q = row.get("buyer_question", "")
        if not q or row.get("probe_engine"):
            return row
        results = [answers[(q, i)] for i in range(args.runs)]
        good = [(text, brands) for ok, text, brands in results if ok]
        if not good:
            return {**row, "probe_status": results[0][1][:120]}
        if any(brands is None for _, brands in good):
            return {**row, "probe_status": "couldn't read the names in the answer; re-run probe"}
        target = Target(pick(row, "company"), row.get("domain", ""))
        marks = [target.mention(text, brands) for text, brands in good]
        verdict = "yes" if "yes" in marks else "no" if all(m == "no" for m in marks) else "maybe"
        first_text, first_brands = good[0]
        others = [b for b in first_brands if not target.is_brand(b)]
        return {**row, "probe_status": "ok", "probe_engine": ENGINE_LABEL[engine], "probe_date": TODAY,
                "probe_runs": str(len(good)), "mentioned": verdict,
                "named_1": others[0] if others else "", "named_2": others[1] if len(others) > 1 else "",
                "named_3": others[2] if len(others) > 2 else "", "named_count": str(len(first_brands)),
                "probe_answer": " ".join(first_text.split())[:1500]}

    out = [one(r) for r in rows]
    write_rows(args.out, out)
    probed = [r for r in out if r.get("probe_status") == "ok"]
    c = Counter(r["mentioned"] for r in probed)
    print(f"Wrote {args.out}: {len(probed)} probed: {c['no']} not named, {c['yes']} named, "
          f"{c['maybe']} unclear (skipped later)", file=sys.stderr)


def first_line(row: dict) -> tuple[str, str]:
    """A plain sentence built only from probe data that was checked against the saved answer:
    every competitor named appears in that answer, and "didn't come up" is only written when the
    company was absent from every run. Read the probe_answer column before sending."""
    company = clean_company(pick(row, "company"))
    q = row.get("buyer_question", "").strip().rstrip("?")
    engine = row.get("probe_engine", "ChatGPT")
    named = [n for n in (row.get(f"named_{i}", "") for i in (1, 2, 3)) if n]
    if row.get("mentioned") == "no" and len(named) >= 2:
        listed = ", ".join(named[:-1]) + f" and {named[-1]}" if len(named) > 2 else " and ".join(named)
        return "not_named", f'I asked {engine} "{q}?" It named {listed}. {company} didn\'t come up.'
    if row.get("mentioned") == "yes":
        also = f", alongside {' and '.join(named[:2])}" if named else ""
        return "named", f'I asked {engine} "{q}?" {company} made the list{also}.'
    return "skip", ""


def cmd_firstline(args) -> None:
    rows = read_rows(args.inp)
    out, counts = [], Counter()
    for r in rows:
        if r.get("probe_status") != "ok":
            counts["skip"] += 1
            continue
        segment, line = first_line(r)
        counts[segment] += 1
        if segment == "skip":
            continue
        out.append({**r, "segment": segment, "first_line": line,
                    "first_name": pick(r, "first_name"), "email": pick(r, "email"),
                    "company": clean_company(pick(r, "company"))})
    write_rows(args.out, out or [{"segment": ""}])
    print(f"Wrote {args.out}: {counts['not_named']} not named (main sequence), {counts['named']} named "
          f"(defend sequence), {counts['skip']} skipped", file=sys.stderr)


# --------------------------------------------------------------------------- cli

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("snapshot", help="full visibility report for one company")
    s.add_argument("--brand", required=True)
    s.add_argument("--domain", required=True)
    s.add_argument("--aliases", help="other names to count, comma separated (e.g. 'Acme CRM,AcmeHQ')")
    s.add_argument("--questions", help="text file, one buyer question per line (default: generated from their site)")
    s.add_argument("--n", type=int, default=10, help="number of questions to generate (default 10)")
    s.add_argument("--region", help="for regional businesses, e.g. 'Denver, Colorado'")
    s.add_argument("--engines", help="comma list (default: every engine with a key)")
    s.add_argument("--runs", type=int, default=2, help="times to ask each question per engine (default 2; 3 for paid plans)")
    s.add_argument("--compare", help="previous raw.json, to show the change since last month")
    s.add_argument("--out", help="output folder (default business/data/reports/<brand>/<date>)")
    s.add_argument("--workers", type=int, default=6)
    s.add_argument("--yes", action="store_true", help="confirm runs over 200 paid API calls")
    s.add_argument("--pdf", action="store_true", help="also save report.pdf (needs playwright)")
    s.add_argument("--prepared-by", default="Rank and Reply", help="name on the report (white-label for agencies)")

    qp = sub.add_parser("questions", help="write the buyer questions for one company (cheap; edit before a paid run)")
    qp.add_argument("--brand", required=True)
    qp.add_argument("--domain", required=True)
    qp.add_argument("--n", type=int, default=40)
    qp.add_argument("--region")
    qp.add_argument("--out", help="file to write (default: print)")

    e = sub.add_parser("enrich", help="prospect CSV: read each website, write category + buyer question")
    e.add_argument("--in", dest="inp", required=True)
    e.add_argument("--out", required=True)
    e.add_argument("--ai", help="model to use (default: cheapest ready)")
    e.add_argument("--region")
    e.add_argument("--workers", type=int, default=4)
    e.add_argument("--yes", action="store_true", help="confirm over 300 paid calls")

    pr = sub.add_parser("probe", help="prospect CSV: ask each buyer question, record who gets named")
    pr.add_argument("--in", dest="inp", required=True)
    pr.add_argument("--out", required=True)
    pr.add_argument("--engine", default="chatgpt,perplexity,gemini,claude", help="first ready engine is used")
    pr.add_argument("--runs", type=int, default=2, help="'didn't come up' is only written if absent from every run")
    pr.add_argument("--workers", type=int, default=4)
    pr.add_argument("--yes", action="store_true", help="confirm over 300 paid calls")

    f = sub.add_parser("firstline", help="prospect CSV: write the opening line from the probe result")
    f.add_argument("--in", dest="inp", required=True)
    f.add_argument("--out", required=True)

    args = p.parse_args()
    {"snapshot": cmd_snapshot, "questions": cmd_questions, "enrich": cmd_enrich, "probe": cmd_probe,
     "firstline": cmd_firstline}[args.cmd](args)


if __name__ == "__main__":
    main()
