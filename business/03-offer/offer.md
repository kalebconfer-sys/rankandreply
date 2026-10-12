# The offer

**Product:** AI Visibility, from Rank and Reply
**One line:** When your buyers ask ChatGPT who to hire or what to buy, we measure whether you're named, and we do the work that gives you the best chance of being in the answer.
**Who it's for:** US B2B companies whose buyers shortlist vendors. Two test segments: software companies (10–200 people), and B2B service firms such as managed IT / cybersecurity providers and agencies.

## The ladder

| Step | Price | What they get | How it's sold | Delivered by |
|---|---|---|---|---|
| **Free snapshot** | $0 | 10 buyer questions, each asked **twice** on ChatGPT, Gemini, Perplexity and Claude (80 answers). Shows who gets named instead, the sites the engines cite, and the top 5 fixes | Reply "yes" to the cold email | `visibility.py snapshot --n 10 --runs 2 --pdf`, delivered within **2 business days** |
| **Fix Plan** | **$490 one-time** | 40 questions × 4 engines × 3 runs (480 answers); the sites the engines cite for the category and whether the client is on them; competitor breakdown; a 30-day fix roadmap; **2 publish-ready pages written for them** (e.g. a comparison page and a use-case page). Delivered in 5 business days. **Fully credited** to the first Retainer month if they upgrade within 30 days | Stripe Payment Link in the snapshot email and on the offer page | Engine + Claude drafts + your QA |
| **Visibility Retainer** | **$1,500/month**, month-to-month | Monthly tracking of 40 questions × 4 engines × 3 runs; **4 publish-ready pages a month**; listings and mentions work (we find the review sites and lists the engines cite, then prepare every submission and pitch); a technical fix spec (structured data, entity/about copy, FAQ markup); a monthly report showing the change since last month | Stripe subscription link | Engine + AI writers + your QA, about 3–4 hrs/client/month |
| **3-month Sprint** | **$3,900 prepaid** (saves $600) | The Retainer for 3 months, paid up front. AI answers often move slowly, so this suits buyers who want a fair test | Stripe Payment Link | Same as the Retainer |
| **Category Leader** | **$3,000/month**, month-to-month | 100 questions tracked; 8 pages a month; we run the outreach for third-party mentions; weekly competitor watch; quarterly refresh of existing pages | Stripe subscription link, or quoted for multi-product companies | Same, at double volume |

**Wholesale (agencies only, from day 46):** The Retainer delivered white-label for **$900/month per end client**. Reports carry the agency's name. Agencies set their own resale price. See [`../04-outreach/agency-partners.md`](../04-outreach/agency-partners.md).

**Capacity cap:** at most **5 Retainer clients** until a contract editor is hired. Above that, quality slips and the guarantee gets expensive.

## The guarantee (honest version)

> **We deliver what your plan lists, or you don't pay for what we missed.** A missed deliverable is credited at its share of the fee (for example, one page on the Retainer = $250) and delivered the following month. Time spent waiting on your approval or access doesn't count against us. Cancel any time by replying to any email from us.
>
> We don't promise rankings. Nobody controls what ChatGPT says, and anyone who guarantees it is guessing. What we promise is the work and an honest measurement of what it changed.

This follows the same "no results claims" rule as the original site. **Never break it in any email, proposal or page.** Describe the work and the measurement, never a promised outcome.

## Same product, every channel

Marketplace prices include the platform's fee, so the price per unit of work is the same everywhere.

| Scope | Direct (Stripe) | Upwork Catalog | Fiverr |
|---|---|---|---|
| Snapshot (10 questions × 4 engines × 2 runs, top 5 fixes) | Free (cold-email lead magnet) | $150 (Starter; also includes 3 named competitors) | $79 (Basic) |
| Standard audit (25 questions × 4 × 2, cited sites, top 5 fixes) | — | $350 | $199 |
| Fix Plan (40 × 4 × 3, roadmap, 2 pages) | $490 | $550 | $590 |

The snapshot is free in cold email because it's the cost of starting a conversation with someone who didn't ask. On a marketplace the buyer came looking, so it's paid.

## What we need from a client (all async, no call)

The onboarding form is sent automatically after payment (Tally or Google Forms; questions in `onboarding-form.md`):
1. Company, domain, and up to 5 competitors.
2. The 5 questions customers ask before buying.
3. Who the buyer is (title, company size, industry).
4. CMS access for publishing (a WordPress/Webflow editor invite), **or** "we'll publish ourselves" (we deliver Google Docs with copy and HTML ready to paste).
5. Two or three pieces of writing they like in their own voice.
6. One person who approves pages (by email).

## Unit economics (estimates; check against real bills in month 1)

| Item | Cost |
|---|---|
| Free snapshot (80 answers + extraction + findings) | about $2–5 in API calls |
| Cold-email probe | under $0.10 per lead (each distinct question asked twice; leads in one category share the question) |
| Retainer month: 480 engine answers at roughly $0.02–0.05 each, web search included | $10–25 |
| Retainer month: page writing and QA passes (Claude and ChatGPT) | $5–15 |
| Extraction and tagging (local model) | $0 |
| Your QA time per Retainer client | 3–4 hours (until a contract editor at about $25–40/hr takes it over) |
| **Gross margin on $1,500** | **about 95% before your time; about 85–90% with a paid editor** |

## Why someone buys this instead of...

| Alternative | Their price | Why we win |
|---|---|---|
| AI-visibility tracking tools (Otterly from about $29, Peec about $95, Profound $99–499+, Semrush AI $99) | $29–499/mo | They **measure**. We measure **and do the work**: pages, listings, fixes |
| AEO/GEO agencies | Typically $1,500–5,000+/mo per published agency pricing guides | Published prices, month-to-month, no calls, and a free report before you pay anything |
| Doing nothing / the SEO agency they already have | — | The snapshot shows who's being recommended for their buyers' questions today, so they can decide with real answers in front of them |
