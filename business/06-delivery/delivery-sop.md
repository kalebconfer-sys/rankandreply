# Delivery: how a client month gets done

AI does the measuring and the first drafts. A human checks everything before it reaches the client. Every step is the same every month, so a contract editor can take this over later without retraining.

## Fix Plan ($490, 5 business days)

| Day | Step | Who | Command / tool |
|---|---|---|---|
| 0 | Payment → onboarding form → client folder `business/data/clients/<slug>/` with their answers saved as `intake.md` | Stripe + Tally; you create the folder | — |
| 1 | Write `questions.txt`: their 5 buyer questions plus generated ones, 40 in total. Read the list and cut any question a real buyer wouldn't ask | Chair, then you | `python visibility.py questions --brand ... --domain ... --n 35 --out ../data/clients/<slug>/questions.txt`, then add their 5 |
| 1 | The full run: 40 questions × 4 engines × 3 runs | Engine | `python visibility.py snapshot --brand ... --domain ... --questions ../data/clients/<slug>/questions.txt --runs 3 --yes --pdf --out ../data/clients/<slug>/<date>` |
| 2 | **Cited-sources analysis.** The report lists the 15 sites the engines cited most. For each one, check on the live web whether the client is listed, reviewed or mentioned there, and what it takes to get on it | Scout (Perplexity, or Claude with web search); you spot-check 3 | One question per site: `python council.py research "Is <brand> (<domain>) listed or mentioned on <site>? Give the URL, or say not found. How does a company get listed there?"` A model without web search would guess, so never use `ask` for this |
| 2 | 30-day roadmap: the 10 actions, ordered by impact, each with an owner (us or the client) | Chair | `python council.py ask "Write the 30-day roadmap..." --ai claude --file .../intake.md --file .../findings.md --file .../sources.md` (`--file` can be repeated) |
| 3 | Write 2 pages (pick the 2 biggest gaps, usually a comparison page and a use-case page) | Chair | `page_writer.txt` via `council.py bulk ... --ai claude` |
| 3 | QA each page | Critic, then you | `qa_check.txt`, then the human checklist below |
| 4 | Fix, format into Google Docs, write a one-page cover note | Chair + you | — |
| 5 | Deliver by email with the Retainer and Sprint offers (Fix Plan credited if they start within 30 days). **For a Fiverr or Upwork order, deliver on the platform with no links, emails or Stripe links** | You | — |

## Retainer month ($1,500)

| Week | Step | Who |
|---|---|---|
| 1 | Tracking run on the same 40 questions: `snapshot --questions .../questions.txt --runs 3 --yes --pdf --compare <last month>/raw.json` | Engine |
| 1 | Pick this month's 4 pages from the biggest gaps; write a listing/mention action list | Chair, then you approve the topics |
| 2 | Write the 4 pages → Critic QA → your QA → send to the client for approval | Chair, Critic, you |
| 3 | Listings and mentions: prepare the submissions for the review sites and directories the engines cite; draft pitches to "best of" list editors; spec any structured-data fixes for their developer | Chair drafts, you send or submit |
| 4 | Publish approved pages (or the client does). Monthly report email: what we shipped + the before/after numbers + next month's plan | You |

**Honest reporting rule:** If the numbers didn't move, say so in the first line, explain what we think is happening, and say what we're changing. Clients stay for honesty. They leave over spin.

## Human QA checklist (every page, every time)

- [ ] The first two sentences answer the target question directly.
- [ ] Every claim about the client comes from the intake form or their own website. No `[NEEDS CLIENT INPUT]` tags are left in.
- [ ] Competitors are described fairly, including where a competitor is the better choice.
- [ ] No numbers without a source. No promises of results.
- [ ] It reads like a knowledgeable person wrote it. Delete anything a buyer would skip.
- [ ] FAQ structured data validates (paste it into validator.schema.org).
- [ ] The client has approved it in writing before it's published.

## Time budget per client per month

| Task | Time |
|---|---|
| Review the tracking run and pick topics | 20 min |
| QA 4 pages (after AI QA) | 80 min |
| Listings and mentions work | 45 min |
| Monthly report email | 20 min |
| Client emails | 30 min |
| **Total** | **about 3–3.5 hours** |

**Capacity cap:** 5 Retainer clients until a contract editor is hired. Hire one ($25–40/hr) when the 4th Retainer signs. The editor costs about $100–140 per client per month.

**Fix Plan cost check:** the full run is 480 answers plus extraction, so `snapshot` will ask for `--yes`. Expect $15–30 in API calls.

## What we never do

- **Fake reviews:** we don't post, buy or ask for them. We don't create sockpuppet accounts.
- **Undisclosed promotion:** we don't write it anywhere, Reddit included.
- **Seeding Reddit or forums for a client:** we don't do it, even with disclosure. Reddit is actively removing AI-visibility seeding (July 2026), and it puts the client's brand at risk.
- **Mass-produced thin pages:** these get sites penalized.
- **Ranking promises:** we don't promise or imply guaranteed rankings, in any document.
- **Unapproved publishing:** nothing goes on a client's site without their written approval.
