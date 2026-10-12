# Source report: AI business-model benchmarks (2026-10-12)

Research agent report, kept close to as written. "UNVERIFIED" and "self-reported" labels are the agent's.

## Headline findings
- **Only one service model on the list has a third-party-verified $100k+/month business.** It is AI SEO / AEO: **AEO Engine** shows $135,128 MRR (Stripe-verified), 52 active subscriptions and $1,597–$10,000/month pricing ([TrustMRR](https://trustmrr.com/startup/aeo-engine), [pricing](https://aeoengine.ai/pricing)).
- **Typical outcomes are small.** In a dataset of 3,787 bootstrapped SaaS businesses, median revenue is **$145/month** and only 6.1% pass $10k MRR ([BigIdeasDB](https://bigideasdb.com/state-of-indie-saas-revenue-2026)).
- **"Weekly GBP posts + review replies" does not support $800–$1,500/month.** Software does it for $30–99 per location, and done-for-you agencies mostly charge $125–400.

## Model by model

| Model | Best revenue evidence | Price | Saturation | No-call fit | AI-deliverable |
|---|---|---|---|---|---|
| (a) AI automation agency (n8n/Make) | Anecdotes and self-reported ($25k MRR [Medium](https://medium.com/write-a-catalyst/how-one-entrepreneur-hit-25k-mrr-in-4-months-with-n8n-and-sales-skills-02c9c49484db); Saraev $72k/mo is self-promotion) | $40–100/hr; rate cards claim $1.8–4.5k builds (unverified) | High at the generic end | Poor: custom scoping means calls | Partly: builds need debugging |
| (b) Pre-built website preview outreach | None documented | $500–2k one-time | Already a $49–199/mo tool ([ClaimSite](https://www.indiehackers.com/post/i-built-a-tool-that-generates-a-live-website-for-a-local-business-before-you-contact-them-qoZTIOY6f8DC83FRfxmP), [LocalScout](https://www.localscout.online/)) | Good | High |
| (c) GBP management + AI review replies | Merchynt/Paige about $2M (Latka estimate, unverified) | $30–99 software; $125–400 done-for-you | **Very high**: bundled into Semrush Local ($30) and GHL ($97) | Good | Very high, which is why it's cheap |
| (d) AI receptionist / missed-call text-back | Rosie $1M ARR (VC-backed team); small resellers $49–200 MRR ([TrustMRR](https://trustmrr.com/startup/call-to-ai)) | $49–99 SaaS | **Very high**: Jobber builds it in | Poor for an agency: phone setup | High |
| (e) Database reactivation (AI SMS) | Vendor case studies only | Pay per appointment | High in GHL circles | Poor: needs client data | High; TCPA risk |
| (f) Document / data extraction | Bank Statement Converter, solo self-serve, $9–16k MRR ([Starter Story](https://www.starterstory.com/stories/bankstatementconverter)) | SaaS tiers | Medium | **Good** | High |
| (g) Niche lead lists / data | BuiltWith (co-founded; about $22M, about 4 staff) | $99/county/mo ([permits.llc](https://permits.llc/)); raw data $3 per 1k on Apify | Commoditizing | Good | High |
| (h) AI SEO / AEO for B2B | **AEO Engine, $135k MRR, verified**; Outrank claims $300k MRR (self-reported) | $1,597–10,000/mo | Rising | **Good**: published pricing, month-to-month | High, with human QA |
| (i) Micro-SaaS built with AI | Median $145/mo | — | — | Good | Security risk: [CVE-2025-48757](https://thenextweb.com/news/lovable-vibe-coding-security-crisis-exposed); about 40% of 5,000 vibe-coded apps leaked data |
| (j) White-label fulfilment for agencies | 51Blocks $210k/mo, but 30 staff ([Starter Story](https://www.starterstory.com/stories/we-make-2-5m-year-selling-white-label-seo-wordpress-hosting)) | GBP wholesale $49–99 per location; SEO $300–5k | Medium–high | Good: agencies buy wholesale | High |

## GBP post / review-reply competitor pricing

| Tool / service | Price |
|---|---|
| Semrush Local (AI posts + review auto-replies) | $30/location/mo, $60 Pro ([Semrush](https://www.semrush.com/pricing/local/)) |
| Localo | $39–49/mo |
| BrightLocal | $41–65/location |
| Merchynt Paige | $99/profile/mo after a $1 trial ([Merchynt](https://intercom.help/merchynt/en/articles/9350578-paige-billing-guide)) |
| GoHighLevel AI Employee | $97/sub-account |
| Birdeye / Podium | $299–599/mo, annual contract, sold on calls |
| Done-for-you GBP management | $125–400 per profile ([Merchynt blog](https://www.merchynt.com/post/google-my-business-management-pricing)) |
| Full managed local SEO | $799–1,299/location ([BrightLocal](https://www.brightlocal.com/blog/introducing-brightlocal-local-seo-services/)) |

**Verdict:** $800–1,500/month is the price of full local SEO, not posts plus replies.

## Sold without a call (documented)
- **Designjoy:** $0 to $120k/month with no sales calls; checkout on the site, work handled asynchronously in Trello ([Indie Hackers](https://www.indiehackers.com/post/how-designjoy-got-from-0-to-120k-month-with-no-paid-advertising-a31375fce0)).
- **Other self-serve sellers:** Paige ($1 trial), Localo (free trial), Bank Statement Converter and permits.llc.
- **The gap:** Birdeye and Podium require sales calls, which leaves room for a competitor that sells without them.

## Agent's ranking
1. **Productized AI SEO/AEO retainer for one B2B niche.** Biggest risk: Google enforcement against scaled AI content; needs human QA.
2. **White-label GBP/review fulfilment for agencies.** Biggest risk: commoditization at $30–99.
3. **Document extraction (self-serve or async).** Biggest risk: accuracy and data-security liability.
