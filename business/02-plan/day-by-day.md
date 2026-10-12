# Day by day: days 1–30

Each day lists **what you do** (marked 👤) and **what the AIs do** (marked 🤖), with rough times. When a step says "ask Claude," open Claude Code in this repo and paste the request. Claude reads these files and does it.

**Where the commands run:** On your own computer. Get the code with `git clone https://github.com/kalebconfer-sys/rankandreply.git`, then `git checkout claude/ai-automated-business-plan-ptu9y7`, then `cd rankandreply/business/tools`. Everything that says `python ...` runs from that folder.

---

## Day 1: Accounts that take time to mature (about 2 hours)

1. 👤 **Buy 5 sending domains** (Namecheap, Cloudflare or Porkbun; about $14 each). Suggested names: `getrankandreply.com`, `tryrankandreply.com`, `rankandreplyhq.com`, `rankandreplymail.com`, `userankandreply.com`. Take whichever are available.
2. 👤 **Create 15 Google inboxes** through Zapmail (it sets up DNS automatically), or Google Workspace directly. Name every inbox after yourself: `kaleb@`, `kaleb.confer@`, `k.confer@`. Add a profile photo and the same signature to each.
3. 👤 **Sign up for Instantly** (Growth plan), connect all 15 inboxes, and **turn warmup ON**.
   - Settings: open tracking **OFF**, link tracking **OFF**, unsubscribe header **ON**.
4. 👤 Set each domain to redirect (301) to `https://rankandreply.com/ai-visibility/`.
5. 🤖 If anything in steps 1–4 is confusing, ask Claude: *"Walk me through setting up DNS for getrankandreply.com in Zapmail, step by step."*

**Finish line:** Instantly shows 15 inboxes, all warming, all with SPF/DKIM/DMARC passing.

## Day 2: The AI team (about 1 hour)

1. 👤 Get the API keys:

   | AI | Where to get the key | Cost |
   |---|---|---|
   | Claude | console.anthropic.com | Add $20 credit |
   | ChatGPT | platform.openai.com | Add $20 credit |
   | Gemini | aistudio.google.com | Free tier |
   | Perplexity | perplexity.ai/settings/api | Uses your Pro credit, or add $10 |

2. 👤 Install Python 3.11+ and Ollama, then run `ollama pull llama3.1:8b`.
3. 👤 In `business/tools`, run `pip install -r requirements.txt`, then `playwright install chromium`.
4. 👤 Copy `.env.example` to `.env` and paste in the keys.
5. 🤖 Run `python council.py status`. Every line should say `ready`.
6. 🤖 First council test: `python council.py ask "In one sentence each: what's the biggest risk in business/01-research/market-research.md?" --file ../01-research/market-research.md`

**Finish line:** five AIs answering.

## Day 3: Prove the engine on real companies (about 1 hour; about $20–40 in API calls)

1. 🤖 Ask Claude: *"Pick 5 real B2B software companies with 10–200 employees and 5 managed IT providers in Pennsylvania or Ohio that would be ideal customers. Give me brand, domain and region."*
2. 🤖 For each one, run:
   ```bash
   python visibility.py snapshot --brand "Company" --domain company.com --n 20 --pdf
   ```
   Add `--region "Pittsburgh, PA"` for the IT providers.
3. 👤 Open 3 of the PDFs. Do they make sense? Would *you* reply to an email that opened with that finding?
4. 🤖 Note the real cost per report from each AI provider's billing page.

**Finish line:** 10 real reports, and you know what one costs.

## Day 4: Money and the legal basics (about 1 hour)

1. 👤 **Stripe:** create an account for RevivaCatch LLC. Create two Payment Links:
   - "AI Visibility Fix Plan": $490, one-time.
   - "AI Visibility Retainer": $1,500/month, recurring.
   - On both: after payment, redirect to your onboarding form (step 3).
2. 👤 **Virtual mailbox** (iPostal1 or Anytime Mailbox, about $10–15/month) for the legal email footer.
3. 👤 **Onboarding form:** build it in Tally from [`../03-offer/onboarding-form.md`](../03-offer/onboarding-form.md) (about 20 minutes).
4. 🤖 Ask Claude: *"Swap the Stripe links into ai-visibility/index.html and the email templates: Fix Plan = <link>, Retainer = <link>."*

**Finish line:** a test purchase in Stripe test mode goes all the way to the onboarding form.

## Day 5: Council review of the hook (about 45 minutes)

1. 🤖 Ask Claude: *"Summarize the 10 reports in business/data/reports into business/data/ten-reports.md: brand, rate, top 3 competitors, headline."* Then run:
   ```bash
   python council.py debate "Based on these 10 snapshot results, is our cold email hook (we asked ChatGPT your buyers' question; here's who it named instead) true, strong, and safe? What would make a busy founder reply? What would make them mark it as spam?" --file ../data/ten-reports.md
   ```
2. 👤 Read the decision. Ask Claude to apply any copy changes it recommends.
3. 🤖 From the 10 reports, Claude writes **one true, citable line** for the emails. Example: "Of 10 software companies I checked this month, the median was named in 15% of answers." Only use it if the numbers support it.

## Day 6: Marketplaces live (about 1.5 hours)

1. 👤 **Upwork:** paste the profile from [`../04-outreach/marketplaces.md`](../04-outreach/marketplaces.md). Create the Catalog listing (3 tiers). Use one of your 10 reports, anonymized, as the portfolio sample.
2. 👤 **Fiverr:** create the gig (3 packages, requirements, description).
3. 👤 **Contra:** profile plus 2 services at full price.

## Day 7: First proposals (about 45 minutes)

1. 🤖 **Scout:**
   ```bash
   python council.py research "Upwork job posts from the last 7 days asking for GEO, AEO, AI search visibility, ChatGPT visibility or LLM SEO. List title, URL, budget, client industry, and whether a company website is named."
   ```
2. 🤖 For each good post, run the probe on the client's site if it's named. Then draft the proposal: put the post text in a CSV column `post` and the probe result in `probe`, and run:
   ```bash
   python council.py bulk --in posts.csv --prompt prompts/upwork_proposal.txt --out proposals.csv --column proposal
   ```
3. 👤 Read each proposal, edit, and **submit by hand**. Target: 10.
4. 👤 Merge the branch on GitHub (or ask Claude to open a pull request and merge it) so `/ai-visibility/` goes live.

## Day 8: First lead batch (about 1 hour)

1. 👤 **Apollo:** run the Segment A search (filters in [`cold-email.md`](../04-outreach/cold-email.md) §2). Export 300 contacts.
2. 👤 **MillionVerifier:** upload, keep only "good" addresses, download.
3. 🤖 Run:
   ```bash
   python visibility.py enrich --in ../data/leads/a-raw.csv --out ../data/leads/a1.csv
   python visibility.py probe --in ../data/leads/a1.csv --out ../data/leads/a2.csv
   python visibility.py firstline --in ../data/leads/a2.csv --out ../data/leads/a-ready.csv
   ```
4. 👤 Read 20 first lines. Delete anything odd.

## Day 9: Second lead batch (about 1 hour)

Same as day 8, for **Segment B** (services, with `--region`). 300 contacts.

## Day 10: Sequences loaded (about 1 hour)

1. 👤 In Instantly, create **Campaign A1** (Segment A, Sequence 1), **A2** (Segment A, Sequence 2) and **B1/B2** (Segment B). Paste the copy from [`cold-email.md`](../04-outreach/cold-email.md) §3 and add the footer.
2. 👤 Upload the ready CSVs. Map the variables. **Schedule the start for day 15.** Sending window 8am–5pm in the recipient's time zone, weekdays only.
3. 🤖 Critic review:
   ```bash
   python council.py ask "You are a busy VP of Marketing. Here's a cold email. What makes you delete it? What makes you reply? Rewrite the weakest sentence." --ai chatgpt --file ../04-outreach/cold-email.md
   ```

## Day 11: Deliverability test (about 30 minutes)

1. 👤 Send one test from each of 3 inboxes to your own Gmail, Outlook and Yahoo addresses. Check that they land in the **Primary** inbox and that SPF/DKIM/DMARC show "PASS" (Gmail → ⋮ → Show original).
2. 👤 Check each domain at mail-tester.com. The target is 9/10 or better.

## Day 12: Reply process dry run (about 30 minutes)

1. 🤖 Ask Claude: *"Make a fake replies CSV with 8 realistic replies: 2 yes, 1 price, 1 question, 1 not now, 1 has agency, 1 unsubscribe, 1 out of office."*
2. 🤖 Run `classify_reply` and then `draft_reply` on it with `council.py bulk` (commands in [`cold-email.md`](../04-outreach/cold-email.md) §4).
3. 👤 Check that the labels are right and the drafts are sendable. Ask Claude to tune the prompts if not.

## Day 13: Upwork and Fiverr (about 45 minutes)

15 more proposals over days 13–14. Deliver any orders that came in (`snapshot --pdf`, QA, send).

## Day 14: Pre-flight (about 30 minutes)

- [ ] Warmup health in Instantly: 95%+ landing in the inbox
- [ ] Campaigns scheduled for tomorrow, at 5 emails per inbox per day
- [ ] Footer with mailbox address and opt-out line on every step
- [ ] Suppression list created (and shared across campaigns)
- [ ] Stripe links live on the page and in template A
- [ ] Onboarding form linked from Stripe

---

## Days 15–30: The daily routine (about 1.5 hours a day)

**Every morning (30–45 min)**
1. 👤 Export new replies from Instantly to `../data/replies/today.csv`. The columns should be `first_name`, `company`, `email`, `reply_text`.
2. 🤖 Classify and draft:
   ```bash
   python council.py bulk --in ../data/replies/today.csv --prompt prompts/classify_reply.txt --out ../data/replies/today-tagged.csv --column label
   python council.py bulk --in ../data/replies/today-tagged.csv --prompt prompts/draft_reply.txt --out ../data/replies/today-drafts.csv --column draft
   ```
3. 🤖 For every `yes`: `python visibility.py snapshot --brand "..." --domain ... --pdf`
4. 👤 Skim each PDF (2 minutes), then send template A with the PDF attached. Send the other drafts. Add every `no` to the suppression list.
5. 👤 Log each report and each sale in your pipeline sheet: copy `business/02-plan/templates/pipeline.csv` to `business/data/pipeline.csv` once and fill in that copy. `business/data/` is never pushed, which matters because this repo is public and real contacts must not go in it.

**Once a day (20 min):** a new lead batch (Apollo → verify → enrich → probe → firstline → upload), so the queue always has 3 days of leads.

**Once a day (20 min):** Upwork. The Scout finds posts, the Chair drafts, you submit 3.

**Ramp:**
- Day 15: 5 emails per inbox per day.
- Day 19: 10.
- Day 23: 15.
- **Pause any inbox whose bounce rate goes over 2%.**

**Mondays (days 15, 22, 29): council review (45 min)**
```bash
python council.py debate "Here is this week's scoreboard. Which funnel step is weakest, why, and what single change should we make this week?" --file ../data/scoreboard.csv
```
(Copy `business/02-plan/templates/scoreboard.csv` to `business/data/scoreboard.csv` once and fill in that copy.)

**Fridays:** fill in the scoreboard row for the week.

**Day 30:** the decision. Look at "yes" rate × report-to-paid rate for Segment A vs B. The winner gets 90% of volume. Then start [Phase 3](90-day-plan.md#phase-3-double-down-and-systematize-days-4690): buy 5 more domains, start warming them, and build the agency list.
