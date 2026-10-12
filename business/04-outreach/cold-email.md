# Cold email: the playbook

> **Why it didn't work before, and why it will now.** Cold email works for everyone else because they don't send it from their real Gmail or their main domain. Since November 2025, Gmail **rejects** mail that isn't set up properly, where before it only sent it to spam. Most beginners also send one generic email with tracking links to an unverified list. Every one of those mistakes is fixed below. Evidence and sources: [`../01-research/sources/cold-email.md`](../01-research/sources/cold-email.md).

## 1. The setup (do once; about $330–360/month)

| Piece | What to buy | Cost | Notes |
|---|---|---|---|
| Sending domains | **10** lookalike .com domains, e.g. `getrankandreply.com`, `tryrankandreply.com`, `rankandreplyhq.com`, `rankandreplymail.com`, `userankandreply.com`, `rankandreplyteam.com`, `hellorankandreply.com`, `rankandreplyai.com`, `meetrankandreply.com`, `rankandreplyco.com` (check availability) | about $140/yr total | **Never send cold email from rankandreply.com or your Gmail.** Point each one (301 redirect) to rankandreply.com/ai-visibility/ |
| Inboxes | **3 per domain = 30 inboxes**, through a cold-email inbox provider such as Zapmail ($99 for 30 Google mailboxes) or Mailforge (about $3/mailbox). **Not** in the Google account that runs rankandreply.com | about $90–100/mo | Real name on every inbox: kaleb@, kaleb.confer@, k.confer@. **No fake personas** |
| DNS | SPF, DKIM, DMARC (`p=none` with reporting) on every domain | $0 | Zapmail does it automatically. Check each domain at mail-tester.com (aim for 10/10) |
| Sending tool | **Instantly** Hypergrowth | $97/mo | Growth ($47) is reported to cap at about 1,000 uploaded contacts and 5,000 sends a month, which is too small from week 3. Check the current limits on Instantly's pricing page before buying. Unlimited inboxes and warmup. **Turn open tracking and link tracking OFF.** Turn the one-click unsubscribe header ON |
| Leads | **Apollo** Professional | $79–99/mo | About 4,000 credits/mo, roughly one month of first touches at full volume |
| Verification | **MillionVerifier** | about $37 per 10k | Remove invalid, catch-all and risky addresses. Target under 2% bounces |
| Mailing address | Virtual mailbox (iPostal1, Anytime Mailbox) or a USPS P.O. box | $10–15/mo | Required by law in every email footer. Keeps your home address private |

> **Google's rules, plainly.** Google Workspace's acceptable-use and program policies prohibit unsolicited bulk email. Low-volume, individually relevant B2B outreach from dedicated domains is common practice, but **expect some inboxes to be suspended**, and plan for it:
> - Sending domains and inboxes **never** live in the Google account that runs rankandreply.com. A suspension must not be able to take down your real business email.
> - Once you pass 30 inboxes, split them across two providers (for example Google through Zapmail and Microsoft through Mailforge).
> - Keep about $30/month in the budget for replacing suspended inboxes.

**Warmup:** Connect all 30 inboxes to Instantly on day 1 with warmup on. **No cold sends until day 15.**

**Ramp after warmup:**

| Days | Cold emails per inbox per day | Total per day |
|---|---|---|
| 15–18 | 5 | 150 |
| 19–22 | 10 | 300 |
| 23–30 | 15 | 450 |
| From day 31 | 20 max | 600 |

**The daily cap includes follow-ups.** Each lead gets 3 emails, so 600 sends a day ≈ 200 new leads a day ≈ **4,200 new leads a month**. Over days 15–30 the ramp sends about 3,900 emails, about 2,000 of them first touches. Add more domains (5 at a time, warmed 14 days) to grow past 600 a day.

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
- Locations: **United States only** for the first 90 days. Canada and the UK need extra consent steps; revisit after day 90.
- Titles:
  - under 50 employees: Founder, Co-founder, CEO.
  - 50+ employees: VP Marketing, Head of Marketing, Director of Marketing, Head of Growth, Demand Generation.

**Apollo filters for Segment B (services, United States only):** Industry: Information Technology & Services, Computer & Network Security, Marketing & Advertising (B2B), Management Consulting. Employees: 5–100. Titles: Owner, Founder, CEO, President, Marketing Manager. Add the city or state to `--region`.

```bash
cd business/tools
python visibility.py enrich    --in ../data/leads/2026-10-27-apollo.csv --out ../data/leads/a1.csv
python visibility.py probe     --in ../data/leads/a1.csv --out ../data/leads/a2.csv
python visibility.py firstline --in ../data/leads/a2.csv --out ../data/leads/a3-ready.csv
```

Or run all three at once: `python autopilot.py leads --in ../data/leads/2026-10-27-apollo.csv`.

Open the ready file and **check 20 rows** before uploading. Read each `first_line` next to `probe_answer` (the AI's actual saved answer): every company named in the line must be in the answer, and the prospect must not be. Is the question something a buyer would really ask? Delete any row that fails. Then upload to Instantly and map the columns `first_name`, `company`, `first_line`, `buyer_question`, `named_1`, `named_2` as custom variables.

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
> In G2's 2026 survey of 1,076 software buyers, about half said they now start their research in an AI chatbot, so answers like that are quietly shaping shortlists.
>
> I can ask ChatGPT, Gemini, Perplexity and Claude the 10 questions your buyers most likely ask (twice each, since answers vary) and send you who gets named, who doesn't, and the five fixes that matter most. Free, no call.
>
> Want it?
>
> Kaleb Confer
> Rank and Reply

*Segment B: replace the G2 sentence with:* "More buyers now ask an assistant for a shortlist before they search Google, so that answer is quietly deciding who gets the call."

**Email 2 (day 3, same thread)**

> {{first_name}}, one more detail. The assistants lean heavily on review sites, "best of" lists and pages that answer comparison questions directly. That's why the same few names keep coming up. It's a content and listings gap, not an ad-spend one.
>
> Happy to send the report for {{company}}. Just reply "send it."
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
> I can ask ChatGPT, Gemini, Perplexity and Claude the 10 questions buyers ask at the shortlist stage (twice each) and show you where {{company}} holds up and where a competitor takes the spot. Free, no call.
>
> Want it?
>
> Kaleb Confer
> Rank and Reply

Emails 2 and 3: the same as Sequence 1.

### The footer (on every email, set once in Instantly)

```
Rank and Reply (RevivaCatch LLC) · [mailbox address], Erie, PA [ZIP]
This is a business solicitation. Not relevant? Reply "no" and I won't email again.
```

CAN-SPAM requires commercial email to identify itself as an advertisement or solicitation. The second line does that plainly.

## 4. Replies: what happens to each one

Export replies from Instantly once a day, at any time that fits your shifts. Use columns `email`, `first_name`, `company`, `website`, `reply_text`. Then run one command:

```bash
python autopilot.py replies --in ../data/replies/2026-10-28.csv
```

It tags every reply with the local model, drafts answers with Claude, runs the report for every "yes", and writes ready-to-send emails into `business/data/outbox/<date>/`. Nothing is sent until you send it.

The manual equivalent, if you prefer:

```bash
python council.py bulk --in ../data/replies/today.csv --prompt prompts/classify_reply.txt --out ../data/replies/today-tagged.csv --column label
python council.py bulk --in ../data/replies/today-tagged.csv --prompt prompts/draft_reply.txt --out ../data/replies/today-drafts.csv --column draft --ai claude
```

| Label | What happens | Who |
|---|---|---|
| `yes` | Run the snapshot. Send the report within 2 business days using template A | AI runs it; you skim the PDF and press send |
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
> - **Fix Plan, $490 once:** the full 480-answer audit, the sites the engines cite, a 30-day roadmap and two pages written for you, in 5 business days. Credited to your first Retainer month if you continue within 30 days. {{stripe_fixplan_link}}
> - **Retainer, $1,500/month,** month-to-month. {{stripe_retainer_link}}
>
> Everything is at rankandreply.com/ai-visibility. Questions? Just reply. No call needed.
>
> Kaleb

**Template A is for cold-email leads only.** Never put a Stripe link, website or email address in anything sent through Upwork or Fiverr.

**Follow-ups after the report:**
- **Day 3:** "Did the report make sense? One thing worth doing this week, even if we never work together: {{fix_1_how_short}}."
- **Day 8:** "Last note on this. If the Fix Plan is useful, here's the link again: {{stripe_fixplan_link}}. Either way, the report is yours."

### Template B: "How did you do this?" / "Who are you?"

> Fair question. I put each question to ChatGPT, Gemini, Perplexity and Claude through their official APIs, with web search on, more than once each, and count who gets named. It's the same question your buyers type. I'm Kaleb, and I run Rank and Reply out of Erie, PA. Happy to send the full report so you can see the method. It's printed on the last page.

### Template C: price

> It's on the page: rankandreply.com/ai-visibility. The short version: the report is free, the Fix Plan is $490 one time, and the Retainer is $1,500/month with no contract. Want the free report first?

### Template D: not now

> Understood. I'll check back in about three months with a fresh run, unless you'd rather I didn't. Just say so.

### Template E: "We already have an SEO agency"

> Makes sense. Worth asking whether they measure what AI assistants say about you. It's a different measurement from rankings. Happy to send the report so you can hand it to them. No strings.

### Template F: they want a call

> Happy to. Here's my calendar: {{calendar_link}}. 15 minutes is usually plenty. I'll bring your report.

## 5. Compliance checklist (all of it, every time)

- [ ] Real name and real company in From and the signature.
- [ ] Subject line describes the email. No fake "Re:" or "Fwd:".
- [ ] Physical mailing address in the footer.
- [ ] The footer identifies the email as a business solicitation.
- [ ] Opt-out line in the footer and the one-click unsubscribe header on. Opt-outs honored the same day (the law allows 10 business days; we do better).
- [ ] **One suppression list** shared by every inbox and every campaign. Anyone who says no is never emailed again, from any domain.
- [ ] **United States only** for the first 90 days. After that, Canada needs CASL evidence for each address (published on the company's site, relevant to the person's role, screenshot kept), and the UK needs limited companies only plus a privacy notice. No EU: Germany and Austria require prior consent even for business email.
- [ ] Sending inboxes live outside the Google account that runs rankandreply.com.
- [ ] No purchased lists of personal (non-work) emails. No scraping LinkedIn.
