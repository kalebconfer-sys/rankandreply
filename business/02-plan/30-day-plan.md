# The first 30 days

**Finish line for day 30:**

| | Target |
|---|---|
| Tools | Proven against the real AI APIs (not only the offline tests) |
| Cold-email infrastructure | Live and clean (bounces under 2%, complaints under 0.1%) |
| Cold-email sends | **About 2,000 first-touch emails** (about 3,900 sends including follow-ups) |
| Reports | **10+ "yes, send it" replies**, every report delivered within 2 business days |
| Revenue | **First money in:** at least 1 Fix Plan or retainer, or 1–3 marketplace orders |
| Decision | The winning segment chosen from real numbers |

**Owners:**

| Owner | Job |
|---|---|
| **You** | Accounts, payments, approvals, pressing send |
| **Claude** (Chair) | Writing, building, deciding |
| **ChatGPT** (Critic) | Attacking the work |
| **Gemini** (Analyst) | Reading the numbers |
| **Perplexity** (Scout) | Checking facts on the live web |
| **Local** (Worker) | Bulk sorting |

The exact daily steps are in [`day-by-day.md`](day-by-day.md).

## Week 1 (days 1–7): Set up everything that needs time to mature

| # | Task | Owner | Done when |
|---|---|---|---|
| 1 | Buy 10 sending domains, create 30 inboxes (outside the rankandreply.com Google account), start warmup in Instantly | You (Claude walks you through it) | Instantly shows 30 inboxes warming, all DNS checks green |
| 2 | API keys for all four AIs (Gemini with billing on); Ollama, or `LOCAL_DISABLED=1` on a small laptop | You | `python council.py status` shows the AIs ready |
| 3 | **Prove the tools on real APIs:** 3 snapshots | Claude runs, you watch | 3 PDFs made. Any error that happens twice → paste it into Claude Code before going on |
| 4 | Stripe: Fix Plan $490, Retainer $1,500/mo and Sprint $3,900 links; virtual mailbox; check the fictitious-name registration | You | Links open a checkout page; address in hand |
| 5 | 7 more snapshots (10 in total, 5 software + 5 services) | Engine | Real cost per report noted |
| 6 | Council debate on the 10 reports: is the hook true and strong? | All the AIs | Decision saved in `business/runs/` |
| 7 | Upwork profile, Catalog and saved-search alerts; Fiverr gig; Contra profile; F5Bot Reddit alerts; read-only inbox access for `scout.py` | You paste; Claude wrote the copy | All live; `scout.py run` reads the alert emails |
| 8 | Merge the branch so /ai-visibility/ is live; swap in the Stripe links | You (Claude makes the edit) | rankandreply.com/ai-visibility/ loads with working buttons |

## Week 2 (days 8–14): Build the first lead batches; keep warming

| # | Task | Owner | Done when |
|---|---|---|---|
| 1 | Apollo searches for both segments (US only); export 1,000 leads | You | 2 CSVs downloaded |
| 2 | Verify → `autopilot.py leads` (enrich, probe, first line) | Worker + scripts | `-ready.csv` files with first lines and the AI's saved answers |
| 3 | Check 40 first lines against `probe_answer` by hand; delete bad rows | You + Critic | 40 rows checked |
| 4 | Load Sequences 1 and 2 into Instantly with the compliance footer on and tracking OFF | You | Test emails land in your own Gmail/Outlook/Yahoo inboxes, not spam |
| 5 | Critic red-teams the emails as the buyer and as a spam filter | ChatGPT | 3 weakest points fixed |
| 6 | Dry-run the reply process on 8 made-up replies | Autopilot | Labels right, drafts sendable |
| 7 | Daily `scout.py run`: Reddit replies (answers only, no business mentions for 2 weeks) and up to 5 Upwork proposals a week | Scout + Claude draft, you post | Posted by hand |

## Week 3 (days 15–21): Launch

| # | Task | Owner | Done when |
|---|---|---|---|
| 1 | Start at 5/inbox/day (150/day), ramping to 10 (300/day) on day 19 | Instantly | Sends going out, bounces under 2% |
| 2 | Buy 5 more domains and 15 inboxes; start warming them | You | Warming in Instantly |
| 3 | Run `autopilot.py replies` once a day; every "yes" gets its report within 2 business days | Autopilot, you send | No "yes" older than 2 business days |
| 4 | New lead batches, so the queue never runs dry (about 200 new leads per sending day at full volume) | You + autopilot | 3 days of leads always queued |
| 5 | Monday council review #1 | All | One change chosen and made |

## Week 4 (days 22–30): Learn and pick

| # | Task | Owner | Done when |
|---|---|---|---|
| 1 | Ramp to 15/inbox/day (450/day) | Instantly | Steady sending, still clean |
| 2 | Follow up on every report delivered (day 3 and day 8 templates) | Claude drafts, you send | No report without a follow-up |
| 3 | Monday council review #2 with the full reply data | All | Reply rate and conversion by segment computed |
| 4 | **Day 30 decision:** the winning segment gets 90% of volume | Claude decides, you approve | Written into the scoreboard |
| 5 | Plan days 31–60: agency list, the editor hire trigger, the new inboxes go live | Claude | Plan saved |

## If things go wrong

| Signal | Do this |
|---|---|
| A tool errors on real APIs | Paste the full error into Claude Code in this repo. If it isn't fixed in 30 minutes, use the standby freelancer budget |
| Bounces over 2% | Stop that list. Re-verify with MillionVerifier. Drop catch-all addresses |
| Emails landing in spam in your own tests | Stop sending. Check DNS at mail-tester.com, cut volume in half, extend warmup a week |
| An inbox gets suspended | Replace it (budgeted), and lower the per-inbox volume on that provider |
| No "yes" after 1,000 first touches | Council debate with the first lines and replies attached. Rewrite the hook. Try the other segment |
| People say yes but nobody buys after 15 reports | Ask 3 of them, by email, what would have made it a yes. Test the Fix Plan at $290, or lead with the Sprint |
| You're out of time | Drop Upwork bidding first. Never miss the 2-business-day report promise |
