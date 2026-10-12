# Agency partners (white-label): the scale channel

**Start:** day 46, once at least 2 clients have been delivered and the delivery steps have run cleanly twice.
**Why:** One agency can bring 3–20 end clients. Agencies already buy fulfilment wholesale by email, and their clients are asking them about ChatGPT. The research found an agency on Upwork right now hiring a 30+ hrs/week GEO specialist for 6+ months ([source](../01-research/sources/marketplaces.md)). Agencies need this capability and would rather not build it.

## The offer to agencies

| | |
|---|---|
| **What they resell** | The Retainer: 40 questions × 4 engines tracked monthly, 4 pages/month, listings and mentions work, structured-data spec, monthly report |
| **Wholesale price** | **$900/month per end client**, month-to-month. First client's first month at $450 so the agency can test it with low risk |
| **What agencies typically charge** | $1,500–$3,000/month (their price, their call) |
| **White-label** | Reports carry the agency's name (`visibility.py snapshot --prepared-by "Agency Name"`). We never contact their client unless they ask us to |
| **Free tool for their sales** | Unlimited snapshots on prospects for agencies with 2+ active clients, so they can open their own deals with real data |
| **Payment** | Stripe subscription, one line item per end client |

**Margin check:** at $900 we keep about $860 after API costs, minus about 3 hours of QA. That's still about $750+ even with a paid editor at $35/hr.

## Who to target

| Filter | Value |
|---|---|
| Type | Marketing agencies that sell SEO, content or web design to B2B or local-service clients |
| Size | 3–50 staff (owner still reads email; no procurement department) |
| Signals | "SEO" or "content marketing" on the services page; a client portfolio or case-study page (we need one client to run a snapshot on) |
| Not | Agencies that already advertise GEO/AEO as a service (they compete, they don't buy); pure paid-ads shops |
| Where | Apollo: Industry = Marketing & Advertising, Keywords = "SEO", Employees 3–50, Titles = Founder, Owner, CEO, Managing Director, Head of SEO |

## The hook: run it on their client

1. From the agency's portfolio page, pick one client.
2. Run a 5-question probe on that client:
   ```bash
   python visibility.py snapshot --brand "Client" --domain client.com --n 5 --engines chatgpt,perplexity --prepared-by "Agency Name"
   ```
3. The email leads with that client's result. Agencies care about anything that lets them look good to a client or sell more to them.

## The sequence

**Email 1 (day 0)**
Subject: `{{client_name}} on ChatGPT`

> Hi {{first_name}},
>
> I asked ChatGPT and Perplexity five questions {{client_name}}'s buyers would ask. They were named in {{rate}}% of answers; {{competitor}} came up in {{competitor_rate}}%.
>
> If {{client_name}} hasn't asked you about AI search yet, they will. I do the measuring and the fix work white-label: reports in {{agency}}'s name, $900/month wholesale per client, month-to-month. You keep the relationship and set your own price.
>
> Want the full report for {{client_name}}, branded as {{agency}}? Free.
>
> Kaleb Confer
> Rank and Reply

**Email 2 (day 4)**

> {{first_name}}, the short version of how it works: you sell it, we deliver it, and every report and page goes out under your name. Nothing reaches your client without your approval. The first client's first month is $450 so you can test it without much risk. Happy to send the {{client_name}} report either way.
>
> Kaleb

**Email 3 (day 9)**

> Last note, {{first_name}}. If AI search isn't something you want to offer yet, no problem. If it is, reply "send it" and the branded {{client_name}} report is yours.
>
> Kaleb

Footer and compliance: the same as [`cold-email.md`](cold-email.md) §3 and §5.

**Run this as its own campaign from its own inboxes.** Agency reply patterns differ, and their numbers shouldn't mix with the direct segments.

## After a "yes"

1. Run the full 20-question snapshot with `--prepared-by "{{agency}}"` and send the PDF within 1 business day.
2. Then send the partner page: pricing, process, what they get each month and what we need from them. Write it as a Google Doc first. Make it a web page later if the channel works.
3. **Onboarding is async:** the agency fills in the same onboarding form per end client and adds "agency" + "white-label name" fields.

## Rules that protect the relationship

- **Never** contact an agency's client directly, or pitch them our own direct offer, even after the agency leaves. Put it in writing in the partner terms.
- The agency sets its retail price. We don't publish their margin.
- Our public pricing page shows "white-label available: email for wholesale pricing" only. Don't print $900 publicly.

## Targets

| By | Agencies contacted | Partners signed | End clients |
|---|---|---|---|
| Day 60 | 300 | 1 | 1–2 |
| Day 90 | 900 | 3 | 4–6 |
| Month 6 | 3,000 | 8–10 | 20–30 |
| Month 12 | — | 20 | 35–60 |
