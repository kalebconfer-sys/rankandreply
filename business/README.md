# Start here

**The business:** *AI Visibility by Rank and Reply.* B2B buyers increasingly ask ChatGPT, Gemini, Perplexity and Claude "who should we use?" We measure whether a company gets recommended, show it who gets named instead, and fix that every month.

**Why this one:** It was researched from a cold start against eight other AI businesses. It's the only service model with an independently verified $100k+/month comparable (AEO Engine, $135k MRR). Buyers are already paying $1,500–$5,000/month for it. The first email can prove something true and specific about the reader. All of it sells without a sales call. Full reasoning and sources: [`01-research/market-research.md`](01-research/market-research.md).

**The money:**

| Price point | Amount | What it gets you |
|---|---|---|
| Free snapshot | $0 | Opens the conversation |
| Fix Plan | $490 | Entry sale |
| Retainer | $1,500/month | The core income |
| Agencies (white-label) | $900/month per client | The scale channel |

- **4 retainers ≈ $6k/month** (the starting goal).
- **67 retainers, or a mix of direct and agency clients, ≈ $100k/month.**

**What you do vs what the AI does:**
- **The AI** does the research, prospect research, the opening lines, the reports, the pages, the reply drafts and the weekly numbers review.
- **You** own the accounts and the money, approve what goes out, press send, and take a call only when a buyer asks for one. Plan on about 1.5–2 hours a day.

## Read in this order

1. [`02-plan/day-by-day.md`](02-plan/day-by-day.md): what to do tomorrow morning (day 1 is about 2 hours of account setup)
2. [`02-plan/30-day-plan.md`](02-plan/30-day-plan.md): the first month, week by week, with owners and finish lines
3. [`02-plan/90-day-plan.md`](02-plan/90-day-plan.md): the phases, the funnel math, the budget (about $340–490 in month 1), and the path to $100k/month
4. [`03-offer/offer.md`](03-offer/offer.md): exactly what we sell, the honest guarantee, and the unit economics
5. [`04-outreach/cold-email.md`](04-outreach/cold-email.md): why cold email failed before and the setup that fixes it, plus sequences, reply templates and legal checklist
6. [`04-outreach/marketplaces.md`](04-outreach/marketplaces.md): Upwork (main), Fiverr (this exact product already sells there), Contra, and which sites to skip
7. [`06-delivery/delivery-sop.md`](06-delivery/delivery-sop.md): how a client month gets done, and the QA checklist
8. [`05-ai-team/roles.md`](05-ai-team/roles.md): which AI does what; [`council-prompts.md`](05-ai-team/council-prompts.md) runs the council with just your subscriptions

## The tools (in [`tools/`](tools/))

| Tool | What it does |
|---|---|
| `council.py` | Runs one task across Claude, ChatGPT, Gemini, Perplexity and your local model. Modes: side-by-side answers, a debate with a written decision, cited research, and bulk work over a spreadsheet |
| `visibility.py` | The product. `enrich` → `probe` → `firstline` turns an Apollo export into verified, personalized opening lines. `snapshot` produces the client report (HTML/PDF) |
| `prompts/` | Templates for tagging replies, drafting replies, Upwork proposals, writing pages and QA |

Both tools were tested end to end against stand-in AIs. **They have not yet run against the real AI APIs.** That needs your keys and happens on day 2–3 of the plan.

## The customer-facing page

[`/ai-visibility/index.html`](../ai-visibility/index.html) is a new page that goes live at rankandreply.com/ai-visibility/ when this branch is merged. The existing contractor homepage is untouched. Whether to switch the homepage over is your call once the new offer has its first customers.

## Ground rules (they protect the business)

- **No results claims we can't back.** No fake reviews, testimonials or case studies. No ranking guarantees.
- **Cold email by the law:** a real name, a mailing address, an honest subject line, and an opt-out honored the same day.
- **Never send cold email from rankandreply.com or your Gmail.**
- **This repo is public.** Real leads, client data and API keys live only in `business/data/` and `business/tools/.env`. Both are gitignored, so they are never pushed.
