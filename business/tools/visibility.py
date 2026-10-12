#!/usr/bin/env python3
"""AI search visibility engine.

Asks ChatGPT, Gemini, Perplexity and Claude the questions a company's buyers ask,
then measures who gets recommended. The same engine produces the cold-email hook,
the free report that closes the sale, and the monthly client report.

Prospecting (one line per lead, cheap):
    python visibility.py enrich    --in apollo.csv        --out leads_1.csv
    python visibility.py probe     --in leads_1.csv       --out leads_2.csv
    python visibility.py firstline --in leads_2.csv       --out leads_ready.csv

Reports (one company, thorough):
    python visibility.py questions --brand "Acme" --domain acme.com --n 40 --out q.txt
    python visibility.py snapshot --brand "Acme" --domain acme.com
    python visibility.py snapshot --brand "Acme" --domain acme.com --questions q.txt --runs 3 --compare ../data/reports/acme/2026-10-12/raw.json

Everything is written under business/data/ (gitignored). Nothing is sent anywhere
except the AI APIs and a GET request to the company's own homepage.
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
import sys
import urllib.request
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

import council as C

DATA = C.HERE.parent / "data"
TODAY = dt.date.today().isoformat()

ENGINE_LABEL = {"chatgpt": "ChatGPT", "gemini": "Gemini", "perplexity": "Perplexity", "claude": "Claude"}


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
    body = {"contents": [{"role": "user", "parts": [{"text": q}]}], "tools": [{"google_search": {}}]}
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "x-goog-api-key": key})
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.load(resp)
    cand = (data.get("candidates") or [{}])[0]
    text = "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", []))
    chunks = cand.get("groundingMetadata", {}).get("groundingChunks", [])
    # Grounding URIs are redirect links; the title carries the real domain.
    urls = [c.get("web", {}).get("title", "") for c in chunks if c.get("web")]
    return text, urls


def ask_perplexity(q: str) -> tuple[str, list[str]]:
    text, resp = C._openai_compatible("https://api.perplexity.ai", "PERPLEXITY_API_KEY", C.PERPLEXITY_MODEL, q, "")
    extra = getattr(resp, "model_extra", None) or {}
    urls = extra.get("citations") or [r.get("url") for r in extra.get("search_results") or [] if r.get("url")]
    return text, urls


def ask_claude(q: str) -> tuple[str, list[str]]:
    text = C.call_claude(q, web=True, effort="medium")
    if text.startswith("[Claude declined"):
        raise RuntimeError(text)
    return text, []


def ask(engine: str, q: str) -> tuple[bool, str, list[str]]:
    """(ok, answer, source_urls). Never raises."""
    try:
        text, urls = ENGINES[engine](q)
        return bool(text.strip()), text, urls
    except Exception as ex:
        return False, f"{engine} {type(ex).__name__}: {ex}", []


ENGINES = {"chatgpt": ask_chatgpt, "gemini": ask_gemini, "perplexity": ask_perplexity, "claude": ask_claude}
ENGINE_KEYS = {"chatgpt": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY",
               "perplexity": "PERPLEXITY_API_KEY", "claude": "ANTHROPIC_API_KEY"}


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


def parse_json(text: str):
    """Lenient JSON parse for models that wrap JSON in prose or code fences."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    for open_, close in (("{", "}"), ("[", "]")):
        i, j = text.find(open_), text.rfind(close)
        if i != -1 and j > i:
            try:
                return json.loads(text[i:j + 1])
            except json.JSONDecodeError:
                continue
    return None


def ask_json(model: str, prompt: str, schema: dict):
    if model == "claude":
        try:
            return json.loads(C.call_claude(prompt, effort="low", schema=schema))
        except Exception as e:
            print(f"  claude json error: {e}", file=sys.stderr)
            return None
    out = C.safe_call(model, prompt + "\n\nReturn only JSON matching this schema, no other text:\n"
                      + json.dumps(schema), C.ROLE_BRIEF["Worker"])
    return parse_json(out)


BRANDS_SCHEMA = {
    "type": "object",
    "properties": {"brands": {"type": "array", "items": {"type": "string"}}},
    "required": ["brands"],
    "additionalProperties": False,
}


def extract_brands(answer: str, model: str) -> list[str]:
    if not answer.strip():
        return []
    data = ask_json(model, (
        "List every company, product or service provider that this answer recommends or names as an option, "
        "in the order they first appear. Use the name as written. Exclude publications, review sites and "
        "the AI itself unless they are recommended as the solution.\n\n<answer>\n" + answer[:12000] + "\n</answer>"
    ), BRANDS_SCHEMA)
    brands = (data or {}).get("brands", []) if isinstance(data, dict) else []
    return [b.strip() for b in brands if isinstance(b, str) and b.strip()][:25]


LEGAL_SUFFIX = re.compile(r"[,.]?\s+(inc|llc|l\.l\.c|ltd|limited|corp|corporation|co|company|gmbh|plc|pty|llp|lp|sa|bv)\.?$", re.I)


def clean_company(name: str) -> str:
    """'Acme Software, Inc.' -> 'Acme Software' so it matches how AI answers write it."""
    name = (name or "").strip()
    while LEGAL_SUFFIX.search(name):
        name = LEGAL_SUFFIX.sub("", name).strip()
    return name


def name_patterns(brand: str, aliases: list[str], domain: str) -> list[re.Pattern]:
    names = [clean_company(brand), *aliases]
    pats = [re.compile(r"(?<![\w-])" + re.escape(n) + r"(?![\w-])", re.I) for n in names if n]
    if domain:
        pats.append(re.compile(re.escape(domain.lower().removeprefix("www.")), re.I))
    return pats


def is_mentioned(text: str, pats: list[re.Pattern]) -> bool:
    return any(p.search(text) for p in pats)


def norm_domain(url: str) -> str:
    url = (url or "").strip().lower()
    url = re.sub(r"^https?://", "", url)
    return url.split("/")[0].removeprefix("www.")


# --------------------------------------------------------------------------- website reading

class _SiteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title, self.desc, self.heads, self.text = "", "", [], []
        self._in, self._skip = None, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style", "noscript", "svg"):
            self._skip += 1
        elif tag == "meta" and (a.get("name", "").lower() == "description" or a.get("property") == "og:description"):
            self.desc = self.desc or (a.get("content") or "")
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
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read(1_500_000).decode(r.headers.get_content_charset() or "utf-8", "replace")
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}
    p = _SiteParser()
    p.feed(raw)
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
    return ask_json(model, (
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

def run_matrix(questions: list[str], engines: list[str], runs: int, pats, domain: str, workers: int) -> list[dict]:
    jobs = [(q, e, r) for q in questions for e in engines for r in range(runs)]
    extractor = worker_name()

    def one(job):
        q, e, r = job
        ok, text, urls = ask(e, q)
        failed = not ok
        return {
            "question": q, "engine": e, "run": r, "answer": text, "sources": urls, "failed": failed,
            "mentioned": (not failed) and is_mentioned(text, pats),
            "cited": (not failed) and bool(domain) and any(domain in (u or "").lower() for u in urls),
            "brands": [] if failed else extract_brands(text, extractor),
        }

    out = []
    with cf.ThreadPoolExecutor(workers) as pool:
        for i, res in enumerate(pool.map(one, jobs), 1):
            out.append(res)
            if i % 10 == 0 or i == len(jobs):
                print(f"  {i}/{len(jobs)} answers", file=sys.stderr)
    return out


def aggregate(rows: list[dict], brand: str, pats) -> dict:
    ok = [r for r in rows if not r["failed"]]
    by_engine = {}
    for e in dict.fromkeys(r["engine"] for r in rows):
        er = [r for r in ok if r["engine"] == e]
        by_engine[e] = {"answers": len(er), "mentioned": sum(r["mentioned"] for r in er),
                        "rate": round(100 * sum(r["mentioned"] for r in er) / len(er)) if er else None}
    counts, display = Counter(), {}
    for r in ok:
        seen = set()
        for b in r["brands"]:
            key = b.casefold()
            if is_mentioned(b, pats):
                key, b = brand.casefold(), brand
            if key not in seen:
                seen.add(key)
                counts[key] += 1
                display.setdefault(key, b)
    top = [{"name": display[k], "answers": c, "share": round(100 * c / len(ok)) if ok else 0,
            "is_you": k == brand.casefold()} for k, c in counts.most_common(15)]
    questions = {}
    for r in ok:
        qd = questions.setdefault(r["question"], {})
        qd.setdefault(r["engine"], []).append(r["mentioned"])
    sources = Counter()
    for r in ok:
        for d in {norm_domain(u) for u in r["sources"] if u}:
            sources[d] += 1
    return {
        "top_sources": [{"domain": d, "answers": c} for d, c in sources.most_common(15) if d],
        "answers": len(ok), "failed": len(rows) - len(ok),
        "mentioned": sum(r["mentioned"] for r in ok),
        "rate": round(100 * sum(r["mentioned"] for r in ok) / len(ok)) if ok else 0,
        "by_engine": by_engine, "top_brands": top, "by_question": questions,
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


def write_findings(brand: str, site: dict, agg: dict, rows: list[dict]) -> dict:
    model = chair_name()
    sources = Counter(norm_domain(u) for r in rows for u in r["sources"] if u)
    sample = [{"q": r["question"], "engine": r["engine"], "named": r["brands"][:6]} for r in rows if not r["failed"]][:40]
    data = ask_json(model, (
        f"You are writing the findings section of an AI search visibility report for {brand}.\n"
        f"Their site: {json.dumps({k: site.get(k) for k in ('title', 'description', 'headings')})}\n"
        f"Results: {json.dumps({k: agg[k] for k in ('answers', 'mentioned', 'rate', 'by_engine', 'top_brands')})}\n"
        f"Sites the AI engines cited most: {json.dumps(sources.most_common(15))}\n"
        f"Sample of who was named per question: {json.dumps(sample)}\n\n"
        "Write: a one-sentence headline stating the finding plainly with the real numbers; a 3-4 sentence summary "
        "a busy founder will read; and the 5 highest-impact fixes. Each fix needs a title, why it matters (tie it to "
        "the data above, e.g. a cited site they are missing from, or a competitor strength), and how to do it in "
        "concrete steps. Fixes should be things like: comparison and alternatives pages, getting listed on the "
        "review sites and lists the engines cite, clear category and use-case wording on the homepage, FAQ "
        "content that answers the buyer questions, structured data. Never promise rankings. Plain English, no hype."
    ), FIXES_SCHEMA)
    return data or {"headline": f"{brand} was named in {agg['mentioned']} of {agg['answers']} AI answers.",
                    "summary": "", "fixes": []}


def render_html(brand: str, domain: str, meta: dict, agg: dict, findings: dict, compare: dict | None,
                prepared_by: str = "Rank and Reply") -> str:
    e = html.escape
    eng_rows = "".join(
        f"<tr><td>{e(ENGINE_LABEL.get(k, k))}</td><td>{v['mentioned']} / {v['answers']}</td>"
        f"<td><div class='bar'><span style='width:{v['rate'] or 0}%'></span></div></td><td>{str(v['rate']) + '%' if v['rate'] is not None else 'failed'}</td></tr>"
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
    src_block = ("<h2>Sites the AI engines cited most</h2><p>Being listed, reviewed or mentioned on these sites is often what gets a company named.</p>"
                 f"<table><tr><th>Site</th><th>Answers citing it</th></tr>{src_rows}</table>") if src_rows else ""
    fixes = "".join(f"<li><strong>{e(f['title'])}</strong><p>{e(f['why'])}</p><p class='how'>{e(f['how'])}</p></li>"
                    for f in findings.get("fixes", []))
    delta = ""
    if compare:
        d = agg["rate"] - compare.get("rate", 0)
        delta = (f"<p class='delta'>Last report ({e(compare.get('date', ''))}): {compare.get('rate', 0)}% "
                 f"&rarr; now {agg['rate']}% ({'+' if d >= 0 else ''}{d} points)</p>")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Visibility Report: {e(brand)}</title>
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
<span class="eyebrow">AI search visibility report · {e(meta['date'])}</span>
<h1>{e(brand)}</h1>
<p><strong>{e(findings.get('headline', ''))}</strong></p>
<p>{e(findings.get('summary', ''))}</p>
{delta}
<div class="kpi"><div><span class="big">{agg['rate']}%</span><small>of AI answers named {e(brand)}</small></div>
<div><span class="big">{agg['answers']}</span><small>answers checked across {answered} AI engine{'s' if answered != 1 else ''}</small></div>
<div><span class="big">{len(agg['by_question'])}</span><small>buyer questions asked</small></div></div>
<h2>By AI engine</h2><table><tr><th>Engine</th><th>Named you</th><th></th><th>Rate</th></tr>{eng_rows}</table>
<h2>Who the AI engines recommend instead</h2>
<p>Share of answers that named each company, across every engine and question.</p>
<table><tr><th>#</th><th>Company</th><th>Answers</th><th>Share</th></tr>{brand_rows}</table>
<h2>Question by question</h2><p>How many runs named {e(brand)}, per engine.</p>
<table><tr><th>Buyer question</th>{q_head}</tr>{q_rows}</table>
{src_block}
<h2>The five fixes that matter most</h2><ol class="fixes">{fixes}</ol>
<p class="method">Method: each question was put to each engine {meta['runs']} time(s) through its official API on {e(meta['date'])}, with web search on where the API offers it. AI answers vary between runs, users and locations, so these are sampled percentages, not fixed rankings. A company counts as named when its name or domain appears in the answer. {agg['failed']} request(s) failed and are excluded. Prepared by {e(prepared_by)}.</p>
</div></body></html>"""


def cmd_questions(args) -> None:
    site = fetch_site(norm_domain(args.domain))
    if not site.get("ok"):
        print(f"Warning: couldn't read the site: {site.get('error')}", file=sys.stderr)
    prof = profile_company(args.brand, site, args.n, chair_name(), args.region or "")
    if not prof:
        sys.exit("Couldn't generate questions.")
    text = "\n".join(prof["questions"][: args.n]) + "\n"
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text)
        print(f"Category: {prof['category']}\nBuyer: {prof['buyer']}\nCompetitors: {', '.join(prof['competitors'])}\nWrote {args.out}",
              file=sys.stderr)
    else:
        print(text, end="")


def cmd_snapshot(args) -> None:
    domain = norm_domain(args.domain)
    engines = ready_engines(args.engines)
    aliases = [a.strip() for a in (args.aliases or "").split(",") if a.strip()]
    pats = name_patterns(args.brand, aliases, domain)
    site = fetch_site(domain)
    if not site.get("ok"):
        print(f"Warning: couldn't read {domain}: {site.get('error')}", file=sys.stderr)

    if args.questions:
        questions = [l.strip() for l in Path(args.questions).read_text().splitlines() if l.strip()]
    else:
        prof = profile_company(args.brand, site, args.n, chair_name(), args.region or "")
        if not prof or not prof.get("questions"):
            sys.exit("Couldn't generate questions. Pass --questions with a text file, one question per line.")
        questions = prof["questions"][: args.n]

    calls = len(questions) * len(engines) * args.runs
    print(f"{len(questions)} questions x {len(engines)} engines ({', '.join(engines)}) x {args.runs} runs = {calls} answers",
          file=sys.stderr)
    if calls > 200 and not args.yes:
        sys.exit("That's over 200 paid API calls. Re-run with --yes to confirm, or lower --n / --runs.")

    rows = run_matrix(questions, engines, args.runs, pats, domain, args.workers)
    agg = aggregate(rows, args.brand, pats)
    findings = write_findings(args.brand, site, agg, rows)
    compare = json.loads(Path(args.compare).read_text())["summary"] if args.compare else None

    slug = re.sub(r"[^a-z0-9]+", "-", args.brand.lower()).strip("-")
    out = Path(args.out) if args.out else DATA / "reports" / slug / TODAY
    out.mkdir(parents=True, exist_ok=True)
    meta = {"brand": args.brand, "domain": domain, "date": TODAY, "runs": args.runs, "engines": engines}
    (out / "questions.txt").write_text("\n".join(questions) + "\n")
    (out / "raw.json").write_text(json.dumps({"meta": meta, "summary": {**agg, "date": TODAY}, "findings": findings,
                                              "rows": rows}, indent=2))
    html_path = out / "report.html"
    html_path.write_text(render_html(args.brand, domain, meta, agg, findings, compare, args.prepared_by))
    print(f"\n{findings.get('headline', '')}\nReport: {html_path}")
    if args.pdf:
        print(f"PDF: {to_pdf(html_path)}")


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


# --------------------------------------------------------------------------- prospect pipeline

ALIASES = {
    "company": ["company", "company name", "company_name", "organization", "organization name", "account name"],
    "website": ["website", "company website", "website url", "domain", "company domain", "url"],
    "first_name": ["first name", "first_name", "firstname"],
    "email": ["email", "email address", "work email"],
}


def pick(row: dict, field: str) -> str:
    low = {k.strip().lower(): v for k, v in row.items() if k}
    for a in ALIASES[field]:
        if low.get(a):
            return low[a].strip()
    return row.get(field, "").strip()


def read_rows(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_rows(path: str, rows: list[dict]) -> None:
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def cmd_enrich(args) -> None:
    rows = read_rows(args.inp)
    model = args.ai or worker_name()
    print(f"Enriching {len(rows)} leads with {model}", file=sys.stderr)
    todo = {}
    for row in rows:
        domain = norm_domain(pick(row, "website"))
        if domain and not row.get("buyer_question"):
            todo.setdefault(domain, clean_company(pick(row, "company")))

    def profile(item):
        domain, company = item
        site = fetch_site(domain)
        if not site.get("ok"):
            return domain, {"enrich_status": f"site error: {site.get('error', '')[:80]}"}
        prof = profile_company(company, site, 3, model, args.region or "")
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
        else:
            out.append({**row, **found[domain]})
    write_rows(args.out, out)
    ok = sum(r.get("enrich_status") == "ok" for r in out)
    print(f"Wrote {args.out}: {ok}/{len(out)} enriched", file=sys.stderr)


def cmd_probe(args) -> None:
    rows = read_rows(args.inp)
    engine = ready_engines(args.engine)[0]
    extractor = worker_name()
    print(f"Probing {len(rows)} leads on {ENGINE_LABEL[engine]}", file=sys.stderr)
    # Leads in the same category share a question, so each distinct question is asked once.
    questions = {r["buyer_question"] for r in rows if r.get("buyer_question") and not r.get("probe_engine")}

    def run(q):
        ok, text, _ = ask(engine, q)
        return q, (ok, text, extract_brands(text, extractor) if ok else [])

    with cf.ThreadPoolExecutor(args.workers) as pool:
        answers = dict(pool.map(run, questions))
    print(f"  asked {len(answers)} distinct questions", file=sys.stderr)

    def one(row):
        q = row.get("buyer_question", "")
        if not q or row.get("probe_engine"):
            return row
        ok, text, brands = answers[q]
        if not ok:
            return {**row, "probe_status": text[:120]}
        pats = name_patterns(pick(row, "company"), [], row.get("domain", ""))
        others = [b for b in brands if not is_mentioned(b, pats)]
        return {**row, "probe_status": "ok", "probe_engine": ENGINE_LABEL[engine], "probe_date": TODAY,
                "mentioned": "yes" if is_mentioned(text, pats) else "no",
                "named_1": others[0] if others else "", "named_2": others[1] if len(others) > 1 else "",
                "named_3": others[2] if len(others) > 2 else "", "named_count": str(len(brands))}

    out = [one(r) for r in rows]
    write_rows(args.out, out)
    probed = [r for r in out if r.get("probe_status") == "ok"]
    missing = sum(r["mentioned"] == "no" for r in probed)
    print(f"Wrote {args.out}: {len(probed)} probed, {missing} not named by {ENGINE_LABEL[engine]}", file=sys.stderr)


def first_line(row: dict) -> tuple[str, str]:
    """A plain, checkable sentence built only from the probe data. No model writes this,
    so it can't invent a fact about the prospect."""
    company = clean_company(pick(row, "company"))
    q = row.get("buyer_question", "").rstrip("?")
    engine = row.get("probe_engine", "ChatGPT")
    named = [row.get(f"named_{i}", "") for i in (1, 2, 3)]
    named = [n for n in named if n]
    if row.get("mentioned") == "no" and len(named) >= 2:
        listed = ", ".join(named[:-1]) + f" and {named[-1]}" if len(named) > 2 else " and ".join(named)
        return "not_named", f'I asked {engine} "{q}?" It recommended {listed}. {company} didn\'t come up.'
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
    write_rows(args.out, out)
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
    s.add_argument("--n", type=int, default=20, help="number of questions to generate (default 20)")
    s.add_argument("--region", help="for regional businesses, e.g. 'Denver, Colorado'")
    s.add_argument("--engines", help="comma list (default: every engine with a key)")
    s.add_argument("--runs", type=int, default=1, help="times to ask each question per engine (default 1; use 3 for paid reports)")
    s.add_argument("--compare", help="previous raw.json, to show the change since last month")
    s.add_argument("--out", help="output folder (default business/data/reports/<brand>/<date>)")
    s.add_argument("--workers", type=int, default=6)
    s.add_argument("--yes", action="store_true", help="confirm runs over 200 API calls")
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

    pr = sub.add_parser("probe", help="prospect CSV: ask each buyer question once, record who gets named")
    pr.add_argument("--in", dest="inp", required=True)
    pr.add_argument("--out", required=True)
    pr.add_argument("--engine", default="chatgpt,perplexity,gemini,claude", help="first ready engine is used")
    pr.add_argument("--workers", type=int, default=4)

    f = sub.add_parser("firstline", help="prospect CSV: write the opening line from the probe result")
    f.add_argument("--in", dest="inp", required=True)
    f.add_argument("--out", required=True)

    args = p.parse_args()
    {"snapshot": cmd_snapshot, "questions": cmd_questions, "enrich": cmd_enrich, "probe": cmd_probe, "firstline": cmd_firstline}[args.cmd](args)


if __name__ == "__main__":
    main()
