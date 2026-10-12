# Freelance marketplaces: Upwork, Fiverr, Contra

Cold email is the main engine. Marketplaces bring three things it can't: **buyers who are already looking**, **reviews** (proof we otherwise don't have yet), and **revenue before the email domains finish warming** (day 15). The same `visibility.py` engine delivers every order, so a cheap marketplace order costs minutes, not hours.

## Which ones, ranked

| Rank | Marketplace | Worth it? | Why | Fee | Your time |
|---|---|---|---|---|---|
| 1 | **Upwork** | **Yes, the main marketplace** | Clients post GEO/AEO jobs right now (examples below). Project Catalog listings sell fixed packages with no proposal and no call. Larger budgets than Fiverr | 0–15% per contract; Catalog listings cost 0 Connects | 20–30 min/day |
| 2 | **Fiverr** | **Yes, as a review-builder and entry product** | **This exact product already sells there**: gigs like "I will audit your AI visibility in ChatGPT, Perplexity, Google" use tiered packages ([example](https://fiverr.com/sam2406/audit-your-ai-visibility-in-chatgpt-perplexity-google), [example](https://fiverr.com/mahamwebs/optimize-your-website-for-ai-search-on-chatgpt-perplexity-and-gemini)). One seller claims thousands of reviews (self-reported). Fully async: buyers order and you deliver | **20%** of everything | 10 min/day |
| 3 | **Contra** | Yes, but low expectations | 0% commission to the freelancer; the client pays a small flat fee ([source](https://www.jobbers.io/best-commission-free-marketplaces-for-freelancers-in-2026-keep-100-of-your-earnings/)). Lists full-price packages. No volume data found | 0% | 1 hour to set up, then check weekly |
| — | Legiit (SEO marketplace) | Maybe, from month 2 | Its buyers are SEO agencies, which makes it a possible white-label channel. No reliable fee or volume data found. Test only after the first 5 reviews elsewhere | Unknown | — |
| ✗ | Freelancer.com, PeoplePerHour, SEOClerks | **No** | Race-to-the-bottom pricing; buyers who want $5 work | — | — |
| ✗ | Toptal and other vetted networks | **No** | Screening requires live interviews, which breaks the no-call rule | — | — |

**The rule that keeps this from eating your day:** list everywhere it's free and async (Upwork Catalog, Fiverr, Contra), but **actively bid only on Upwork**.

**Platform rules (hard limits):**
- Never ask a marketplace client for an email, phone number or outside payment before or during a contract. Both Upwork and Fiverr suspend accounts for this. Upwork allows moving off-platform only after paying its conversion fee.
- AI drafts proposals and you submit them by hand. **No bots that auto-submit.**
- Monthly clients from a marketplace stay on that marketplace: an Upwork hourly or monthly contract, or a Fiverr subscription. The fee is the cost of the lead.

---

## Upwork

### Profile
**Title:** AI Search Visibility (GEO/AEO): Get Recommended by ChatGPT, Gemini & Perplexity

**Overview:**
> When your buyers ask ChatGPT for a recommendation, does your company come up? I measure it and fix it.
>
> I ask ChatGPT, Gemini, Perplexity and Claude the questions your buyers actually ask, several times each, and show you exactly who gets recommended instead of you, plus which review sites and lists the assistants are reading. Then I do the work: comparison and use-case pages written for you, listings and mentions prepared, and structured-data fixes specified. I measure again every month.
>
> What you can expect:
> - A report with the method printed on it, so you can check every number
> - Published fixed prices, and async by default (calls only if you want one)
> - No ranking guarantees. Nobody controls what an AI says. I guarantee the work and an honest measurement
>
> New to Upwork, so instead of reviews I'll show you your own results first. Send me your website and I'll tell you what ChatGPT says about your category.

**Skills tags:** Generative Engine Optimization, Answer Engine Optimization, SEO, AI Search, Content Strategy, Schema Markup, ChatGPT, Perplexity, Competitive Analysis.

### Project Catalog listing (0 Connects to list; buyers purchase directly)

**"AI Visibility Audit: do ChatGPT, Gemini, Perplexity & Claude recommend your business?"**

| Tier | Price | Includes | Delivery |
|---|---|---|---|
| Starter | $150 | 10 buyer questions × 4 engines, 3 competitors, top 3 fixes, PDF report | 2 days |
| Standard | $350 | 25 questions × 4 engines × 2 runs, the sites the engines cite, top 5 fixes | 3 days |
| Advanced | $750 | 40 questions × 4 engines × 3 runs, 30-day roadmap, **2 publish-ready pages** | 5 days |

**Second listing (from week 3):** "AI-search-ready comparison or alternatives page, written and researched": $180 per page, or $600 for 4.

### Finding jobs (the Scout's daily search)
Saved searches: `GEO`, `AEO`, `generative engine optimization`, `AI search visibility`, `ChatGPT visibility`, `LLM SEO`, `AI Overviews`, `answer engine`. Also look at `SEO content` posts that mention AI.

**Bid on:**
- Fixed-price audits and content jobs.
- Agencies hiring GEO help (each one is a white-label partner prospect).
- Companies that name their website in the post (you can run the probe first).

**Skip:**
- Posts that demand years of documented GEO case studies until we have some.
- Anything under $100.
- "Reddit marketing" posts that want fake accounts or undisclosed promotion.

### The proposal that stands out: show their result first

When the post names the company or website, run the probe before writing:
```bash
python visibility.py snapshot --brand "TheirCo" --domain theirco.com --n 5 --engines chatgpt,perplexity
```
Then open with the finding. AI drafts the proposal with `prompts/upwork_proposal.txt`, you read it, and you submit by hand.

### Three real posts to start with

These came from search results on 2026-10-12. The pages themselves couldn't be opened from here, so **open each one, check it's still accepting proposals, and re-read the full post** before sending. Edit the draft to match.

**1. "GEO / AI Search Visibility Specialist – Get Clients Cited by ChatGPT, Claude, Perplexity & Google AI"**
An agency launching a GEO service; hourly, 30+ hrs/week, 6+ months ([post](https://www.upwork.com/freelance-jobs/apply/GEO-Search-Visibility-Specialist-Get-Clients-Cited-ChatGPT-Claude-Perplexity-Google_~022106528246978264059/)). They ask for an example of a brand you got mentioned in an AI answer. We don't have one yet, so we don't pretend. We offer the measurement system instead.

> Hi, you're launching GEO for clients, so the hardest part is proving it worked. That's the part I've built.
>
> I run each client's buyer questions through ChatGPT, Gemini, Perplexity and Claude via their APIs (web search on, several runs each, because answers vary) and produce a client-ready report: how often they're named, who's named instead, which sites the engines cite, and the five highest-impact fixes. Same questions every month, so you get a clean before/after.
>
> To be straight with you: I'm new on Upwork and don't have a client case study to show yet. So send me one of your clients' websites (or your own) and I'll run a free report within 48 hours. You can judge the work, not the claims. It can carry your agency's name.
>
> Beyond reporting, I write the fix content: comparison/alternatives pages, FAQ content, structured-data specs and listing submissions, with each piece checked by hand before it reaches you.
>
> Which client should I run first?
> Kaleb

**2. "SEO Specialist (SEO/AEO/GEO) for Home Services"** ([post](https://www.upwork.com/freelance-jobs/apply/SEO-Specialist-SEO-AEO-GEO-for-Home-Services_~022088409054895657873/)). Re-read the post for the business name and city. If they're listed, run the probe with `--region "<city, state>"` and paste the real result into line one.

> Hi, I asked ChatGPT "[best <service> company in <city>]" and it named [A], [B] and [C]. [Your company wasn't one of them / You came up third].* That's the gap I close.
>
> For home-services businesses, the assistants lean on the Google Business Profile, review volume and replies, local directories, and pages that answer "how much does X cost in <city>" directly. My monthly work: measure the questions your customers ask across ChatGPT, Gemini, Perplexity and Claude, write the pages that answer them, tighten the profile and listings, and report the change every month. No ranking promises; nobody can make them honestly.
>
> I'm new to Upwork, so I'll start with a free 10-question report for your business so you can judge the work first. Want it?
> Kaleb
>
> *Only include this sentence if you actually ran the question. Never guess.

**3. "Fractional Head of SEO and AEO"** for an IT services firm ([post](https://www.upwork.com/freelance-jobs/apply/Fractional-Head-SEO-and-AEO_~022086849833496747381/)). This is a 30+ hrs/week leadership role, a stretch for a new account. Bid only if the post allows a smaller AI-visibility scope. Lead with the probe result for "best managed IT provider in <their area>" and propose the Retainer scope as the AEO half of the role.

---

## Fiverr

**Gig title:** I will audit your AI visibility on ChatGPT, Gemini, Perplexity and Claude
**Category:** Digital Marketing → SEO → (GEO / AI search, if offered; Fiverr groups GEO, AEO and LLM SEO together)

| Package | Price | Includes | Delivery |
|---|---|---|---|
| Basic | $79 | 10 buyer questions × **4** engines (most gigs check 3), 3 competitors, top 3 fixes, PDF | 2 days |
| Standard | $199 | 25 questions × 4 engines × 2 runs, the sites the engines cite, top 5 fixes | 3 days |
| Premium | $449 | 40 questions × 4 engines × 3 runs, 30-day roadmap, 1 publish-ready page | 5 days |

**After the 20% fee:** $63 / $159 / $359. API cost per order: $1–15. Your time: 10–40 minutes (skim, QA, send).

**Gig requirements (asked automatically at order):** website, company name, up to 3 competitors, who your buyer is, any questions you know buyers ask.

**Description (short):**
> When buyers ask ChatGPT for a recommendation, do you make the list? I put your buyers' real questions to ChatGPT, Gemini, Perplexity **and** Claude, several times each, and show you how often you're named, who's named instead, and exactly what to fix. Method and date printed on every report. No ranking guarantees, just honest measurement and a clear fix list.

**Gig extras:** +1 publish-ready comparison page ($120); 24-hour delivery (+$40); monthly re-check subscription if Fiverr offers subscriptions in the category.

**Launch tactic:** The first orders matter most for Fiverr's ranking. Deliver early, over-deliver one extra fix, and ask politely for a review in the delivery message. **Never offer anything in exchange for a review**: it's against Fiverr's rules and our own.

---

## Contra
- Free profile, using the same copy as Upwork.
- List two services at **full** prices: Fix Plan $490 and Retainer $1,500/month. Contra charges you 0%.
- Link the Contra profile from the website footer later as social proof once reviews exist.

---

## Weekly marketplace targets (first 30 days)

| Week | Upwork | Fiverr | Contra |
|---|---|---|---|
| 1 | Profile and Catalog live; 10 proposals | Gig live | Profile live |
| 2 | 15 proposals | — | — |
| 3 | 15 proposals; 2nd Catalog listing | Add gig extras | — |
| 4 | 15 proposals | Review the first orders | — |
| **Goal by day 30** | **2–4 orders or contracts, 2+ five-star reviews** | **3+ orders** | 0–1 |
