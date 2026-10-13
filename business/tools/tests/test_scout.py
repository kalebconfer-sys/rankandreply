"""Offline checks for scout.py, outbox.py and the weekly posts. Run through tests/run_all.py."""
import imaplib
import json
import os
import sys
from datetime import date
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import council as C  # noqa: E402
import scout as S  # noqa: E402

T = Path(os.environ["T"])
FIX = Path(__file__).resolve().parent / "fixtures"
S.DATA = T / "data"
S.SEEN = S.DATA / "scout_seen.json"
S.LOG = S.DATA / "scout_log.jsonl"


def ok(c, m):
    print(("PASS " if c else "FAIL ") + m)


class Args:
    days, eml_dir, recency, max_queries, n = 2, str(FIX / "eml"), "week", 1, 3


# ---- parsing alert emails
msgs = S.read_eml_dir(str(FIX / "eml"))
items = [i for m in msgs for i in S.items_from_message(m)]
by = {}
for i in items:
    by.setdefault(i["kind"], []).append(i)
ok({"reddit", "upwork", "hn", "x", "bluesky"} <= set(by), f"all platforms parsed: {sorted(by)}")
ok(len(by["upwork"]) == 2, "Upwork: tracking link and 'View job' button merged into one job")
geo = [i for i in by["upwork"] if "~021234567890abcdef1" in i["url"]][0]
ok(geo["url"] == "https://www.upwork.com/jobs/~021234567890abcdef1" and geo["title"].startswith("GEO audit") and "HR software" in geo["snippet"], "Upwork redirect unwrapped; title and snippet kept")
saas = [i for i in by["reddit"] if i["subreddit"] == "SaaS"][0]
ok(saas["title"].startswith("How do we get our SaaS") and "30-person" in saas["snippet"] and saas["source"] == "f5bot", "F5Bot Reddit thread parsed")
ok(by["hn"][0]["title"].startswith("Ask HN"), "Hacker News thread parsed")
ok(by["x"][0]["url"] == "https://x.com/founderjane/status/1845678901234567890" and by["x"][0]["source"] == "syften", "X link canonical, from Syften")
ok(not any("settings" in i["url"] for i in items), "settings links ignored")

# ---- the inbox is read-only
log = []


class FakeIMAP:
    def __init__(self, host): log.append(("host", host))
    def __enter__(self): return self
    def __exit__(self, *a): pass
    def login(self, u, p): log.append(("login", u))
    def select(self, folder, readonly=False): log.append(("select", folder, readonly)); return ("OK", [b"2"])
    def search(self, charset, *crit):
        log.append(("search", crit))
        return ("OK", [b"1"] if "upwork.com" in crit[1] else [b"2"])  # two senders match message 2
    def fetch(self, num, what):
        log.append(("fetch", num, what))
        f = "1-upwork.eml" if num == b"1" else "2-f5bot.eml"
        return ("OK", [(b"1 (BODY[] {n})", (FIX / "eml" / f).read_bytes()), b")"])


imaplib.IMAP4_SSL = FakeIMAP
os.environ.update(IMAP_USER="kaleb@example.com", IMAP_PASSWORD="app-pass")
got = S.read_imap(2)
ok(("select", "INBOX", True) in log, "inbox opened read-only")
ok(all(c[2] == "(BODY.PEEK[])" for c in log if c[0] == "fetch"), "fetch uses BODY.PEEK (nothing marked read)")
ok(any(c[0] == "search" and c[1][0] == "FROM" and "SINCE" in c[1] for c in log), "search limited by sender and date")
ok(len(got) == 2 and sum(c[0] == "fetch" for c in log) == 2, "each email fetched once even when two filters match")

# ---- reddit search through (stand-in) Perplexity
os.environ["PERPLEXITY_API_KEY"] = "test"
C.ENDPOINTS["perplexity"] = (os.environ["LOCAL_URL"], "PERPLEXITY_API_KEY", "sonar-pro")
r = S.search_reddit("AI overviews traffic", "week")
ok(len(r) == 1 and r[0]["subreddit"] == "marketing", "only threads the search really returned are kept")

# ---- full run: score, draft, page, dedupe
os.environ["ANTHROPIC_API_KEY"] = "test"
C.available = lambda: {"claude": "ready", "chatgpt": "missing", "gemini": "missing", "perplexity": "ready", "local": "ready"}
prompts = []


def fake_claude(prompt, system="", **kw):
    prompts.append(prompt)
    if kw.get("schema"):
        return json.dumps({"posts": [{"type": "data", "text": "Median: named in 5% of AI answers."},
                                     {"type": "how-to", "text": "Ask ChatGPT your buyer's question three times."},
                                     {"type": "question", "text": "People keep asking how LLMs pick vendors."}]})
    return "SKIP" if "Shopify" in prompt else "Here's what I'd check first... <b>bold</b>"


C.CALLERS["claude"] = fake_claude
C.call_claude = fake_claude
S.cmd_run(Args())
out = sorted((S.DATA / "outbox").glob("*/scout-*.txt"))
texts = [o.read_text(encoding="utf-8") for o in out]
ok(any("WHERE: r/SaaS" in t for t in texts) and any("WHERE: Upwork" in t for t in texts) and any("WHERE: X" in t for t in texts), f"drafts written: {[o.name for o in out]}")
ok(not any("pizza" in t for t in texts), "off-topic thread filtered out by scoring")
ok(not any("Shopify" in t for t in texts), "the writer's SKIP is respected")
ok(any("X blocks automated replies" in t for t in texts), "X items say to reply by hand")
ok(all("Never invent experience" in p for p in prompts if "Where: r/SaaS" in p), "community replies use the honest prompt")
page = next((S.DATA / "outbox").glob("*/today.html")).read_text(encoding="utf-8")
ok(page.count('class="btn copy"') == len(out) and "&lt;b&gt;bold&lt;/b&gt;" in page and "<b>bold</b>" not in page, "today.html: one Copy button per draft, drafts escaped")
n1 = len(out)
S.cmd_run(Args())
ok(len(list((S.DATA / "outbox").glob("*/scout-*.txt"))) == n1, "second run adds nothing already seen")

# ---- weekly posts never name a checked company
raw = json.loads((FIX / "report_raw.json").read_text(encoding="utf-8"))
raw["meta"]["date"] = date.today().isoformat()
dest = S.DATA / "reports" / "acme-dispatch" / date.today().isoformat()
dest.mkdir(parents=True, exist_ok=True)
(dest / "raw.json").write_text(json.dumps(raw), encoding="utf-8")
S.cmd_posts(Args())
posts = sorted((S.DATA / "outbox").glob("*/posts-*-linkedin.txt"))
ok(len(posts) == 3 and "WHEN: Monday" in posts[0].read_text(encoding="utf-8"), "3 LinkedIn posts with a schedule")
pp = [p for p in prompts if "LinkedIn posts" in p][0]
ok("Acme Dispatch" not in pp and "acmedispatch" not in pp, "the company you checked never reaches the posts prompt")
ok('"companies_checked": 1' in pp and "Jobber" in pp, "real anonymous numbers are passed in")
print("done")
