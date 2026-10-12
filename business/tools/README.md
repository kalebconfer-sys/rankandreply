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
| `bulk --in leads.csv --prompt prompts/x.txt --out out.csv --column name` | Runs a prompt on every row of a spreadsheet: scoring leads, writing first lines, tagging replies. Uses the free local model first. Re-run it to resume after a crash |

Every run is saved to `business/runs/`, which is gitignored and never pushed.

## Model names

Model names change every few months. When one is retired, set the new name in `.env` (for example `OPENAI_MODEL=...`). You don't need to edit the code.

Claude calls use `claude-opus-5-5` with server-side refusal fallback turned on (`fallbacks: "default"`). If Claude's safety filter declines a request, the API retries it on a fallback model automatically instead of failing. Set `CLAUDE_MODEL` to change the model.
