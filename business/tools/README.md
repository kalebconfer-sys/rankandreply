# Tools

Everything here runs on your own computer (Windows, Mac or Linux) with Python 3.10+.

## One-time setup (about 15 minutes)

```bash
cd business/tools
pip install -r requirements.txt
copy .env.example .env        # Mac/Linux: cp .env.example .env
```

Open `.env` and paste in whichever keys you have. You don't need all of them.

| AI | Where to get a key | Cost |
|---|---|---|
| Claude | console.anthropic.com → API Keys | Pay per use. A Claude.ai subscription is separate and doesn't include API credit |
| ChatGPT | platform.openai.com → API keys | Pay per use. ChatGPT Plus doesn't include API credit |
| Gemini | aistudio.google.com → Get API key | Free tier available |
| Perplexity | perplexity.ai/settings/api | Pro subscribers get monthly API credit |
| Local | Install Ollama from ollama.com, then run `ollama pull llama3.1:8b` | Free |

Check what's connected:

```bash
python council.py status
```

## council.py

| Command | What it does |
|---|---|
| `status` | Shows which AIs are ready |
| `ask "question" [--file doc.md]` | Sends the same question to every ready AI and shows the answers side by side |
| `debate "question" [--file doc.md]` | Round 1: each AI answers alone. Round 2: each reads the others and revises. Then Claude writes a decision with next actions and the result that would prove it wrong |
| `research "topic"` | Live web research with sources (Perplexity, or Claude with web search) |
| `bulk --in leads.csv --prompt prompts/x.txt --out out.csv --column name [--ai claude]` | Runs a prompt on every row of a spreadsheet. Uses the free local model unless you pass `--ai`; **use `--ai claude` for anything a buyer reads**. Re-run the same command to resume: failed rows are retried, and a row keeps its stored value only if its inputs are unchanged. It stops up front if the prompt's `{placeholders}` don't match the CSV columns |

`--file` can be repeated on `ask` and `debate` to attach several documents.

## visibility.py and autopilot.py

| Command | What it does |
|---|---|
| `autopilot.py leads --in apollo.csv` | Enrich → probe → firstline in one go. Writes `<name>-ready.csv` |
| `autopilot.py replies --in replies.csv` | Tags each reply, drafts answers, runs the free report for every "yes", writes ready-to-send emails into `business/data/outbox/<date>/`. Sends nothing |
| `visibility.py snapshot --brand X --domain x.com [--pdf]` | The report: 10 generated questions × every engine with a key × 2 runs by default. `--questions file --runs 3 --yes` for paid plans; `--compare last/raw.json` for month-over-month; `--prepared-by "Agency"` for white-label |
| `visibility.py questions --brand X --domain x.com --n 40 --out q.txt` | Just the buyer questions, to edit before a paid run |
| `visibility.py enrich / probe / firstline` | The three lead steps on their own |

## scout.py (Reddit and Upwork)

| Command | What it does |
|---|---|
| `scout.py run` | Reads new Upwork and F5Bot alert emails, searches reddit.com for recent buyer questions, scores every post, and drafts replies and proposals into `business/data/outbox/<date>/scout-*.txt` |
| `scout.py inbox` / `scout.py reddit` | Just one of the two sources |
| `--eml-dir folder` | Parse saved `.eml` files instead of logging in to the inbox |
| `scout.py posts` | 3 posts for your own LinkedIn profile (data, how-to, question of the week). Only real report numbers, never the names of companies you checked. You schedule them once |

Every scout and autopilot run also writes `today.html` in the day's outbox: one page with every draft, an Open link and a Copy button (`outbox.py`). Links found in alert emails from Upwork, F5Bot (Reddit, Hacker News) and Syften (X, Bluesky, Stack Exchange, Indie Hackers) are all recognized.

**What it never does:**
- **Post anything.** You post every reply and submit every proposal by hand.
- **Touch your mail.** The inbox is opened read-only, only alert senders are fetched, and nothing is marked, moved or deleted.
- **Keep a thread the search didn't return.** If the AI's answer lists a thread that wasn't in the search results, it's dropped.

Posts it has already seen are skipped on the next run. Search terms live in `scout_queries.txt`.

**How "named" is decided:** the company's full name, its domain, or a competitor-list entry that normalizes to the same name ("Acme Software, Inc." = "Acme"). A shortened name on its own counts as "maybe": it isn't counted in reports and is never claimed in an email. The opening line is written only when the company was absent from **every** probe run, and every competitor it names appears in the saved `probe_answer`.

**Cost guards:** `snapshot` stops above 200 paid calls, and `enrich`/`probe` above 300, unless you add `--yes`. Extraction calls are counted when the local model isn't running.

Every run is saved to `business/runs/`, which is gitignored and never pushed.

## Model names

Model names change every few months. When one is retired, set the new name in `.env` (for example `OPENAI_MODEL=...`). You don't need to edit the code.

Claude calls use `claude-opus-5-5` with server-side refusal fallback turned on (`fallbacks: "default"`). If Claude's safety filter declines a request, the API retries it on a fallback model automatically instead of failing. Set `CLAUDE_MODEL` to change the model.
