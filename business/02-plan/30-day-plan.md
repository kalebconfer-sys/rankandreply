# The first 30 days

**Finish line for day 30:**

| | Target |
|---|---|
| Cold-email infrastructure | Live and clean (bounces under 2%, complaints under 0.1%) |
| Cold-email sends | **1,800+ first touches** (3,000+ including follow-ups) |
| Reports | **15+ "yes, send it" replies**, every report delivered within 1 business day |
| Revenue | **First money in:** at least 1 Fix Plan or retainer, or 3+ marketplace orders |
| Decision | The winning segment chosen from real numbers |

**Owners:**

| Owner | Job |
|---|---|
| **You** | Accounts, payments, approvals, pressing send |
| **Claude** (Chair) | Writing, building, deciding |
| **ChatGPT** (Critic) | Attacking the work |
| **Gemini** (Analyst) | Reading the numbers |
| **Perplexity** (Scout) | Finding buyers and checking facts |
| **Local** (Worker) | Bulk sorting |

The exact daily steps are in [`day-by-day.md`](day-by-day.md).

## Week 1 (days 1–7): Set up everything that needs time to mature

| # | Task | Owner | Done when |
|---|---|---|---|
| 1 | Buy 5 sending domains, create 15 inboxes, start warmup in Instantly | You (Claude walks you through it) | Instantly shows 15 inboxes warming, all DNS checks green |
| 2 | Get API keys for all four AIs; install Ollama; fill in `.env` | You | `python council.py status` shows 5× ready |
| 3 | Stripe: Fix Plan $490 link and Retainer $1,500/mo link | You | Both links open a checkout page |
| 4 | Virtual mailbox address for the legal footer | You | Address in hand |
| 5 | Run 10 snapshots on real companies (5 software, 5 services) | Claude runs, you watch | 10 reports in `business/data/reports/`; real cost per report noted |
| 6 | Council debate on the 10 reports: is the hook true and strong? | All five AIs | Decision written to `business/runs/` |
| 7 | Upwork profile, Catalog listing; Fiverr gig; Contra profile | You paste; Claude wrote the copy | All three live |
| 8 | First 10 Upwork proposals | Perplexity finds, Claude drafts, you submit | 10 sent |
| 9 | Merge the branch so /ai-visibility/ is live; swap in the Stripe links | You (Claude makes the edit) | rankandreply.com/ai-visibility/ loads with working buttons |

## Week 2 (days 8–14): Build the first lead batches; keep warming

| # | Task | Owner | Done when |
|---|---|---|---|
| 1 | Apollo searches for both segments; export 600 leads | You | 2 CSVs downloaded |
| 2 | Verify → enrich → probe → firstline | Worker + scripts | `ready.csv` files with first lines |
| 3 | Read 40 first lines by hand; fix or delete bad rows | You + Critic | 40 rows checked |
| 4 | Load Sequences 1 and 2 into Instantly, compliance footer on, tracking OFF | You | Test emails land in your Gmail/Outlook/Yahoo inboxes, not spam |
| 5 | Critic red-teams the emails as the buyer and as a spam filter | ChatGPT | 3 weakest points fixed |
| 6 | 15 more Upwork proposals | Scout, Chair, you | 25 sent in total |
| 7 | Set up the reply process: export → classify → draft | Worker + Chair | Dry run on 5 fake replies works |

## Week 3 (days 15–21): Launch

| # | Task | Owner | Done when |
|---|---|---|---|
| 1 | Start sending at 5/inbox/day (75/day), ramping to 10 (150/day) on day 19 | Instantly | Sends going out, bounces under 2% |
| 2 | Reply check every morning; every "yes" gets its report within 1 business day | Worker tags, Chair drafts, you send | Zero "yes" replies older than 24 hours |
| 3 | 2 new lead batches (300 each) | You + scripts | Queue never runs dry |
| 4 | 15 Upwork proposals; deliver any marketplace orders | You + AIs | All orders delivered early |
| 5 | Monday council review #1 | All | One change chosen and made |

## Week 4 (days 22–30): Learn and pick

| # | Task | Owner | Done when |
|---|---|---|---|
| 1 | Ramp to 15/inbox/day (225/day) | Instantly | Steady sending, still clean |
| 2 | Follow up on every report delivered (day 3 and day 8 templates) | Chair drafts, you send | No report without a follow-up |
| 3 | Monday council review #2 with the full reply data | All | Reply-rate and conversion by segment computed |
| 4 | **Day 30 decision:** winning segment gets 90% of volume | Chair decides, you approve | Written into the scoreboard |
| 5 | Plan days 31–60 (Phase 3 prep: 5 more domains, agency list) | Chair | Domains bought and warming |

## If things go wrong

| Signal | Do this |
|---|---|
| Bounces over 2% | Stop that list. Re-verify with MillionVerifier. Drop catch-all addresses |
| Emails landing in spam in your own tests | Stop sending. Check DNS at mail-tester.com, cut volume in half, extend warmup a week |
| No "yes" after 600 first touches | Council debate with the first lines and replies attached. Rewrite the hook. Try the other segment |
| People say yes but nobody buys after 15 reports | Ask 3 of them, by email, what would have made it a yes. Test the Fix Plan at $290, or a 14-day trial of the Retainer |
| You're out of time | Cut Upwork bidding first, never the 24-hour report delivery |
