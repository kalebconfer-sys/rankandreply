# CLAUDE.md

Guidance for Claude Code sessions in this repository.

## What this is

Two things share this repo:
1. **rankandreply.com**: a static GitHub Pages site (`index.html`, `privacy-policy.html`, `terms-of-service.html`, and the new offer page `ai-visibility/` with its own `privacy.html` and `terms.html`). No build step.
2. **The AI Visibility business** in `business/`: research, plans, outreach playbooks and Python tools. `_config.yml` keeps `business/` off the Pages site. **Start with `business/README.md`.** The setup steps for the owner's computer are in `business/SETUP.md`.

The business measures whether ChatGPT, Gemini, Perplexity and Claude recommend a B2B company when buyers ask, then does the work to improve it. It's sold by cold email and marketplaces, without sales calls. The owner is non-technical, has limited time, and prefers plain-language explanations and step-by-step instructions on Windows.

## Rules that protect the business (don't break them)

- **The repo is public.** Never commit `business/tools/.env`, anything in `business/data/` (leads, replies, reports, clients, outbox), or real contact details. `.gitignore` covers these; keep it that way.
- **No results claims we can't back:** no fake testimonials, case studies, client counts or ranking guarantees, on any page, email or proposal. Vendor or self-reported statistics are labeled as such. Sources live in `business/01-research/sources/`.
- **Nothing posts automatically.** Tools find, score and draft. The owner sends every email, Reddit or community reply, and Upwork proposal by hand. Reddit, X, LinkedIn and Upwork ban automated replies and proposals (see `business/04-outreach/reddit.md`). The one allowed exception: the owner schedules posts for their own LinkedIn profile.
- **Cold email compliance:** United States only for the first 90 days; a real name, a mailing address and a "business solicitation" line in every footer; opt-outs honored immediately; sending domains never in the Google account that runs rankandreply.com.
- **Never seed Reddit or forums for clients.**
- The old `privacy-policy.html` carries Google API Limited Use language for the earlier Google Business Profile product. Don't edit it casually (see `README.md`).

## Tools (`business/tools/`)

| File | Purpose |
|---|---|
| `council.py` | Runs one task across Claude, ChatGPT, Gemini, Perplexity and a local Ollama model: ask, debate, research, bulk |
| `visibility.py` | The product engine: `snapshot` (client report), `questions`, and `enrich`/`probe`/`firstline` (cold-email leads) |
| `autopilot.py` | `leads` and `replies`: the daily routine |
| `scout.py` | Reads Upwork, F5Bot and Syften alert emails (IMAP, read-only) and searches reddit.com through Perplexity; drafts replies; `posts` writes weekly LinkedIn posts |
| `outbox.py` | Builds `today.html` from the day's outbox |
| `*.bat`, `setup-mac.sh` | Owner-facing double-click scripts (keep the `.bat` files CRLF, ASCII) |

- Keys and model names come from `business/tools/.env` (template: `.env.example`). The default Claude model is `claude-opus-5-5` with server-side refusal fallback.
- **Before committing any change to the tools, run the offline tests:** `cd business/tools && python tests/run_all.py`. They must end with `0 failed`. They use `tests/fake_llm.py` (a stand-in OpenAI-compatible server) and never touch real accounts. Add a check when you fix a bug.
- Keep the honesty guarantees in the code: an email's opening line is built only from the saved probe answer, and "didn't come up" requires absence from every run; competitor names must appear in the answer; threads must come from real search results; report data is anonymized before it reaches LinkedIn posts.
- The tools have been tested only against the stand-in server. The first real run happens on the owner's machine with real keys (day 3 of the plan). If real formats differ, especially alert emails, ask for a saved `.eml` and adjust the parser.

## Working with the owner

- Explain what you're doing in plain words, and give exact steps (which file to double-click, what to paste where).
- Work on the branch `claude/ai-automated-business-plan-ptu9y7` unless told otherwise. Merging to `main` publishes `ai-visibility/` on rankandreply.com, so confirm with the owner first.
- The plan and the current day are in `business/02-plan/`. When asked "what's next," check the day-by-day plan and the scoreboard (`business/data/scoreboard.csv`, if it exists).
