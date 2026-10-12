# The 90-day plan

**Goal:** **$5,000+/month in recurring revenue by day 90** (retainers and agency seats, not counting one-time sales). In the base case the first $4–5k month, counting one-time sales, arrives in month 2.
**Stretch:** $10,000+/month in total revenue in month 3.
**Business:** AI Visibility by Rank and Reply. See [`../01-research/market-research.md`](../01-research/market-research.md) for why.
**Your time:** about 1.5–2 hours/day, at whatever time fits your shifts. You never cold-call. Calls happen only when a buyer asks for one.

## The three phases

| Phase | Days | Theme | Must be true at the end |
|---|---|---|---|
| **1. Build and warm** | 1–14 | Accounts, keys, engine tested on real companies, inboxes warming, marketplaces live | 30 inboxes warmed; the tools proven against the real AI APIs; 10 real snapshots run (on companies we pick, not clients); offer page live; Upwork/Fiverr/Contra live |
| **2. Launch and learn** | 15–45 | Cold email live in two segments; every "yes" gets a report within 2 business days | About 2,000 first-touch emails by day 30 and 5,000+ by day 45; 25+ reports delivered; **first paying customers**; one segment chosen by reply data |
| **3. Double down and systematize** | 46–90 | More volume in the winning segment, agency white-label channel, automation of the manual steps | **$5k+/month recurring**; reply-to-report automated with one-click approval; first real case study (with permission) |

## Funnel math (assumptions, replaced by real numbers every Monday)

**Sending capacity:** The daily cap includes follow-ups, and every lead gets 3 emails, so new leads per month = sends ÷ 3.

| Setup | Sends/day | New leads/month |
|---|---|---|
| 30 inboxes from day 1, at 20 emails per inbox per day | 600 | about 4,200 |
| Plus 15 more inboxes bought on day 15 and warmed by day 30 | 900 | about 6,300 |

| Step | Conservative | Base | Good | Source of the assumption |
|---|---|---|---|---|
| New leads emailed in month 2 / month 3 | 5,500 / 6,300 | 5,500 / 6,300 | 5,500 / 6,300 | The capacity above, with the ramp |
| "Yes, send it" replies | 0.4% | 0.7–0.8% | 1.5% | Instantly 2026 average reply rate is 3.43% across all replies; positive replies are a fraction of that. Our asset-first offer is untested |
| Report → Fix Plan ($490) | 5% | 8% | 12% | Untested estimate |
| Report → Retainer directly | 2% | 3% | 5% | Untested estimate |
| Fix Plan → Retainer within 30 days | 20% | 30% | 40% | The Fix Plan price is credited to month one |
| Monthly retainer churn | 10% | 8% | 5% | AI answers move slowly, so expect some early cancellations. The 3-month Sprint and monthly progress signals reduce it |
| Marketplace revenue per month | $100 | $500 | $1,500 | Upwork plus Fiverr, small orders; few posts found so far |

**What base case means:**
- **Month 2:**
  - About 38 reports.
  - About 3 Fix Plans: $1,470.
  - About 2 new retainers: $3,000/month, less about $490 in Fix Plan credit.
  - Marketplaces: about $500.
  - **About $4,500 for the month.**
- **Month 3:**
  - About 50 reports (better copy).
  - About 4 Fix Plans: $1,960.
  - About 2.7 new retainers, bringing the total to **about 4.5 active ($6,750/month)** after churn.
  - 1 agency partner with 1–2 clients: $900–1,800.
  - Marketplaces: about $500.
  - **About $10,000–11,000 for the month, of which about $7,600–8,500 is recurring.**

**Conservative case:** about $2,000–3,000/month by day 90, of which about $2,000 is recurring. That triggers the kill criteria in the research doc: the council reviews the segment, the copy and the offer before any more spend.

**Good case:** more retainers than one person can deliver. The **capacity cap of 5 retainers** (see the offer) binds by month 2, so the contract editor gets hired early.

These are planning numbers, not promises. They exist so that every Monday we can see which step of the funnel is underperforming and fix that step.

## Phase 1: Build and warm (days 1–14)

Day-by-day steps are in [`day-by-day.md`](day-by-day.md).

- **Money and legal:**
  - Stripe account.
  - Payment Links: Fix Plan $490, Retainer $1,500/month, Sprint $3,900.
  - A virtual mailbox address for the email footer.
  - Confirm "Rank and Reply" is registered as a fictitious name of RevivaCatch LLC in Pennsylvania.
- **AI:**
  - API keys for Claude, ChatGPT, Gemini (**with billing on**, because the free tier may use inputs to improve Google's products) and Perplexity.
  - Ollama with `llama3.1:8b`, or `LOCAL_DISABLED=1` on a computer with less than 16 GB of memory.
  - `council.py status` shows the AIs ready.
- **Email:**
  - 10 sending domains and 30 inboxes, warming in Instantly from day 1–2. They live outside the Google account that runs rankandreply.com.
  - Apollo and MillionVerifier accounts.
- **Proof:** Run `visibility.py snapshot` on **10 real companies** across both segments. You're not selling to them yet. This does three things:
  1. Proves the tools work against the real APIs.
  2. Shows us the real cost per report.
  3. Gives us our own data for emails. Only use it if the numbers support it, and describe the sample truthfully, for example "Of 5 B2B software companies I checked...".
- **Marketplaces:** Upwork profile, Catalog listing and saved-search alerts. Fiverr gig. Contra profile.
- **Site:** Merge the branch so rankandreply.com/ai-visibility/ goes live, with the Stripe links swapped in.

## Phase 2: Launch and learn (days 15–45)

- **Sending:**
  - Ramp 150 → 300 → 450 sends/day, then 600 from day 31 (see [`../04-outreach/cold-email.md`](../04-outreach/cold-email.md)).
  - Split 70/30 between Segment A (software) and Segment B (B2B services). United States only.
  - **Day 15:** buy 5 more domains and 15 more inboxes, and start warming them. They're ready by day 30.
- **Every "yes" gets its report within 2 business days.** Speed still sells. `autopilot.py replies` runs the reports and drafts the emails; you skim and send.
- **Monday council review:**
  - Gemini (Analyst) reads the week's sends, replies and sales.
  - ChatGPT (Critic) attacks the weakest step.
  - Claude (Chair) picks **one** change for the week.
  - You approve it.
- **Day 30 checkpoint:**
  - Pick the winning segment: higher "yes" rate × higher report-to-paid rate. The loser drops to 10% of volume.
  - If the positive reply rate is under 0.3% in both, rewrite the hook before sending more. Use a council debate with the reply CSV attached.
- **First client delivery:** follow [`../06-delivery/delivery-sop.md`](../06-delivery/delivery-sop.md). Every first delivery gets extra QA time, because these clients become the case studies.
- **Hire the editor** when the 4th retainer signs, before the cap of 5 is reached. Hire a part-time contract editor ($25–40/hr) through Upwork, and give them the QA checklist.

## Phase 3: Double down and systematize (days 46–90)

- **Volume:** 45 inboxes at 20/day (900 sends/day) in the winning segment. Add 15 more inboxes only if bounces and complaints stay clean.
- **Niche depth:** Inside the winning segment, split by sub-category (for example "HR software" vs "dev tools") and keep a separate copy variant for each. The best-replying sub-category gets more volume.
- **Agency white-label channel (from day 46):** follow [`../04-outreach/agency-partners.md`](../04-outreach/agency-partners.md). The goal is 3 agencies with at least 1 client each by day 90.
- **Reddit Ads test (from day 46):** a promoted post offering the free report, $15/day for 14 days (about $210). Keep it if the cost per "yes" is under about $40. See [`../04-outreach/reddit.md`](../04-outreach/reddit.md).
- **Reduce churn:**
  - Offer the 3-month Sprint ($3,900 prepaid) in every report email.
  - Every monthly report leads with progress signals that move before AI answers do: pages published, listings won, and whether the client's own pages are being **cited** by the engines (the report already tracks this).
- **Automation (remove you from the repetitive steps):**
  - `autopilot.py replies` already tags, drafts and runs reports.
  - Next, connect it to Instantly's reply webhook (n8n or a small script), so the outbox fills on its own and you approve with one click.
  - Stripe payment sends the onboarding form; the form submission creates the client folder and runs the first tracking report.
  - Monthly client reports run on a schedule (`snapshot --compare last-month/raw.json`).
- **Proof:**
  - Ask the first two retainer clients for written permission to publish an anonymized before/after.
  - Add it to the page and the emails. Proof is the single biggest lift available to cold email.
  - Until then, **we publish no results claims.**

## Weekly rhythm (from week 3)

| When | What | Who |
|---|---|---|
| Once a day, any time (30–45 min) | `autopilot.py replies`: read the outbox, send the drafts and reports, add opt-outs to Instantly's blocklist | Worker tags, Chair drafts, **you** approve and send |
| Once a day (20 min) | `autopilot.py leads` on a new Apollo export; check 20 first lines against `probe_answer`; upload | **You** run it; the AI does the rest |
| Once a day (15–20 min) | `scout.py run`: Reddit and Upwork posts found, scored and drafted → **you** post up to 3 Reddit replies by hand and submit good Upwork proposals | Scout, Worker, Claude, **you** |
| Monday (45 min) | Council review: numbers, the weakest step, one change | Gemini, ChatGPT, Claude, **you** |
| Friday (15 min) | Fill in the scoreboard (copy [`templates/scoreboard.csv`](templates/scoreboard.csv) to `business/data/` once) | You |

## Budget

| Item | Month 1 | Months 2–3 |
|---|---|---|
| 15 domains (10 on day 1, 5 on day 15; yearly) | about $210 | — |
| Inboxes (30, plus 15 from day 15) | $100–150 | $145–160 |
| Reserve for suspended inboxes | $30 | $30 |
| Instantly Hypergrowth | $97 | $97 |
| Apollo Professional | $79–99 | $79–99 |
| MillionVerifier | $37 | $37 |
| Virtual mailbox | $10–15 | $10–15 |
| AI APIs (test snapshots, probes, reports) | $50–100 | $75–150 |
| Upwork Connects | $20–50 | $20–50 |
| Stripe, Fiverr, Contra | $0 (fees come out of sales) | — |
| **Total** | **about $630–790** | **about $490–640/month** |
| Optional: a Python freelancer on standby for setup problems | up to $150 one-time | — |
| Reddit Ads test (from day 46) | — | about $210 one-time |
| F5Bot Reddit alerts | $0 | $0 |

## After day 90: the path to $100k/month

**The math that matters:**
- At 8% monthly churn, 45 retainers lose about 3.6 a month. Growing from about 5 to 45 over 12 months takes about **7–8 new retainers a month**.
- At base-case conversion (about 5–6% of reports become retainers) that's about 130 reports a month. Cold email alone would need roughly 2,000+ sends a day.
- So the agency channel, the self-serve tier and inbound have to carry a large share.

| Milestone | Target timing | How |
|---|---|---|
| $25k/month | Month 6 | About 1,200 sends/day across 20 domains; 2 sub-niches; 8–10 agency partners; a part-time QA editor and an inbox VA |
| $50k/month | Month 9–12 | Self-serve **tracking tier at $99–299/month** built on the same engine (measurement only, no content), offered to everyone who gets a report but doesn't buy the Retainer; 20 agency partners; inbound from our own visibility for "AEO agency" questions |
| **$100k/month (about $1.2M/year)** | Month 12–18 | About 45 direct retainers at about $1,600 average ($72k) + about 35 white-label seats at $900 ($31k), plus tracking subscriptions. Team: 2 editors, 1 VA, 1 operations lead. For comparison, AEO Engine reports $135k MRR from 52 subscriptions (one verified data point) |

These timings are targets. The only real test is the funnel numbers each Monday.
