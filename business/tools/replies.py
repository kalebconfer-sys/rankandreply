"""Replies to the AI Visibility campaign, read from Instantly, sorted, and written up with the next step.
Read-only against Instantly; nothing is ever sent. Kaleb sends from the Unibox.

  python replies.py                 # new replies since the last run -> one file each in data/replies/
  python replies.py --dry-run       # same, writes nothing
  python replies.py --campaign ID   # another campaign (e.g. to test on an old one)

Needs INSTANTLY_CAMPAIGN and INSTANTLY_API_KEY (scope emails:read) in .env, or INSTANTLY_ENV pointing at a
file that has the key.
Buckets: SEND_IT (wants the report: T1 draft + the runbook commands), PRICE / WHAT / CALL (a question:
counts toward the kill bar, no approved draft yet), NO, BOUNCE (pause the campaign), AUTO (dropped).
"""
import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import council as C  # loads .env
from visibility import norm_domain

HERE = Path(__file__).resolve().parent
CAMPAIGN = os.getenv("INSTANTLY_CAMPAIGN", "")  # .env: the campaign to watch
API = "https://api.instantly.ai/api/v2/emails"
OUT = HERE.parent / "data" / "replies"
LEADS = sorted((HERE.parent / "leads").glob("*-instantly-upload.csv"))
try:
    ET = ZoneInfo("America/New_York")
except ZoneInfoNotFoundError:  # Windows Python has no tz database. US rule: 2nd Sunday of March to 1st Sunday of November.
    t = dt.date.today()
    dst = dt.date(t.year, 3, 8 + (6 - dt.date(t.year, 3, 8).weekday()) % 7) <= t < \
        dt.date(t.year, 11, 1 + (6 - dt.date(t.year, 11, 1).weekday()) % 7)
    ET = dt.timezone(dt.timedelta(hours=-4 if dst else -5), "ET")
POSITIVE = {"SEND_IT", "PRICE", "WHAT", "CALL"}  # decision 3: wants the check or asks a question
T1 = "Thanks {first_name}. Running it now; you'll have it by {when}.\n\nKaleb"

# First match wins: "no thanks" must beat "thanks", a phone number is a call whatever else it says.
RULES = (
    ("AUTO", re.compile(r"out of (?:the )?office|auto(?:matic)?[- ]repl|automated response|we have received your "
                        r"(?:e-?mail|message)|thank you for contacting|currently (?:away|unavailable)|on vacation|"
                        r"on (?:parental|maternity|paternity) leave|verify your email address|trusted sender|opt-inbox", re.I)),
    ("NO", re.compile(r"no,? thanks|no thank you|not interested|unsubscribe|remove me|take me off|\bstop\b|"
                      r"do(?:n'?t| not) (?:contact|email|message)|not (?:for us|right now|at this time)|^no\.?$", re.I | re.M)),
    ("CALL", re.compile(r"\(?\b\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b|call me|give me a call|hop on a call|"
                        r"what'?s your (?:number|phone)", re.I)),
    ("SEND_IT", re.compile(r"send (?:it|me|over|away|them)|\bsure\b|\byes\b|\byep\b|\byeah\b|\bok(?:ay)?\b|go ahead|"
                           r"sounds good|please do|interested|go for it|do it|show me|let'?s see|curious", re.I)),
    ("PRICE", re.compile(r"how much|what (?:does|would) (?:it|this) cost|\bcost\b|\bpric|\brate\b|\$\s?\d", re.I)),
    ("WHAT", re.compile(r"what (?:do|does|is) (?:you|this)|who are you|is this (?:a )?(?:bot|scam|real|spam|ai)|"
                        r"what (?:exactly|is it)|more info|how does (?:this|it) work", re.I)),
)
QUOTE = re.compile(r"^(?:On [^\n]{5,120}(?:\n[^\n]{0,40})?wrote:|-+ ?Original Message ?-+|From: .+|Sent from my |>)", re.M)
BOUNCE = re.compile(r"mailer-daemon|postmaster|undeliverable|delivery (?:status|failure)|mail delivery failed", re.I)


def body_text(item: dict) -> str:
    """Instantly's body is {"text": ..., "html": ...}; fall back to the preview."""
    b = item.get("body") or {}
    if isinstance(b, dict):
        b = b.get("text") or re.sub(r"<[^>]+>", " ", b.get("html") or "")
    return b or item.get("content_preview") or ""


def own_words(text: str) -> str:
    """What the person typed, above any quoted email."""
    text = (text or "").replace("\r\n", "\n")
    m = QUOTE.search(text)
    return text[: m.start() if m else len(text)].strip()


def classify(text: str, sender: str = "", subject: str = "") -> str:
    if BOUNCE.search(sender) or BOUNCE.search(subject):
        return "BOUNCE"
    if re.search(r"no-?reply|donotreply|notifications?@", sender, re.I):
        return "AUTO"
    words = re.sub(r"\bnot sure\b", "", own_words(text), flags=re.I)  # a hedge, not a yes
    return next((name for name, rx in RULES if rx.search(words)), "OTHER")


def when(now: dt.datetime) -> str:
    """D5: same business day if the reply lands before 2 PM ET, else noon the next business day."""
    if now.weekday() < 5 and now.hour < 14:
        return "end of day today"
    d = now + dt.timedelta(days=1)
    while d.weekday() >= 5:
        d += dt.timedelta(days=1)
    return "noon tomorrow" if (d - now).days == 1 else f"noon {d:%A}"


def api_key() -> str:
    if not os.getenv("INSTANTLY_API_KEY") and os.getenv("INSTANTLY_ENV"):
        C.load_env(Path(os.environ["INSTANTLY_ENV"]))
    key = os.getenv("INSTANTLY_API_KEY", "")
    if not key:
        sys.exit("INSTANTLY_API_KEY is empty: put it in .env, or set INSTANTLY_ENV to a file that has it")
    return key


def fetch(key: str, campaign: str, since: str) -> list[dict]:
    """Every received email for this campaign since `since`, oldest first."""
    out, after = [], None
    while True:
        params = {"email_type": "received", "campaign_id": campaign, "mode": "emode_all", "sort_order": "asc",
                  "min_timestamp_created": since, "limit": 100, **({"starting_after": after} if after else {})}
        req = urllib.request.Request(f"{API}?{urllib.parse.urlencode(params)}",
                                     headers={"Authorization": f"Bearer {key}", "User-Agent": "rankandreply-replies/1"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read())
        except urllib.error.HTTPError as e:
            sys.exit("Instantly rejected the API key (401): it needs the emails:read scope" if e.code == 401
                     else f"Instantly answered HTTP {e.code}")
        items = data.get("items") or []
        out += items
        after = data.get("next_starting_after")
        if not after or len(items) < 100:
            return out


def leads() -> dict[str, dict]:
    rows = {}
    for f in LEADS:
        with open(f, encoding="utf-8", newline="") as fh:
            rows.update({r["Email"].strip().lower(): r for r in csv.DictReader(fh) if r.get("Email")})
    return rows


def render(item: dict, bucket: str, lead: dict, now: dt.datetime) -> str:
    company = lead.get("company_name") or item.get("lead") or "Unknown"
    first = lead.get("first_name") or "there"
    domain = norm_domain(lead.get("Website", ""))
    slug = re.sub(r"[^a-z0-9]+", "-", company.lower()).strip("-")
    stamp = dt.datetime.fromisoformat(item["timestamp_created"].replace("Z", "+00:00")).astimezone(ET)
    lines = [f"# {company} replied: {bucket}", "",
             f"- From: {item.get('from_address_email', '?')} ({first})", f"- At: {stamp:%a %Y-%m-%d %I:%M %p} ET",
             f"- To our step {item.get('step', '?')}, subject: {item.get('subject', '')}", "",
             "## What they wrote", "", own_words(body_text(item)), ""]
    if bucket == "SEND_IT":
        lines += ["## Send now (T1, voted in panel step 10): reply in the same thread from the Unibox", "",
                  T1.format(first_name=first, when=when(now)), "",
                  "## Then the runbook (10-send-it/RUNBOOK.md, steps 1 and 3 to 7), filled in", "",
                  f'1. projects.json: positive reply {now:%Y-%m-%d}, {company}, {first}.',
                  f'3. python snapshot0.py questions --brand "{company}" --domain {domain} --n 10 --out q-{slug}.txt',
                  f'   line 1 = their Email 1 question: "{lead.get("first_line", "")}"',
                  f'5. python snapshot0.py snapshot --brand "{company}" --domain {domain} --aliases "<short name>" '
                  f'--questions q-{slug}.txt --claude claude-{slug}.json --runs 2 --out "<reports>/{slug}/{now:%Y-%m-%d}"',
                  "7. T2 with the PDF, no price.", ""]
    elif bucket == "BOUNCE":
        lines += ["## Next", "", "Hard bounce. Step 08 rule: pause the campaign (Kaleb's click) and check the address.", ""]
    elif bucket == "NO":
        lines += ["## Next", "", "Nothing to send. Instantly stops the sequence on any reply.", ""]
    elif bucket == "OTHER":
        lines += ["## Next", "", "Unsorted: read it and answer by hand. Log it as positive only if they want the check "
                  "or ask a question. No price until they have the report.", ""]
    else:
        lines += ["## Next", "", "A question: it counts toward the kill bar. No approved draft for this reply type yet "
                  "(panel step 11); answer by hand. The $490 Fix Plan is only quoted after they have the report.", ""]
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dry-run", action="store_true", help="sort and print, write nothing")
    p.add_argument("--campaign", default=CAMPAIGN)
    p.add_argument("--days", type=int, default=7, help="first run only: how many days back to read")
    a = p.parse_args()
    if not a.campaign:
        sys.exit("set INSTANTLY_CAMPAIGN in .env or pass --campaign")
    state_file = OUT / f"seen-{a.campaign[:8]}.json"
    state = json.loads(state_file.read_text(encoding="utf-8")) if state_file.exists() else {
        "seen": [], "since": (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=a.days)).strftime("%Y-%m-%dT%H:%M:%S.000Z")}
    now = dt.datetime.now(ET)
    book = leads()
    new = [i for i in fetch(api_key(), a.campaign, state["since"]) if i.get("id") not in state["seen"]]
    written = []
    for item in new:
        sender = (item.get("from_address_email") or "").lower()
        bucket = classify(body_text(item), sender, item.get("subject", ""))
        state["seen"].append(item["id"])
        state["since"] = max(state["since"], item.get("timestamp_created", state["since"]))
        if bucket == "AUTO":
            continue
        lead = book.get(sender) or book.get((item.get("lead") or "").lower(), {})
        company = lead.get("company_name") or item.get("lead") or "unknown"
        name = f"{now:%Y-%m-%d}-{re.sub(r'[^a-z0-9]+', '-', company.lower()).strip('-')}.md"
        print(f"{bucket:7} {OUT.name}/{name}")
        written.append(name)
        if a.dry_run:
            print(render(item, bucket, lead, now))
            continue
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / name).write_text(render(item, bucket, lead, now), encoding="utf-8")
        with open(OUT / "log.md", "a", encoding="utf-8") as log:
            log.write(f"- {now:%Y-%m-%d %H:%M} ET | {company} | {bucket} | {name} | NOT YET ANSWERED\n")
    if not a.dry_run:
        OUT.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps(state, indent=1), encoding="utf-8")
    log = (OUT / "log.md").read_text(encoding="utf-8") if (OUT / "log.md").exists() else ""
    positive = {l.split(" | ")[1] for l in log.splitlines() if len(l.split(" | ")) > 2 and l.split(" | ")[2] in POSITIVE}
    print(f"NEW REPLIES: {len(written)}" if written else f"no new replies ({len(new)} auto-replies dropped)" if new
          else "no new replies", f"| positive companies so far: {len(positive)} (kill bar: 2 of the first 50)")


if __name__ == "__main__":
    main()
