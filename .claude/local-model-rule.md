# Standing rule: use the local model where it's appropriate

Claude usage is a metered resource and I want it to last. Don't spend it on
work a small local model handles fine.

Once per session, check whether a local model is reachable:

```
ollama list
```

If that succeeds, prefer delegating the work below to a local model via Bash
(`ollama run <model> "<prompt>"`) instead of generating it yourself. Pick a
model from whatever `ollama list` actually returns — don't assume a name. If
the check fails (no Ollama, cloud session, not installed), just do the work
directly and don't mention it.

## Delegate to local

- First drafts and rough passes that will be reviewed before anything ships
- Bulk variations on a line or paragraph that already works
- Classification and triage (is this review angry? is this lead in scope?)
- Reformatting, restructuring, or summarizing text that already exists
- Throwaway scratch text, test fixtures, placeholder copy

## Keep on Claude

- Anything published under a client's business name — Google Business Profile
  posts, review replies. Short, public, and carrying someone else's
  reputation: the wrong place to save money.
- Legal and policy pages
- Pricing, positioning, and claims copy
- Code changes, debugging, and anything needing real repo context

## The test

If a human reviews it before it goes out, local is fine. If it publishes
without a second look, use Claude.

Don't ask permission to route a task locally under these rules — just do it,
and say which model produced the draft.

---

**How to install this globally (Windows):**

```
copy .claude\local-model-rule.md %USERPROFILE%\.claude\CLAUDE.md
```

Run that from the repo root. It applies to every project on the machine.
Verify with `/memory` inside Claude Code.
