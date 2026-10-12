# Cold email: the playbook

> **Why it didn't work before, and why it will now.** Cold email works for everyone else because they don't send it from their real Gmail or their main domain. Since November 2025, Gmail **rejects** mail that isn't set up properly, where before it only sent it to spam. Most beginners also send one generic email with tracking links to an unverified list. Every one of those mistakes is fixed below. Evidence and sources: [`../01-research/sources/cold-email.md`](../01-research/sources/cold-email.md).

## 1. The setup (do once; about $200/month)

| Piece | What to buy | Cost | Notes |
|---|---|---|---|
| Sending domains | **5** lookalike .com domains, e.g. `getrankandreply.com`, `tryrankandreply.com`, `rankandreplyhq.com`, `rankandreplymail.com`, `userankandreply.com` (check availability) | about $70/yr total | **Never send cold email from rankandreply.com or your Gmail.** Point each one (301 redirect) to rankandreply.com/ai-visibility/ |
| Inboxes | **3 per domain = 15 inboxes**, Google Workspace via Zapmail ($39 for 10, plus 5 more) or Google Workspace directly ($7–8.40 each) | about $55–125/mo | Real name on every inbox: kaleb@, kaleb.confer@, k.confer@. **No fake personas** |
| DNS | SPF, DKIM, DMARC (`p=none` with reporting) on every domain | $0 | Zapmail does it automatically. Check each domain at mail-tester.com (aim for 10/10) |
| Sending tool | **Instantly** Growth | $47/mo | Unlimited inboxes and warmup. **Turn open tracking and link tracking OFF.** Turn the one-click unsubscribe header ON |
| Leads | **Apollo** Basic | $49–65/mo | 2,500 credits/mo is enough for month 1 |
| Verification | **MillionVerifier** | about $37 per 10k | Remove invalid, catch-all and risky addresses. Target under 2% bounces |
| Mailing address | Virtual mailbox (iPostal1, Anytime Mailbox) or a USPS P.O. box | $10–15/mo | Required by law in every email footer. Keeps your home address private |

**Warmup:** Connect all 15 inboxes to Instantly on day 1 with warmup on. **No cold sends until day 15.**

**Ramp after warmup:**

| Days | Cold emails per inbox per day | Total per day |
|---|---|---|
| 15–18 | 5 | 75 |
| 19–22 | 10 | 150 |
| 23–30 | 15 | 225 |
| From day 31 | 20 max | 300 |

Add more domains (5 at a time, warmed 14 days) to grow past 300 a day.

**Stop rules (Instantly can enforce these):**
- Bounces above **2%** on any inbox: pause it.
- Spam complaints above **0.1%**: pause everything and run a council review.

## 2. The lead pipeline (daily, about 20 minutes of your time)

```
Apollo search ─► export CSV ─► MillionVerifier ─► visibility.py enrich ─► probe ─► firstline ─► Instantly
     (you)          (you)          (you)            (AI reads sites)   (AI asks ChatGPT)  (script)    (upload)
```

**Apollo filters for Segment A (software):**
- Industry: Computer Software / Internet / IT Services.
- Employees: 10–200.
- Locations: United States, Canada (see the CASL rule below), United Kingdom.
- Titles:
  - under 50 employees: Founder, Co-founder, CEO.
  - 50+ employees: VP Marketing, Head of Marketing, Director of Marketing, Head of Growth, Demand Generation.

**Apollo filters for Segment B (services):** Industry: Information Technology & Services, Computer & Network Security, Marketing & Advertising (B2B), Management Consulting. Employees: 5–100. Titles: Owner, Founder, CEO, President, Marketing Manager. Add the city or state to `--region`.

```bash
cd business/tools
python visibility.py enrich    --in ../data/leads/2026-10-27-apollo.csv --out ../data/leads/a1.csv
python visibility.py probe     --in ../data/leads/a1.csv --out ../data/leads/a2.csv
python visibility.py firstline --in ../data/leads/a2.csv --out ../data/leads/a3-ready.csv
```

Open `a3-ready.csv` and **read 20 rows** before uploading. Does each first line make sense? Is the question something a buyer would really ask? Delete any odd rows. Then upload to Instantly and map the columns `first_name`, `company`, `first_line`, `buyer_question`, `named_1`, `named_2` as custom variables.

`segment = not_named` rows go to **Sequence 1**. `segment = named` rows go to **Sequence 2**.

## 3. The sequences

Rules, from the research:
- Under 100 words.
- Plain text, no links and no images in email 1.
- Ask about interest, not for time.
- The opening line is a fact we checked, about them.
- No "hope this finds you well."
- Never claim results we don't have.

### Sequence 1: not named (the main one)

**Email 1 (day 0)**
Subject A: `{{company}} on ChatGPT`
Subject B: `{{company}} and AI search`

> Hi {{first_name}},
>
> {{first_line}}
>
> About half of software buyers now start their shortlist in a chatbot (G2, 2026), so that answer is quietly picking vendors for you.
>
> I can run the 20 questions your buyers most likely ask across ChatGPT, Gemini, Perplexity and Claude, and send you who gets named, who doesn't, and the five fixes that matter most. Free, no call.
>
> Want it?
>
> Kaleb Confer
> Rank and Reply

*Segment B: replace the G2 sentence with:* "More buyers now ask an assistant for a shortlist before they search Google, so that answer is quietly deciding who gets the call."

**Email 2 (day 3, same thread)**

> {{first_name}}, one more detail. The assistants lean heavily on review sites, "best of" lists and pages that answer comparison questions directly. That's why the same few names keep coming up. It's a content and listings gap, not an ad-spend one.
>
> Happy to send the 20-question report for {{company}}. Just reply "send it."
>
> Kaleb

**Email 3 (day 7, same thread)**

> Last one from me, {{first_name}}. If AI search isn't a priority this quarter, no problem. If it is, reply "send it" and the report's yours, whether or not we ever work together.
>
> Kaleb

### Sequence 2: named (defend the spot)

**Email 1 (day 0)**
Subject: `{{company}} on ChatGPT`

> Hi {{first_name}},
>
> {{first_line}} Good sign, but that's one question on one assistant.
>
> I can run the 20 questions buyers ask at the shortlist stage across ChatGPT, Gemini, Perplexity and Claude and show you where {{company}} holds up and where a competitor takes the spot. Free, no call.
>
> Want it?
>
> Kaleb Confer
> Rank and Reply

Emails 2 and 3: the same as Sequence 1.

### The footer (on every email, set once in Instantly)

```
Rank and Reply · RevivaCatch LLC · [mailbox address], Erie, PA [ZIP]
Not relevant? Reply "no" and I won't email again.
```

## 4. Replies: what happens to each one

Export replies from Instantly each morning (or use its webhook later). Then run:

```bash
python council.py bulk --in ../data/replies/today.csv --prompt prompts/classify_reply.txt --out ../data/replies/today-tagged.csv --column label
python council.py bulk --in ../data/replies/today-tagged.csv --prompt prompts/draft_reply.txt --out ../data/replies/today-drafts.csv --column draft
```

| Label | What happens | Who |
|---|---|---|
| `yes` | Run the snapshot. Send the report within 1 business day using template A | AI runs it; you skim the PDF and press send |
| `question` | Answer from the FAQ (template B) | AI drafts; you send |
| `price` | Template C | AI drafts; you send |
| `not_now` | Template D; snooze 90 days | AI |
| `has_agency` | Template E | AI drafts; you send |
| `wants_call` | They're close to buying. Send your calendar link (template F) | **You.** This is the only call you take |
| `no` / `unsubscribe` / `angry` | Add to the suppression list **immediately**. No reply, or one line: "Done, sorry for the bother." | AI flags; you confirm |
| `ooo` (out of office) | Re-queue after their return date | Instantly |

### Template A: the report (after "yes")

> Hi {{first_name}},
>
> Here's the report for {{company}} (PDF attached).
>
> The short version:
> - {{company}} was named in {{mentioned}} of {{answers}} answers ({{rate}}%).
> - {{top_competitor}} was named in {{top_share}}% of them.
> - The biggest gap: {{fix_1_title}}.
>
> If you'd like to fix it yourself, the five fixes at the end are where to start. If you'd rather we did it:
> - **Fix Plan, $490 once:** the full 480-answer audit, the sites the engines cite, a 30-day roadmap and two pages written for you, in 5 business days. {{stripe_fixplan_link}}
> - **Retainer, $1,500/month,** month-to-month. {{stripe_retainer_link}}
>
> Everything is at rankandreply.com/ai-visibility. Questions? Just reply. No call needed.
>
> Kaleb

**Follow-ups after the report:**
- **Day 3:** "Did the report make sense? One thing worth doing this week, even if we never work together: {{fix_1_how_short}}."
- **Day 8:** "Last note on this. If the Fix Plan is useful, here's the link again: {{stripe_fixplan_link}}. Either way, the report is yours."

### Template B: "How did you do this?" / "Who are you?"

> Fair question. I put each question to ChatGPT, Gemini, Perplexity and Claude through their official APIs, with web search on, and count who gets named. It's the same question your buyers type. I'm Kaleb, and I run Rank and Reply out of Erie, PA. Happy to send the full report so you can see the method. It's printed on the last page.

### Template C: price

> It's on the page: rankandreply.com/ai-visibility. The short version: the report is free, the Fix Plan is $490 one time, and the Retainer is $1,500/month with no contract. Want the free report first?

### Template D: not now

> Understood. I'll check back in about three months with a fresh run, unless you'd rather I didn't. Just say so.

### Template E: "We already have an SEO agency"

> Makes sense. Worth asking whether they measure AI answers. Most SEO reporting doesn't. Happy to send the report so you can hand it to them. No strings.

### Template F: they want a call

> Happy to. Here's my calendar: {{calendar_link}}. 15 minutes is usually plenty. I'll bring your report.

## 5. Compliance checklist (all of it, every time)

- [ ] Real name and real company in From and the signature.
- [ ] Subject line describes the email. No fake "Re:" or "Fwd:".
- [ ] Physical mailing address in the footer.
- [ ] Opt-out line in the footer and the one-click unsubscribe header on. Opt-outs honored the same day (the law allows 10 business days; we do better).
- [ ] **One suppression list** shared by every inbox and every campaign. Anyone who says no is never emailed again, from any domain.
- [ ] **Canada:** only email addresses published on the company's own site, where the email is relevant to that person's role. Screenshot the page with the date and keep it (CASL burden of proof). If unsure, skip Canada.
- [ ] **UK:** limited companies only. Skip sole traders.
- [ ] **No EU** (Germany and Austria require prior consent even for business email).
- [ ] No purchased lists of personal (non-work) emails. No scraping LinkedIn.
