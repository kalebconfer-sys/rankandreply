#!/usr/bin/env python3
"""The AI council: Claude, ChatGPT, Gemini, Perplexity and a free local model
working one problem together.

Every AI is optional. The script uses whichever ones have keys set and skips the
rest, so it works with one AI on day one and all five once the keys are in.

    python council.py status
    python council.py ask      "Which of these three offers would you buy?"
    python council.py debate   "Pick our niche from business/01-research/market-research.md" --file business/01-research/market-research.md
    python council.py research "Upwork jobs posted this week asking for n8n lead-gen automations, with budgets"
    python council.py bulk --in leads.csv --prompt prompts/first_line.txt --out leads_out.csv --column first_line

Roles (see business/05-ai-team/roles.md):
    perplexity  Scout    live web research with citations (falls back to Claude + web search)
    claude      Chair    final decisions, writing, code; synthesizes the debate
    chatgpt     Critic   red-teams plans and copy, plays the skeptical buyer
    gemini      Analyst  cheap long-context work: big CSVs, many job posts at once
    local       Worker   free unlimited bulk: scoring leads, first lines, dedupe

Keys go in business/tools/.env (copy .env.example). Nothing here sends email or
posts anywhere: it only reads and writes local files.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import datetime as dt
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE.parent / "runs"


def load_env(path: Path) -> None:
    """Minimal .env loader so the only dependencies are the two SDKs."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


load_env(HERE / ".env")

# Model names change often. Override any of them in .env without touching code.
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-5-5")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
PERPLEXITY_MODEL = os.getenv("PERPLEXITY_MODEL", "sonar-pro")
LOCAL_MODEL = os.getenv("LOCAL_MODEL", "llama3.1:8b")
LOCAL_URL = os.getenv("LOCAL_URL", "http://localhost:11434/v1")  # Ollama; LM Studio is http://localhost:1234/v1

ROLES = {
    "perplexity": "Scout",
    "claude": "Chair",
    "chatgpt": "Critic",
    "gemini": "Analyst",
    "local": "Worker",
}

ROLE_BRIEF = {
    "Scout": "You find current, verifiable facts on the live web. Cite a URL for every claim. Say plainly when you cannot verify something.",
    "Chair": "You make the final call. Weigh evidence over enthusiasm, name the single biggest risk, and give concrete next actions.",
    "Critic": "You are the skeptical buyer and the investor who has seen 1,000 failed side businesses. Find the hole in the plan before the market does. Be specific, not contrarian for its own sake.",
    "Analyst": "You process large amounts of material and pull out patterns, counts and outliers. Show your numbers.",
    "Worker": "You do one small, well-defined task quickly and exactly as specified. No preamble.",
}


class Unavailable(Exception):
    pass


# --------------------------------------------------------------------------- providers

def _claude_client():
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise Unavailable("ANTHROPIC_API_KEY not set")
    import anthropic
    return anthropic.Anthropic()


def call_claude(prompt: str, system: str = "", web: bool = False, effort: str = "high") -> str:
    client = _claude_client()
    kwargs = dict(
        model=CLAUDE_MODEL,
        max_tokens=16000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",  # if a safety classifier declines, the API re-runs on a fallback model
        output_config={"effort": effort},
        messages=[{"role": "user", "content": prompt}],
    )
    if system:
        kwargs["system"] = system
    if web:
        kwargs["tools"] = [{"type": "web_search_20260209", "name": "web_search", "max_uses": 10}]

    text_parts: list[str] = []
    for _ in range(5):  # web search can pause a long turn; resume it a few times
        resp = client.beta.messages.create(**kwargs)
        if resp.stop_reason == "refusal":
            detail = resp.stop_details.explanation if resp.stop_details else ""
            return f"[Claude declined this request. {detail}]"
        for block in resp.content:
            if block.type == "text":
                text_parts.append(block.text)
        if resp.stop_reason != "pause_turn":
            break
        kwargs["messages"] = kwargs["messages"] + [{"role": "assistant", "content": resp.content}]
    return "".join(text_parts).strip()


def _openai_compatible(base_url: str | None, key_env: str | None, model: str, prompt: str, system: str) -> tuple[str, object]:
    from openai import OpenAI
    if key_env and not os.getenv(key_env):
        raise Unavailable(f"{key_env} not set")
    client = OpenAI(
        api_key=os.getenv(key_env) if key_env else "local",
        base_url=base_url,
        timeout=600,
    )
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    resp = client.chat.completions.create(model=model, messages=messages)
    return (resp.choices[0].message.content or "").strip(), resp


def call_chatgpt(prompt: str, system: str = "") -> str:
    return _openai_compatible(None, "OPENAI_API_KEY", OPENAI_MODEL, prompt, system)[0]


def call_gemini(prompt: str, system: str = "") -> str:
    return _openai_compatible(
        "https://generativelanguage.googleapis.com/v1beta/openai/", "GEMINI_API_KEY", GEMINI_MODEL, prompt, system
    )[0]


def call_perplexity(prompt: str, system: str = "") -> str:
    text, resp = _openai_compatible("https://api.perplexity.ai", "PERPLEXITY_API_KEY", PERPLEXITY_MODEL, prompt, system)
    extra = getattr(resp, "model_extra", None) or {}
    urls = extra.get("citations") or [r.get("url") for r in extra.get("search_results") or [] if r.get("url")]
    if urls:
        text += "\n\nSources:\n" + "\n".join(f"- {u}" for u in urls)
    return text


def call_local(prompt: str, system: str = "") -> str:
    import openai
    try:
        return _openai_compatible(LOCAL_URL, None, LOCAL_MODEL, prompt, system)[0]
    except openai.APIConnectionError as e:  # Ollama / LM Studio not running
        raise Unavailable(f"no local model server at {LOCAL_URL}") from e


def local_ready() -> str:
    if os.getenv("LOCAL_DISABLED") == "1":
        return "disabled (LOCAL_DISABLED=1)"
    import openai
    try:
        ids = [m.id for m in openai.OpenAI(api_key="local", base_url=LOCAL_URL, timeout=5).models.list()]
    except openai.APIConnectionError:
        return f"no local model server at {LOCAL_URL} (start Ollama)"
    except Exception as e:
        return f"error: {e}"
    if LOCAL_MODEL not in ids:
        return f"server up, but {LOCAL_MODEL} not pulled (run: ollama pull {LOCAL_MODEL})"
    return "ready"


CALLERS = {
    "claude": call_claude,
    "chatgpt": call_chatgpt,
    "gemini": call_gemini,
    "perplexity": call_perplexity,
    "local": call_local,
}


def available() -> dict[str, str]:
    """Which AIs can be called right now, and why the others can't."""
    status = {}
    checks = {
        "claude": "ANTHROPIC_API_KEY",
        "chatgpt": "OPENAI_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "perplexity": "PERPLEXITY_API_KEY",
    }
    for name, env in checks.items():
        status[name] = "ready" if os.getenv(env) else f"missing {env}"
    status["local"] = local_ready()
    return status


def ready_names(only: str | None) -> list[str]:
    stat = available()
    names = [n for n, s in stat.items() if s == "ready"]
    if only:
        wanted = [n.strip() for n in only.split(",")]
        names = [n for n in wanted if n in names]
    if not names:
        sys.exit("No AI is ready. Run `python council.py status` and add keys to business/tools/.env")
    return names


def safe_call(name: str, prompt: str, system: str = "") -> str:
    try:
        return CALLERS[name](prompt, system)
    except Unavailable as e:
        return f"[{name} unavailable: {e}]"
    except Exception as e:
        return f"[{name} error: {type(e).__name__}: {e}]"


def save_run(kind: str, body: str) -> Path:
    RUNS.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    path = RUNS / f"{stamp}-{kind}.md"
    path.write_text(body)
    return path


def with_file(question: str, file: str | None) -> str:
    if not file:
        return question
    return f"{question}\n\n<document path=\"{file}\">\n{Path(file).read_text()}\n</document>"


# --------------------------------------------------------------------------- commands

def cmd_status(_args) -> None:
    for name, state in available().items():
        model = {"claude": CLAUDE_MODEL, "chatgpt": OPENAI_MODEL, "gemini": GEMINI_MODEL,
                 "perplexity": PERPLEXITY_MODEL, "local": LOCAL_MODEL}[name]
        print(f"{name:<11} {ROLES[name]:<8} {model:<22} {state}")


def cmd_ask(args) -> None:
    prompt = with_file(args.question, args.file)
    names = ready_names(args.ai)
    with cf.ThreadPoolExecutor(len(names)) as pool:
        answers = dict(zip(names, pool.map(lambda n: safe_call(n, prompt, ROLE_BRIEF[ROLES[n]]), names)))
    out = [f"# Ask\n\n**Question:** {args.question}\n"]
    for n, a in answers.items():
        out.append(f"\n## {n} ({ROLES[n]})\n\n{a}\n")
    body = "".join(out)
    print(body)
    print(f"\nSaved: {save_run('ask', body)}")


def cmd_debate(args) -> None:
    """Round 1: everyone answers alone. Round 2: everyone reads the others and
    revises. Round 3: the Chair writes the decision, keeping real dissent."""
    prompt = with_file(args.question, args.file)
    names = ready_names(args.ai)

    with cf.ThreadPoolExecutor(len(names)) as pool:
        r1 = dict(zip(names, pool.map(lambda n: safe_call(n, prompt, ROLE_BRIEF[ROLES[n]]), names)))

    def revise(n: str) -> str:
        others = "\n\n".join(f"### {m} ({ROLES[m]})\n{a}" for m, a in r1.items() if m != n)
        p = (f"{prompt}\n\nYour first answer:\n{r1[n]}\n\nThe other AIs answered:\n{others}\n\n"
             "Revise your answer. Keep what holds up, drop what the others proved wrong, and state any point "
             "where you still disagree with them and why. Be concise.")
        return safe_call(n, p, ROLE_BRIEF[ROLES[n]])

    with cf.ThreadPoolExecutor(len(names)) as pool:
        r2 = dict(zip(names, pool.map(revise, names)))

    chair = "claude" if "claude" in names else names[0]
    transcript = "\n\n".join(f"### {n} ({ROLES[n]})\n{a}" for n, a in r2.items())
    decision = safe_call(chair, (
        f"{prompt}\n\nThe council's revised answers:\n{transcript}\n\n"
        "Write the decision: (1) the call, in one sentence; (2) the evidence it rests on; "
        "(3) unresolved disagreements and who holds them; (4) the three next actions, each with an owner "
        "(a named AI or the human) and a finish line; (5) the result that would prove this decision wrong."
    ), ROLE_BRIEF["Chair"])

    parts = [f"# Debate\n\n**Question:** {args.question}\n\n## Round 1\n"]
    parts += [f"\n### {n} ({ROLES[n]})\n{a}\n" for n, a in r1.items()]
    parts.append("\n## Round 2 (after reading each other)\n")
    parts += [f"\n### {n} ({ROLES[n]})\n{a}\n" for n, a in r2.items()]
    parts.append(f"\n## Decision ({chair})\n\n{decision}\n")
    body = "".join(parts)
    print(f"## Decision ({chair})\n\n{decision}")
    print(f"\nFull transcript: {save_run('debate', body)}")


def cmd_research(args) -> None:
    sys_msg = ROLE_BRIEF["Scout"]
    if os.getenv("PERPLEXITY_API_KEY"):
        who, answer = "perplexity", safe_call("perplexity", args.topic, sys_msg)
    elif os.getenv("ANTHROPIC_API_KEY"):
        who = "claude+web_search"
        try:
            answer = call_claude(args.topic, sys_msg, web=True)
        except Exception as e:
            answer = f"[claude error: {e}]"
    else:
        sys.exit("Research needs PERPLEXITY_API_KEY or ANTHROPIC_API_KEY in business/tools/.env")
    body = f"# Research ({who})\n\n**Topic:** {args.topic}\n\n{answer}\n"
    print(body)
    print(f"\nSaved: {save_run('research', body)}")


def cmd_bulk(args) -> None:
    """Fill one new column in a CSV by running a prompt template on every row.
    Template placeholders are column names in braces, e.g. {company} {website}.
    Re-running skips rows that already have a value, so it resumes after a crash."""
    template = Path(args.prompt).read_text()
    rows = list(csv.DictReader(open(args.inp, newline="", encoding="utf-8-sig")))
    if not rows:
        sys.exit("Input CSV is empty")
    order = [args.ai] if args.ai else ["local", "gemini", "claude", "chatgpt"]
    stat = available()
    worker = next((n for n in order if stat.get(n) == "ready"), None)
    if not worker:
        sys.exit("No worker AI ready for bulk. Start Ollama or add a key.")
    print(f"Bulk worker: {worker} ({len(rows)} rows)")

    out_path = Path(args.out)
    if out_path.exists():  # resume
        done = {i: r for i, r in enumerate(csv.DictReader(open(out_path, newline="", encoding="utf-8")))}
        for i, r in done.items():
            if i < len(rows) and r.get(args.column):
                rows[i][args.column] = r[args.column]

    todo = [i for i, r in enumerate(rows) if not r.get(args.column)]

    def run(i: int) -> tuple[int, str]:
        filled = template.format_map(defaultdict(str, rows[i]))
        return i, safe_call(worker, filled, ROLE_BRIEF["Worker"])

    fields = list(rows[0].keys()) + ([args.column] if args.column not in rows[0] else [])
    with cf.ThreadPoolExecutor(args.workers) as pool:
        for n, (i, val) in enumerate(pool.map(run, todo), 1):
            rows[i][args.column] = val
            if n % 10 == 0 or n == len(todo):
                with open(out_path, "w", newline="", encoding="utf-8") as f:
                    w = csv.DictWriter(f, fieldnames=fields)
                    w.writeheader()
                    w.writerows(rows)
                print(f"  {n}/{len(todo)}")
    print(f"Wrote {out_path}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="show which AIs are connected")

    a = sub.add_parser("ask", help="same question to every AI, answers side by side")
    a.add_argument("question")
    a.add_argument("--file", help="attach a text/markdown file as context")
    a.add_argument("--ai", help="comma list to limit, e.g. claude,chatgpt")

    d = sub.add_parser("debate", help="answer, cross-critique, then a written decision")
    d.add_argument("question")
    d.add_argument("--file")
    d.add_argument("--ai")

    r = sub.add_parser("research", help="live web research with citations")
    r.add_argument("topic")

    b = sub.add_parser("bulk", help="run a prompt template over every row of a CSV")
    b.add_argument("--in", dest="inp", required=True)
    b.add_argument("--prompt", required=True, help="template file with {column} placeholders")
    b.add_argument("--out", required=True)
    b.add_argument("--column", required=True, help="name of the new column to fill")
    b.add_argument("--ai", help="force a worker (default: local, then gemini, claude, chatgpt)")
    b.add_argument("--workers", type=int, default=4)

    args = p.parse_args()
    {"status": cmd_status, "ask": cmd_ask, "debate": cmd_debate, "research": cmd_research, "bulk": cmd_bulk}[args.cmd](args)


if __name__ == "__main__":
    main()
