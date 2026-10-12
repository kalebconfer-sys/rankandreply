#!/usr/bin/env python3
"""Autopilot: the daily routine in two commands.

    python autopilot.py leads   --in ../data/leads/2026-10-27-apollo.csv [--region "Ohio"]
        enrich -> probe -> firstline, written next to the input as *-ready.csv

    python autopilot.py replies --in ../data/replies/2026-10-28.csv
        tags every reply, drafts an answer, runs the free report for every "yes",
        and writes ready-to-send emails into business/data/outbox/<date>/

Nothing is sent. You read the outbox, then paste or forward each email from the
inbox the lead replied to. That approval step stays until a sequence has run
clean for two weeks (see business/05-ai-team/roles.md).

Reply CSV columns (names are matched loosely): email, first_name, company,
website or domain, reply_text.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from argparse import Namespace
from collections import Counter, defaultdict
from pathlib import Path

import council as C
import visibility as V

PROMPTS = C.HERE / "prompts"
LABELS = {"yes", "question", "price", "wants_call", "has_agency", "not_now", "no", "ooo", "other"}
# "unsorted" means the model call failed: a person reads that reply.
REPLY_ALIASES = ["reply_text", "reply text", "reply", "body", "message", "reply body", "last reply"]


def reply_text(row: dict) -> str:
    low = {k.strip().lower(): v for k, v in row.items() if k}
    return next((low[a] for a in REPLY_ALIASES if low.get(a)), "")


def fill(template: str, values: dict) -> str:
    return template.format_map(defaultdict(str, values))


# --------------------------------------------------------------------------- leads

def cmd_leads(args) -> None:
    src = Path(args.inp)
    stem = src.with_suffix("")
    step1, step2, ready = f"{stem}-1-enriched.csv", f"{stem}-2-probed.csv", f"{stem}-ready.csv"
    V.cmd_enrich(Namespace(inp=str(src), out=step1, ai=None, region=args.region, workers=args.workers, yes=args.yes))
    V.cmd_probe(Namespace(inp=step1, out=step2, engine=args.engine, runs=args.runs, workers=args.workers, yes=args.yes))
    V.cmd_firstline(Namespace(inp=step2, out=ready))
    print(f"\nNext: open {ready}. For 20 rows, read first_line next to probe_answer (the AI's actual answer) "
          "and delete anything that doesn't match. Then upload to Instantly.")


# --------------------------------------------------------------------------- replies

TEMPLATE_A = """Hi {first_name},

Here's the report for {company} (PDF attached).

The short version:
- {company} was named in {mentioned} of {answers} answers ({rate}%).
- {top_competitor} was named in {top_share}% of them.
- The biggest gap: {fix_1}.

If you'd like to fix it yourself, the five fixes at the end are where to start. If you'd rather we did it:
- Fix Plan, $490 once: the full 480-answer audit, the sites the engines cite, a 30-day roadmap and two pages written for you, in 5 business days. Credited to your first Retainer month if you continue within 30 days. {fixplan_link}
- Retainer, $1,500/month, month-to-month. {retainer_link}

Everything is at rankandreply.com/ai-visibility. Questions? Just reply. No call needed.

Kaleb"""


def classify(row: dict, model: str) -> str:
    prompt = fill((PROMPTS / "classify_reply.txt").read_text(),
                  {**row, "reply_text": reply_text(row), "first_name": V.pick(row, "first_name"),
                   "company": V.clean_company(V.pick(row, "company"))})
    try:
        out = C.strict_call(model, prompt, C.ROLE_BRIEF["Worker"]).strip().lower()
    except Exception as ex:
        print(f"  couldn't classify a reply ({type(ex).__name__}); marked unsorted", file=sys.stderr)
        return "unsorted"
    word = re.findall(r"[a-z_]+", out)
    return next((w for w in word if w in LABELS), "other")


def draft(row: dict, label: str, model: str) -> str:
    if label == "ooo":
        return ""
    prompt = fill((PROMPTS / "draft_reply.txt").read_text(),
                  {"reply_text": reply_text(row), "label": label, "first_name": V.pick(row, "first_name")})
    try:
        return C.strict_call(model, prompt, C.ROLE_BRIEF["Chair"]).strip()
    except Exception as ex:
        return f"[Draft failed ({type(ex).__name__}). Write this reply by hand.]"


def report_email(row: dict, report_dir: Path) -> str:
    data = json.loads((report_dir / "raw.json").read_text())
    s, f = data["summary"], data.get("findings", {})
    brand = data["meta"]["brand"]
    others = [b for b in s["top_brands"] if not b["is_you"] and b["answers"]]
    top = others[0] if others else {"name": "No single competitor", "share": 0}
    fixes = f.get("fixes") or [{"title": "see the fixes at the end of the report"}]
    return fill(TEMPLATE_A, {
        "first_name": V.pick(row, "first_name") or "there", "company": brand,
        "mentioned": s["mentioned"], "answers": s["answers"], "rate": s["rate"],
        "top_competitor": top["name"], "top_share": top["share"], "fix_1": fixes[0]["title"],
        "fixplan_link": os.getenv("STRIPE_FIXPLAN_LINK", "[Fix Plan Stripe link]"),
        "retainer_link": os.getenv("STRIPE_RETAINER_LINK", "[Retainer Stripe link]"),
    })


def cmd_replies(args) -> None:
    rows = V.read_rows(args.inp)
    worker, chair = V.worker_name(), V.chair_name()
    outbox = V.DATA / "outbox" / V.TODAY
    outbox.mkdir(parents=True, exist_ok=True)
    counts, suppress, summary = Counter(), [], []

    for i, row in enumerate(rows, 1):
        email = V.pick(row, "email")
        company = V.clean_company(V.pick(row, "company"))
        if not reply_text(row).strip():
            continue
        label = classify(row, worker)
        counts[label] += 1
        attach, body = "", ""

        if label == "yes":
            domain = V.norm_domain(V.pick(row, "website"))
            if not (company and domain):
                body = "[Needs company + website to run the report. Add them to the CSV row and re-run.]"
            else:
                slug = re.sub(r"[^a-z0-9]+", "-", company.lower()).strip("-")
                rdir = V.DATA / "reports" / slug / V.TODAY
                if not (rdir / "raw.json").exists():
                    print(f"[{i}/{len(rows)}] report for {company}...", file=sys.stderr)
                    try:
                        V.cmd_snapshot(Namespace(
                            brand=company, domain=domain, aliases=None, questions=None, n=10, region=args.region,
                            engines=None, runs=2, compare=None, out=str(rdir), workers=6, yes=False, pdf=True,
                            prepared_by="Rank and Reply"))
                    except SystemExit as ex:  # snapshot exits on unrecoverable problems; keep going with the rest
                        print(f"  report failed for {company}: {ex}", file=sys.stderr)
                if (rdir / "raw.json").exists():
                    body = report_email(row, rdir)
                    pdf = rdir / "report.pdf"
                    attach = str(pdf if pdf.exists() else rdir / "report.html")
                else:
                    body = f"[Report for {company} failed. Run visibility.py snapshot by hand, then send template A.]"
        elif label == "no":
            suppress.append(email)
            body = "Done, sorry for the bother.\n\nKaleb"  # fixed text: nothing to get wrong
        elif label == "unsorted":
            body = "[Couldn't classify this reply. Read it and answer by hand.]"
        else:
            body = draft(row, label, chair)

        name = f"{i:03d}-{label}-{re.sub(r'[^a-z0-9]+', '-', (email or company or 'lead').lower())}.txt"
        if body:
            (outbox / name).write_text(
                f"TO: {email}\nRE: (reply in the same thread)\nATTACH: {attach or '-'}\nLABEL: {label}\n\n{body}\n"
                f"\n----- their reply -----\n{reply_text(row)}\n", encoding="utf-8")
        summary.append({"email": email, "company": company, "label": label, "file": name if body else "", "attach": attach})

    V.write_rows(str(outbox / "summary.csv"), summary or [{"email": "", "label": ""}])
    if suppress:
        with open(V.DATA / "suppression.txt", "a", encoding="utf-8") as f:
            f.write("\n".join(e for e in suppress if e) + "\n")
    print(f"\n{dict(counts)}\nOutbox: {outbox}")
    if suppress:
        print(f"Added {len(suppress)} to business/data/suppression.txt. Also add them to Instantly's blocklist now.")
    if counts["wants_call"]:
        print(f"{counts['wants_call']} want a call: these are your near-certain buyers. Answer them first.")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    lp = sub.add_parser("leads", help="Apollo export -> ready-to-upload CSV")
    lp.add_argument("--in", dest="inp", required=True)
    lp.add_argument("--region")
    lp.add_argument("--engine", default="chatgpt,perplexity,gemini,claude")
    lp.add_argument("--runs", type=int, default=2)
    lp.add_argument("--workers", type=int, default=4)
    lp.add_argument("--yes", action="store_true", help="confirm batches over 300 paid calls")
    rp = sub.add_parser("replies", help="replies CSV -> tagged, drafted, reports run, outbox written")
    rp.add_argument("--in", dest="inp", required=True)
    rp.add_argument("--region")
    args = p.parse_args()
    {"leads": cmd_leads, "replies": cmd_replies}[args.cmd](args)


if __name__ == "__main__":
    main()
