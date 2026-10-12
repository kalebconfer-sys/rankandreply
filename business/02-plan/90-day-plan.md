# The 90-day plan

**Goal:** $5,000+/month by day 60–75, and a machine that keeps compounding. **Stretch:** $10,000/month by day 90.
**Business:** AI Visibility by Rank and Reply. See [`../01-research/market-research.md`](../01-research/market-research.md) for why.
**Your time:** about 1.5–2 hours/day. You never cold-call. Calls happen only when a buyer asks for one.

## The three phases

| Phase | Days | Theme | Must be true at the end |
|---|---|---|---|
| **1. Build and warm** | 1–14 | Accounts, keys, engine tested on real companies, inboxes warming, marketplaces live | 15 inboxes warmed; 10 real snapshots run (on companies we pick, not clients); offer page live; Upwork/Fiverr/Contra live; 25 Upwork proposals sent |
| **2. Launch and learn** | 15–45 | Cold email live in two segments; every "yes" gets a report within 24 hours | 3,000+ sends; 25+ reports delivered; **first paying customers**; one segment chosen by reply data |
| **3. Double down and systematize** | 46–90 | More volume in the winning segment, agency white-label channel, automation of the manual steps | **$5k+/month recurring**; reply-to-report fully automated; first real case study (with permission) |

## Funnel math (assumptions, replaced by real numbers every Monday)

| Step | Conservative | Base | Good | Source of the assumption |
|---|---|---|---|---|
| First-touch emails per month (from month 2) | 4,500 | 5,000 | 6,000 | 15 inboxes × 15–20/day × about 21 sending days |
| "Yes, send it" replies | 0.4% | 0.7% | 1.5% | Instantly 2026 average reply rate is 3.43% across all replies; positive replies are a fraction of that. The asset-first offer is untested |
| Report → Fix Plan ($490) | 5% | 8% | 12% | Untested estimate |
| Report → Retainer directly | 2% | 3% | 5% | Untested estimate |
| Fix Plan → Retainer within 30 days | 20% | 30% | 40% | The Fix Plan price is credited to month one |
| Marketplace revenue per month | $300 | $800 | $2,000 | Upwork plus Fiverr, small orders |

**What base case means:**
- **Month 2:** about 35 reports → about 3 Fix Plans ($1,470) + about 2 retainers ($3,000 MRR) + marketplaces ($800). That's **about $5,300** in the month.
- **Month 3:** about 45 reports (better copy) → about 4 Fix Plans ($1,960) + 2–3 new retainers (about 5 in total, $7,500 MRR), plus 1–2 agency partners (+$900–1,800) and marketplaces. That's **about $10,000–12,000** in the month.

**What conservative case means:** about $2,500–3,500/month by day 90. That triggers the kill criteria in the research doc: the council reviews the segment, the copy and the offer before any more spend.

These are planning numbers, not promises. They exist so that every Monday we can see which step of the funnel is underperforming and fix that step.

## Phase 1: Build and warm (days 1–14)

Day-by-day steps are in [`day-by-day.md`](day-by-day.md).

- **Money:**
  - Stripe account.
  - Two Payment Links: Fix Plan $490 one-time, Retainer $1,500/month.
  - A virtual mailbox address for the email footer.
- **AI:**
  - API keys for Claude, ChatGPT, Gemini and Perplexity in `business/tools/.env`.
  - Ollama installed with `llama3.1:8b`.
  - `council.py status` shows all five AIs ready.
- **Email:**
  - 5 sending domains and 15 inboxes, warming in Instantly from day 1–2.
  - Apollo and MillionVerifier accounts.
- **Proof:** Run `visibility.py snapshot` on **10 real companies** across both segments. You're not selling to them yet. This does three things:
  1. Tests the engine with real APIs.
  2. Shows us the real cost per report.
  3. Gives us our own data: "In 10 software companies we checked, the median was named in X% of answers." That's a true, citable line for emails.
- **Marketplaces:** Upwork profile, Project Catalog listing and the first 25 proposals. Fiverr gig. Contra profile.
- **Site:** Merge the branch so rankandreply.com/ai-visibility/ goes live, with the Stripe links swapped in.

## Phase 2: Launch and learn (days 15–45)

- **Sending:**
  - Ramp 75 → 150 → 225 sends/day (see the ramp in [`../04-outreach/cold-email.md`](../04-outreach/cold-email.md)).
  - Split 70/30 between Segment A (software) and Segment B (B2B services).
- **Every "yes" gets its report within 1 business day.** Speed is the product. Run the snapshot, skim the PDF, send template A.
- **Monday council review:**
  - Gemini (Analyst) reads the week's sends, replies and sales.
  - ChatGPT (Critic) attacks the weakest step.
  - Claude (Chair) picks **one** change for the week.
  - You approve it.
- **Day 30 checkpoint:**
  - Pick the winning segment: higher "yes" rate × higher report-to-paid rate. The loser drops to 10% of volume.
  - If the positive reply rate is under 0.3% in both, rewrite the hook before sending more. Use a council debate with the reply CSV attached.
- **First client delivery:** follow [`../06-delivery/delivery-sop.md`](../06-delivery/delivery-sop.md). Every first delivery gets extra QA time, because these clients become the case studies.

## Phase 3: Double down and systematize (days 46–90)

- **Volume:** Add 5 more domains / 15 more inboxes (warm 14 days), taking sending to about 450–600/day in the winning segment.
- **Niche depth:** Inside the winning segment, split by sub-category (for example "HR software" vs "dev tools") and keep a separate copy variant for each. The best-replying sub-category gets more volume.
- **Agency white-label channel (from day 46):**
  - Target: marketing agencies with 5–50 staff that sell SEO to B2B or local clients.
  - Offer: the Retainer at **$900/month per end client**, reports in the agency's name (`--prepared-by "Agency Name"`).
  - Hook: run the snapshot on one of the agency's own clients (picked from its portfolio page) and send the agency the result.
  - Goal: 3 agencies with at least 1 client each by day 90.
- **Automation (remove you from the repetitive steps):**
  - The Instantly reply webhook triggers n8n (or a small script). It classifies the reply with the local model, runs the snapshot automatically when the reply is "yes", and drafts the reply email with the PDF attached. **You approve with one click** instead of doing each step.
  - Stripe payment sends the onboarding form; the form submission creates the client folder and runs the first tracking report.
  - Monthly client reports run on a schedule (`snapshot --compare last-month/raw.json`).
- **Proof:**
  - Ask the first two retainer clients for permission to publish an anonymized before/after.
  - Add it to the page and the emails. Proof is the single biggest lift available to cold email.
  - Until then, **we publish no results claims.**

## Weekly rhythm (from week 3)

| When | What | Who |
|---|---|---|
| Daily, morning (30 min) | Tag replies, approve drafts, send reports, check bounces | Worker tags, Chair drafts, **you** approve |
| Daily, any time (20 min) | Today's leads: Apollo export → verify → enrich → probe → firstline → upload | **You** run 5 commands; the AI does the rest |
| Daily (20 min) | Upwork: Scout finds posts, Chair drafts proposals, **you** submit 3 | Perplexity, Claude, you |
| Monday (45 min) | Council review: numbers, the weakest step, one change | Gemini, ChatGPT, Claude, **you** |
| Friday (15 min) | Fill in the scoreboard ([`templates/scoreboard.csv`](templates/scoreboard.csv)) | You |

## Budget

| Item | Month 1 | Months 2–3 |
|---|---|---|
| 5 domains (yearly) | $70 | — |
| 15 Google inboxes | $55–125 | $55–125 |
| Instantly Growth | $47 | $47 |
| Apollo Basic | $49–65 | $49–65 |
| MillionVerifier | $37 | $37 |
| Virtual mailbox | $10–15 | $10–15 |
| AI APIs (10 test snapshots, probes, reports) | $50–100 | $75–150 |
| Upwork Connects / Freelancer Plus | $20–30 | $20–30 |
| Stripe, Fiverr, Contra | $0 (fees come out of sales) | — |
| **Total** | **about $340–490** | **about $300–470/month** |

Phase 3 adds 5 more domains and 15 inboxes: about +$125/month.

## After day 90: the path to $100k/month

| Milestone | Target timing | How |
|---|---|---|
| $25k/month | Month 6 | 900 sends/day across 15 domains; 2 sub-niches; 8–10 agency partners; a part-time QA editor ($25–40/hr) and an inbox VA |
| $50k/month | Month 9–12 | Self-serve **tracking tier at $99–299/month** built on the same engine (measurement only, no content), sold to everyone who gets a report but doesn't buy the Retainer; 20 agency partners; our own AI visibility for "AEO agency" questions as inbound |
| **$100k/month (about $1.2M/year)** | Month 12–18 | About 45 direct retainers at about $1,600 average ($72k) + about 35 white-label seats at $900 ($31k), plus tracking subscriptions. Team: 2 editors, 1 VA, 1 operations lead. For comparison, AEO Engine reports $135k MRR from 52 subscriptions (verified) |

These timings are targets. The only real test is the funnel numbers each Monday.
