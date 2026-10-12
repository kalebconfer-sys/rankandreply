# Freelance marketplaces: Upwork, Fiverr, Contra

Cold email is the main engine. Marketplaces bring three things it can't: **buyers who are already looking**, **reviews** (proof we otherwise don't have yet), and **possible revenue before the email domains finish warming** (day 15). The same `visibility.py` engine delivers every order, so a small marketplace order costs minutes, not hours.

## Which ones, ranked

| Rank | Marketplace | Worth it? | Why | Fee | Your time |
|---|---|---|---|---|---|
| 1 | **Upwork** | **Yes, but small** | Clients do post GEO/AEO work ([examples](../01-research/sources/demand-signals.md)). Project Catalog sells fixed packages with no proposal and no call. But the posts found so far are few, and several want 30+ hrs/week hires | 0–15% per contract; Catalog listings cost 0 Connects | 15 min/day |
| 2 | **Fiverr** | **Yes, as a review-builder and entry product** | Fiverr already has gigs for this exact service with tiered packages ([examples](../01-research/sources/demand-signals.md)), so the category exists there. **How much they sell couldn't be verified**, and one seller's large review count is self-reported. Fully async: buyers order and you deliver | **20%** of everything | 10 min/day |
| 3 | **Contra** | Yes, with low expectations | 0% commission to the freelancer; the client pays a small flat fee (third-party source). No volume data found | 0% | 1 hour to set up, then check weekly |
| — | Legiit (SEO marketplace) | Maybe, from month 2 | Its buyers are SEO agencies, which makes it a possible white-label channel. No reliable fee or volume data found | Unknown | — |
| ✗ | Freelancer.com, PeoplePerHour, SEOClerks | **No** | Race-to-the-bottom pricing | — | — |
| ✗ | Toptal and other vetted networks | **No** | Screening requires live interviews, which breaks the no-call rule | — | — |

**The rule that keeps this from eating your day:** list everywhere it's free and async (Upwork Catalog, Fiverr, Contra). Bid only on Upwork, **only on fixed-price posts**, and **at most 5 proposals a week**.

**Platform rules (hard limits):**
- **Marketplace deliverables contain no URL, email address, phone number or Stripe link.** That includes reports and PDFs: run the snapshot with `--prepared-by "Kaleb Confer"` for marketplace orders, and never send template A there.
- Never ask a marketplace client to pay or talk outside the platform. Upwork allows it only after paying its conversion fee. Fiverr suspends accounts for it.
- AI drafts proposals and you submit them by hand. **No bots that auto-submit.**
- Monthly clients from a marketplace stay on that marketplace: an Upwork monthly contract, or a Fiverr subscription. The fee is the cost of the lead.
- Don't apply for hourly roles you can't truthfully staff (for example 30+ hrs/week).

---

## Upwork

### Profile
**Title:** AI Search Visibility (GEO/AEO): Measure and Improve How ChatGPT, Gemini & Perplexity Answer Your Buyers

**Overview:**
> When your buyers ask ChatGPT for a recommendation, does your company come up? I measure it, and I do the work that gives you the best chance of being named.
>
> I ask ChatGPT, Gemini, Perplexity and Claude the questions your buyers actually ask, more than once each because answers vary, and show you who gets recommended instead of you, plus which review sites and lists the assistants are reading. Then I do the work: comparison and use-case pages written for you, listings and mentions prepared, and structured-data fixes specified. I measure again every month.
>
> What you can expect:
> - A report with the method printed on it, so you can check every number
> - Fixed prices, and async by default (calls only if you want one)
> - No ranking guarantees. Nobody controls what an AI says. I guarantee the work and an honest measurement
>
> I'm new to Upwork, so instead of reviews I'll show you your own results first.

**Skills tags:** Generative Engine Optimization, Answer Engine Optimization, SEO, AI Search, Content Strategy, Schema Markup, ChatGPT, Perplexity, Competitive Analysis.

### Project Catalog listing (0 Connects to list; buyers purchase directly)

**"AI Visibility Audit: do ChatGPT, Gemini, Perplexity & Claude recommend your business?"**

| Tier | Price | Includes | Delivery |
|---|---|---|---|
| Starter | $99 | 10 buyer questions × 4 engines × 2 runs, 3 named competitors, top 5 fixes, PDF report | 3 days |
| Standard | $249 | 25 questions × 4 engines × 2 runs, the sites the engines cite, top 5 fixes | 4 days |
| Advanced | $550 | The Fix Plan: 40 questions × 4 engines × 3 runs, 30-day roadmap, **2 publish-ready pages** | 6 days |

Prices match the direct prices plus the platform fee (see the table in [`../03-offer/offer.md`](../03-offer/offer.md)).

**Second listing (from week 3):** "AI-search-ready comparison or alternatives page, written and researched": $180 per page, or $600 for 4.

### Finding jobs
Perplexity and the other AIs **can't read Upwork job pages**, so use Upwork's own tools:
- Create **saved searches with email alerts** for `GEO`, `AEO`, `generative engine optimization`, `AI search visibility`, `ChatGPT visibility`, `LLM SEO`, `AI Overviews`. Filter: fixed price, payment verified.
- When an alert arrives, paste the post text into a CSV column `post` (and the probe result into `probe` if you ran one). Then draft with Claude:
  ```bash
  python council.py bulk --in ../data/upwork/posts.csv --prompt prompts/upwork_proposal.txt --out ../data/upwork/proposals.csv --column proposal --ai claude
  ```
- Read each draft, edit it, and submit by hand.

**Bid on:**
- Fixed-price audits and AI-search content jobs.
- Agencies asking for GEO help that would accept a fixed-price, white-label arrangement.
- Posts that name the company's website (so you can run the probe first).

**Skip:**
- Hourly roles of 30+ hrs/week.
- Posts that demand years of documented GEO case studies, until we have some.
- Anything under $100.
- "Reddit marketing" posts that want fake accounts or undisclosed promotion.

**Connects budget:** 5 proposals/week × about 6–16 Connects × $0.15 ≈ **$20–50/month**.

### The proposal that stands out: show their result first

When the post names the company or website, run a small probe before writing:
```bash
python visibility.py snapshot --brand "TheirCo" --domain theirco.com --n 5 --engines chatgpt,perplexity --prepared-by "Kaleb Confer"
```
Open with the finding, quoted exactly from the report. Never paraphrase it into something stronger.

### Two real posts to start with (check they're still open)

These came from search results on 2026-10-12 and couldn't be opened from here. **Open each one, check it's still accepting proposals, and re-read the full post** before sending. Edit the draft to match.

**1. "GEO / AI Search Visibility Specialist – Get Clients Cited by ChatGPT, Claude, Perplexity & Google AI"**
An agency launching a GEO service ([post](https://www.upwork.com/freelance-jobs/apply/GEO-Search-Visibility-Specialist-Get-Clients-Cited-ChatGPT-Claude-Perplexity-Google_~022106528246978264059/)). It's posted as a 30+ hrs/week hourly role, so **don't apply for that role.** Send a proposal that offers a different arrangement only if the post invites proposals beyond that role; otherwise skip it and pitch agencies like this through [`agency-partners.md`](agency-partners.md).

> Hi, you're launching GEO for clients, so the hardest part will be proving it worked. That's the part I've built.
>
> I'm not able to commit 30 hours a week, so this is a different offer: fixed-price, white-label delivery per client. For each client I run their buyer questions through ChatGPT, Gemini, Perplexity and Claude via their APIs (web search on, more than once each, because answers vary) and produce a report under your agency's name: how often they're named, who's named instead, which sites the engines cite, and the five highest-impact fixes. Same questions every month, so you get a clean before/after. I also write the fix content.
>
> To be straight with you: I'm new on Upwork and don't have a client case study yet. I'd rather show than claim. Which client should I run first?
>
> Kaleb

**2. "SEO Specialist (SEO/AEO/GEO) for Home Services"** ([post](https://www.upwork.com/freelance-jobs/apply/SEO-Specialist-SEO-AEO-GEO-for-Home-Services_~022088409054895657873/)). **Bid only if it's fixed-price or a small hourly scope.** Re-read the post for the business name and city; if they're listed, run the probe with `--region "<city, state>"` and paste the real result into line one.

> Hi, I asked ChatGPT "[best <service> company in <city>]" and it named [A], [B] and [C]. [Your company wasn't one of them / You came up]* That's the gap I work on.
>
> For home-services businesses, the assistants lean on the Google Business Profile, review volume and replies, local directories, and pages that answer "how much does X cost in <city>" directly. My monthly work: measure the questions your customers ask across ChatGPT, Gemini, Perplexity and Claude, write the pages that answer them, tighten the profile and listings, and report the change every month. No ranking promises; nobody can make them honestly.
>
> I'm new to Upwork, so judge the work rather than my profile: the full 10-question report for your business is the Starter package in my catalog. Want me to start with that?
>
> Kaleb
>
> *Only include this sentence if you actually ran the question and the report says so. Never guess.

---

## Fiverr

**Gig title:** I will audit your AI visibility on ChatGPT, Gemini, Perplexity and Claude
**Category:** Digital Marketing → SEO → (GEO / AI search, if offered)

| Package | Price | Includes | Delivery |
|---|---|---|---|
| Basic | $99 | 10 buyer questions × **4** engines × 2 runs, 3 competitors, top 5 fixes, PDF | 3 days |
| Standard | $249 | 25 questions × 4 engines × 2 runs, the sites the engines cite, top 5 fixes | 4 days |
| Premium | $590 | The Fix Plan: 40 questions × 4 engines × 3 runs, 30-day roadmap, 2 publish-ready pages | 6 days |

**After the 20% fee:** $79 / $199 / $472. API cost per order: about $2–5 (Basic and Standard) and $15–30 (Premium). Your time: 15–40 minutes for Basic and Standard; the Premium follows the Fix Plan steps in [`../06-delivery/delivery-sop.md`](../06-delivery/delivery-sop.md).

**Gig requirements (asked automatically at order):** website, company name, up to 3 competitors, who your buyer is, any questions you know buyers ask.

**Description (short):**
> When buyers ask ChatGPT for a recommendation, do you make the list? I put your buyers' real questions to ChatGPT, Gemini, Perplexity **and** Claude, more than once each, and show you how often you're named, who's named instead, and what to fix. Method and date printed on every report. No ranking guarantees, just honest measurement and a clear fix list.

**Gig extras:** +1 publish-ready comparison page ($150); faster delivery (+$40); monthly re-check subscription if Fiverr offers subscriptions in the category.

**Launch tactic:** Deliver early and do it well, then ask politely for a review in the delivery message. **Never offer anything in exchange for a review**: it's against Fiverr's rules and ours.

---

## Contra
- Free profile, using the same copy as Upwork.
- List the Fix Plan ($490) and Retainer ($1,500/month) at direct prices. Contra charges you 0%.

---

## Realistic targets (first 30 days)

| Week | Upwork | Fiverr | Contra |
|---|---|---|---|
| 1 | Profile, Catalog and saved-search alerts live | Gig live | Profile live |
| 2–4 | Up to 5 fixed-price proposals a week | Deliver any orders early | Check weekly |
| **By day 30** | **1–2 orders or contracts** | **1–3 orders** | 0 |

If a marketplace hasn't produced an order by day 45, stop spending time on it and keep the listing up passively.
