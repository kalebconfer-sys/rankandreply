#!/usr/bin/env python3
"""The AI council: Claude, ChatGPT, Gemini, Perplexity and a free local model
working one problem together.

Every AI is optional. The script uses whichever ones have keys set and skips the
rest, so it works with one AI on day one and all five once the keys are in.

    python council.py status
    python council.py ask      "Which of these three offers would you buy?"
    python council.py debate   "Pick our niche" --file ../01-research/market-research.md --file ../03-offer/offer.md
    python council.py research "Upwork jobs posted this week asking for GEO or AEO work, with budgets"
    python council.py bulk --in replies.csv --prompt prompts/classify_reply.txt --out tagged.csv --column label

Roles (see business/05-ai-team/roles.md):
    perplexity  Scout    live web research with citations (falls back to Claude + web search)
    claude      Chair    final decisions, writing, code; synthesizes the debate
    chatgpt     Critic   red-teams plans and copy, plays the skeptical buyer
    gemini      Analyst  cheap long-context work: big CSVs, many job posts at once
    local       Worker   free unlimited bulk: scoring leads, tagging replies

Keys go in business/tools/.env (copy .env.example). Nothing here sends email or
posts anywhere: it only reads and writes local files.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import datetime as dt
import json
import os
import string
import sys
from collections import defaultdict
from pathlib import Path

# Windows consoles default to cp1252; never crash on an em dash or arrow.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
RUNS = HERE.parent / "runs"


def load_env(path: Path) -> None:
    """Minimal .env loader so the only dependencies are the two SDKs."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


load_env(HERE / ".env")

# Model names change often. Override any of them in .env without touching code.
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-5-5")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")  # 2.5-flash is retired (404) for new keys
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


class Declined(Exception):
    """Claude's safety classifier declined and the fallback model did too."""


# --------------------------------------------------------------------------- providers

def _claude_client():
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise Unavailable("ANTHROPIC_API_KEY not set")
    import anthropic
    return anthropic.Anthropic()


def call_claude(prompt: str, system: str = "", web: bool = False, effort: str = "high",
                schema: dict | None = None, sources: list | None = None,
                web_domains: list[str] | None = None) -> str:
    """schema: a JSON Schema; when given, the reply is guaranteed to be valid JSON text.
    sources: pass a list to collect the URLs web search returned.
    web_domains: limit web search to these sites (e.g. ["reddit.com"])."""
    client = _claude_client()
    output_config = {"effort": effort}
    if schema:
        output_config["format"] = {"type": "json_schema", "schema": schema}
    kwargs = dict(
        model=CLAUDE_MODEL,
        max_tokens=16000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",  # if a safety classifier declines, the API re-runs on a fallback model
        output_config=output_config,
        messages=[{"role": "user", "content": prompt}],
    )
    if system:
        kwargs["system"] = system
    if web:
        tool = {"type": "web_search_20260209", "name": "web_search", "max_uses": 10}
        if web_domains:
            tool["allowed_domains"] = web_domains
        kwargs["tools"] = [tool]

    text_parts: list[str] = []
    for _ in range(5):  # web search can pause a long turn; resume it a few times
        resp = client.beta.messages.create(**kwargs)
        if resp.stop_reason == "refusal":
            detail = resp.stop_details.explanation if resp.stop_details else ""
            raise Declined(detail or "declined")
        for block in resp.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "web_search_tool_result" and sources is not None:
                results = getattr(block, "content", None)
                if isinstance(results, list):  # an error comes back as a single object
                    sources.extend(r.url for r in results if getattr(r, "url", None))
        if resp.stop_reason != "pause_turn":
            break
        kwargs["messages"] = kwargs["messages"] + [{"role": "assistant", "content": resp.content}]
    return "".join(text_parts).strip()


def _openai_compatible(base_url: str | None, key_env: str | None, model: str, prompt: str, system: str,
                       response_format: dict | None = None, extra_body: dict | None = None) -> tuple[str, object]:
    from openai import OpenAI
    if key_env and not os.getenv(key_env):
        raise Unavailable(f"{key_env} not set")
    client = OpenAI(
        api_key=os.getenv(key_env) if key_env else "local",
        base_url=base_url,
        timeout=600,
    )
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    extra = {"response_format": response_format} if response_format else {}
    if extra_body:  # provider-specific options, e.g. Perplexity's search_domain_filter
        extra["extra_body"] = extra_body
    resp = client.chat.completions.create(model=model, messages=messages, **extra)
    return (resp.choices[0].message.content or "").strip(), resp


ENDPOINTS = {  # name -> (base_url, key env var, model)
    "chatgpt": (None, "OPENAI_API_KEY", OPENAI_MODEL),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai/", "GEMINI_API_KEY", GEMINI_MODEL),
    "perplexity": ("https://api.perplexity.ai", "PERPLEXITY_API_KEY", PERPLEXITY_MODEL),
    "local": (LOCAL_URL, None, LOCAL_MODEL),
}


def call_chatgpt(prompt: str, system: str = "") -> str:
    return _openai_compatible(*ENDPOINTS["chatgpt"], prompt, system)[0]


def call_gemini(prompt: str, system: str = "") -> str:
    return _openai_compatible(*ENDPOINTS["gemini"], prompt, system)[0]


def call_perplexity(prompt: str, system: str = "") -> str:
    text, resp = _openai_compatible(*ENDPOINTS["perplexity"], prompt, system)
    extra = getattr(resp, "model_extra", None) or {}
    urls = extra.get("citations") or [r.get("url") for r in extra.get("search_results") or [] if r.get("url")]
    if urls:
        text += "\n\nSources:\n" + "\n".join(f"- {u}" for u in urls)
    return text


def call_local(prompt: str, system: str = "") -> str:
    import openai
    try:
        return _openai_compatible(*ENDPOINTS["local"], prompt, system)[0]
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


def strict_call(name: str, prompt: str, system: str = "") -> str:
    """Call one AI. Raises on any failure, so callers never mistake an error for an answer."""
    return CALLERS[name](prompt, system)


def safe_call(name: str, prompt: str, system: str = "") -> str:
    """For human-read output (ask, debate): failures become a visible bracketed note."""
    try:
        return strict_call(name, prompt, system)
    except Unavailable as e:
        return f"[{name} unavailable: {e}]"
    except Declined as e:
        return f"[{name} declined: {e}]"
    except Exception as e:
        return f"[{name} error: {type(e).__name__}: {e}]"


# --------------------------------------------------------------------------- structured output

def conforms(data, schema: dict) -> bool:
    """Small JSON Schema check covering what our schemas use: object, array, string, required."""
    t = schema.get("type")
    if t == "object":
        if not isinstance(data, dict):
            return False
        props = schema.get("properties", {})
        if any(k not in data for k in schema.get("required", [])):
            return False
        return all(conforms(data[k], props[k]) for k in props if k in data)
    if t == "array":
        return isinstance(data, list) and all(conforms(x, schema.get("items", {})) for x in data)
    if t == "string":
        return isinstance(data, str)
    return True


def parse_json(text: str):
    """Lenient JSON parse for models that wrap JSON in prose or code fences."""
    text = (text or "").strip()
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


def call_json(name: str, prompt: str, schema: dict, system: str = ""):
    """Structured output from any AI. Returns data matching the schema, or None. Never raises."""
    try:
        if name == "claude":
            data = json.loads(call_claude(prompt, system, effort="low", schema=schema))
        else:
            base, key, model = ENDPOINTS[name]
            fmt = {"type": "json_schema", "json_schema": {"name": "output", "schema": schema, "strict": True}}
            try:
                text, _ = _openai_compatible(base, key, model, prompt, system, response_format=fmt)
            except Exception as e:
                import openai
                if not isinstance(e, openai.BadRequestError):
                    raise
                # Endpoint doesn't support schemas: ask in words instead.
                text, _ = _openai_compatible(base, key, model, prompt + "\n\nReturn only JSON matching this schema:\n"
                                             + json.dumps(schema), system)
            data = parse_json(text)
    except Exception as e:
        print(f"  {name} json error: {type(e).__name__}: {e}", file=sys.stderr)
        return None
    return data if conforms(data, schema) else None


# --------------------------------------------------------------------------- files

def save_run(kind: str, body: str) -> Path:
    RUNS.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    path = RUNS / f"{stamp}-{kind}.md"
    path.write_text(body, encoding="utf-8")
    return path


def with_file(question: str, files: list[str] | None) -> str:
    for f in files or []:
        question += f"\n\n<document path=\"{f}\">\n{Path(f).read_text(encoding='utf-8-sig', errors='replace')}\n</document>"
    return question


def template_fields(template: str) -> set[str]:
    return {f for _, f, _, _ in string.Formatter().parse(template) if f}


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
    path = save_run("ask", body)
    print(body)
    print(f"\nSaved: {path}")


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
    path = save_run("debate", "".join(parts))  # save first, so nothing is lost if printing fails
    print(f"## Decision ({chair})\n\n{decision}")
    print(f"\nFull transcript: {path}")


def cmd_research(args) -> None:
    sys_msg = ROLE_BRIEF["Scout"]
    if os.getenv("PERPLEXITY_API_KEY"):
        who, answer = "perplexity", safe_call("perplexity", args.topic, sys_msg)
    elif os.getenv("ANTHROPIC_API_KEY"):
        who = "claude+web_search"
        urls: list[str] = []
        try:
            answer = call_claude(args.topic, sys_msg, web=True, sources=urls)
            if urls:
                answer += "\n\nSources:\n" + "\n".join(f"- {u}" for u in dict.fromkeys(urls))
        except Exception as e:
            answer = f"[claude error: {e}]"
    else:
        sys.exit("Research needs PERPLEXITY_API_KEY or ANTHROPIC_API_KEY in business/tools/.env")
    body = f"# Research ({who})\n\n**Topic:** {args.topic}\n\n{answer}\n"
    path = save_run("research", body)
    print(body)
    print(f"\nSaved: {path}")


def cmd_bulk(args) -> None:
    """Fill one new column in a CSV by running a prompt template on every row.
    Template placeholders are column names in braces, e.g. {company} {website}.
    Re-running the same input resumes: a row keeps its stored value only if every
    input column is identical, and rows that failed are retried."""
    template = Path(args.prompt).read_text(encoding="utf-8")
    with open(args.inp, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        sys.exit("Input CSV is empty")
    inputs = [k for k in rows[0] if k and k != args.column]
    missing = sorted(template_fields(template) - set(inputs))
    if missing:
        sys.exit(f"The prompt uses {{{'}, {'.join(missing)}}} but the CSV has no such column(s).\n"
                 f"CSV columns: {', '.join(inputs)}\nRename the CSV columns to match, then re-run.")

    order = [args.ai] if args.ai else ["local", "gemini", "claude", "chatgpt"]
    stat = available()
    worker = next((n for n in order if stat.get(n) == "ready"), None)
    if not worker:
        sys.exit(f"No worker AI ready for bulk ({', '.join(order)}). Run `python council.py status`.")
    print(f"Bulk worker: {worker} ({len(rows)} rows)")

    def key(r: dict) -> tuple:
        return tuple((k, r.get(k) or "") for k in inputs)

    out_path = Path(args.out)
    if out_path.exists():
        with open(out_path, newline="", encoding="utf-8-sig") as f:
            stored = {key(r): r.get(args.column) for r in csv.DictReader(f) if r.get(args.column)}
        for r in rows:
            r[args.column] = stored.get(key(r), "")

    todo = [i for i, r in enumerate(rows) if not r.get(args.column)]
    failures: list[str] = []

    def run(i: int) -> tuple[int, str]:
        filled = template.format_map(defaultdict(str, {k: v or "" for k, v in rows[i].items()}))
        try:
            return i, strict_call(worker, filled, ROLE_BRIEF["Worker"]).strip()
        except Exception as e:
            failures.append(f"row {i + 2}: {type(e).__name__}: {e}")
            return i, ""  # left empty, so the next run retries it

    fields = inputs + [args.column]

    def save() -> None:
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)

    with cf.ThreadPoolExecutor(args.workers) as pool:
        for n, (i, val) in enumerate(pool.map(run, todo), 1):
            rows[i][args.column] = val
            if n % 10 == 0 or n == len(todo):
                save()
                print(f"  {n}/{len(todo)}")
    save()
    print(f"Wrote {out_path}")
    if failures:
        print(f"{len(failures)} row(s) failed and were left empty. Re-run the same command to retry them:",
              *failures[:5], sep="\n  ")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="show which AIs are connected")

    a = sub.add_parser("ask", help="same question to every AI, answers side by side")
    a.add_argument("question")
    a.add_argument("--file", action="append", help="attach a text/markdown file (repeat for several)")
    a.add_argument("--ai", help="comma list to limit, e.g. claude,chatgpt")

    d = sub.add_parser("debate", help="answer, cross-critique, then a written decision")
    d.add_argument("question")
    d.add_argument("--file", action="append", help="attach a file (repeat for several)")
    d.add_argument("--ai")

    r = sub.add_parser("research", help="live web research with citations")
    r.add_argument("topic")

    b = sub.add_parser("bulk", help="run a prompt template over every row of a CSV")
    b.add_argument("--in", dest="inp", required=True)
    b.add_argument("--prompt", required=True, help="template file with {column} placeholders")
    b.add_argument("--out", required=True)
    b.add_argument("--column", required=True, help="name of the new column to fill")
    b.add_argument("--ai", help="force a model (default: local, then gemini, claude, chatgpt). Use claude for anything a buyer reads")
    b.add_argument("--workers", type=int, default=4)

    args = p.parse_args()
    {"status": cmd_status, "ask": cmd_ask, "debate": cmd_debate, "research": cmd_research, "bulk": cmd_bulk}[args.cmd](args)


if __name__ == "__main__":
    main()
