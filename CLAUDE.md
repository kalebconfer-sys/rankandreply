# Working in this repo

Static marketing site for rankandreply.com. Three HTML files, inline CSS, no
build step, hosted on GitHub Pages. Edit and push.

Read `README.md` before changing page content — the "Things not to break"
section is load-bearing, not style preference. Short version: the privacy
policy names real data processors and must stay accurate, no results claims
anywhere (there are no clients yet), and the two prices are quoted in live
outreach so they change together or not at all.

The bot that does the actual customer work lives at `C:\Users\kaleb\content-bot`,
not here.

## Standing rule: use the local model where it's appropriate

Claude usage is a metered resource and the owner wants it to last. Don't spend
it on work a small local model handles fine.

At the start of a session, check once whether a local model is reachable:

```
ollama list
```

If that succeeds, prefer delegating the work below to it via Bash
(`ollama run <model> "<prompt>"`) instead of generating it yourself. If it
fails — no Ollama, cloud container, not installed — just do the work directly
and don't mention it.

**Delegate to local:**
- First drafts and rough passes that will be reviewed before anything ships
- Bulk variations on a line or paragraph that already works
- Classification and triage (is this review angry? is this lead in scope?)
- Reformatting, restructuring, summarizing text that already exists
- Throwaway scratch text, test fixtures, placeholder copy

**Keep on Claude:**
- Anything published under a client's business name — GBP posts, review
  replies. These are short, public, and carry someone else's reputation.
  They are the wrong place to save money.
- The privacy policy and terms pages
- Pricing, positioning, and claims copy
- Code changes, debugging, and anything requiring repo context

**When in doubt:** if a human reviews it before it goes out, local is fine.
If it publishes without a second look, use Claude.

Don't ask permission to route a task locally under these rules — just do it
and note which model produced the draft.
