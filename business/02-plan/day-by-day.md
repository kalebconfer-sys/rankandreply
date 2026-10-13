# Day by day: days 1–30

Each day lists **what you do** (marked 👤) and **what the AIs do** (marked 🤖), with rough times. The times fit around shifts: nothing has to happen at a particular hour. When a step says "ask Claude," open Claude Code in this repo and paste the request. Claude reads these files and does it.

**Where the commands run:** On your own computer.
1. Get the code: `git clone https://github.com/kalebconfer-sys/rankandreply.git`
2. Switch to this branch: `git checkout claude/ai-automated-business-plan-ptu9y7`
3. Go to the tools folder: `cd rankandreply/business/tools`

Everything that says `python ...` runs from that folder. You need Python 3.10 or newer.

**If something breaks:** paste the whole error into Claude Code in this repo. If the same error happens twice, stop and fix it before moving on. Every later step depends on the tools working.

---

## Day 1: Accounts that take time to mature (about 2 hours)

1. 👤 **Buy 10 sending domains** (Namecheap, Cloudflare or Porkbun; about $14 each). Suggested names are in [`cold-email.md`](../04-outreach/cold-email.md) §1. Take whichever are available.
2. 👤 **Create 30 inboxes (3 per domain)** through a cold-email inbox provider such as Zapmail ($99 for 30, DNS set up automatically).
   - **Never** add these domains to the Google account that runs rankandreply.com. A suspension there would take down your real email.
   - Name every inbox after yourself: `kaleb@`, `kaleb.confer@`, `k.confer@`. Add a profile photo and the same signature to each.
3. 👤 **Sign up for Instantly** (Hypergrowth plan; check the current limits on its pricing page). Connect all 30 inboxes and **turn warmup ON**.
   - Settings: open tracking **OFF**, link tracking **OFF**, unsubscribe header **ON**.
4. 👤 Set each domain to redirect (301) to `https://rankandreply.com/ai-visibility/`.
5. 🤖 If anything in steps 1–4 is confusing, ask Claude: *"Walk me through setting up getrankandreply.com in Zapmail, step by step."*

**Finish line:** Instantly shows 30 inboxes, all warming, all with SPF/DKIM/DMARC passing.

## Day 2: The AI team (about 1 hour)

1. 👤 Get the API keys:

   | AI | Where to get the key | Cost |
   |---|---|---|
   | Claude | console.anthropic.com | Add $20 credit |
   | ChatGPT | platform.openai.com | Add $20 credit |
   | Gemini | aistudio.google.com | **Turn billing on.** The free tier may use your inputs to improve Google's products, and we'll be sending client data through it |
   | Perplexity | perplexity.ai/settings/api | Uses your Pro credit, or add $10 |

2. 👤 **Windows:** follow [`../SETUP.md`](../SETUP.md). Install Python, then double-click `business\tools\setup.bat`. It installs everything and opens `.env` for your keys. **Mac:** run `bash setup-mac.sh`.
3. 👤 Optional: install Ollama and run `ollama pull llama3.1:8b`. If your computer has less than 16 GB of memory, skip Ollama and put `LOCAL_DISABLED=1` in `.env`; Gemini then does the bulk work.
4. 👤 Paste the keys into `.env` and save.
5. 🤖 Run `setup.bat` again (or `python council.py status`). Each AI you set up should say `ready`.
6. 🤖 First council test:
   ```bash
   python council.py ask "In one sentence each: what's the biggest risk in this plan?" --file ../01-research/market-research.md
   ```

**Finish line:** the AIs answer.

## Day 3: Prove the tools on real APIs (about 1 hour; about $10–20 in API calls)

1. 🤖 Ask Claude: *"Pick 3 real B2B software companies with 10–200 employees that would be ideal customers. Give me brand and domain."*
2. 🤖 For each one, run:
   ```bash
   python visibility.py snapshot --brand "Company" --domain company.com --pdf
   ```
   (Default: 10 questions, each asked twice on every engine.)
3. 👤 Open the 3 PDFs. Do the numbers make sense? Spot-check 3 answers in `raw.json` against the report.
4. 🤖 Note the real cost per report from each AI provider's billing page.

**Finish line:** 3 good PDFs. **If any step errors twice, stop and fix it with Claude before day 4.** Days 5–15 all depend on this.

## Day 4: Money and the legal basics (about 1.5 hours)

1. 👤 **Stripe:** create an account for RevivaCatch LLC. Create three Payment Links, each redirecting to your onboarding form after payment (step 4):

   | Payment Link | Price |
   |---|---|
   | AI Visibility Fix Plan | $490 one-time |
   | AI Visibility Retainer | $1,500/month recurring |
   | AI Visibility Sprint (3 months) | $3,900 one-time |

2. 👤 **Virtual mailbox** (iPostal1 or Anytime Mailbox, about $10–15/month) for the legal email footer.
3. 👤 **Fictitious name:** check that "Rank and Reply" is registered with Pennsylvania as a fictitious name of RevivaCatch LLC. If it isn't, file it (PA Department of State, about $70).
4. 👤 **Onboarding form:** build it in Tally from [`../03-offer/onboarding-form.md`](../03-offer/onboarding-form.md) (about 20 minutes).
5. 🤖 Ask Claude: *"Swap the Stripe links into ai-visibility/index.html, and put them in business/tools/.env as STRIPE_FIXPLAN_LINK and STRIPE_RETAINER_LINK: Fix Plan = <link>, Retainer = <link>, Sprint = <link>."*
6. 👤 Read `ai-visibility/privacy.html` and `terms.html`. They're drafts; have a lawyer look at them when you can.

**Finish line:** a test purchase in Stripe test mode goes all the way to the onboarding form.

## Day 5: More proof, then a council review of the hook (about 1 hour; about $20–40)

1. 🤖 Run 7 more snapshots: 2 more software companies and 5 managed IT providers in Pennsylvania or Ohio. For the IT providers, add `--region "Pittsburgh, PA"`.
2. 🤖 Ask Claude: *"Summarize the 10 reports in business/data/reports into business/data/ten-reports.md: brand, rate, top 3 competitors, headline."*
3. 🤖 Run:
   ```bash
   python council.py debate "Based on these 10 snapshot results, is our cold email hook (we asked ChatGPT your buyers' question; here's who it named instead) true, strong, and safe? What would make a busy founder reply? What would make them mark it as spam?" --file ../data/ten-reports.md --file ../04-outreach/cold-email.md
   ```
4. 👤 Read the decision. Ask Claude to apply any copy changes it recommends.
5. 🤖 Only if the numbers support it, Claude writes **one true line** for the emails that describes the sample honestly, for example: "Of 5 B2B software companies I checked this month, 4 weren't named in most answers."

## Day 6: Marketplaces live (about 1.5 hours)

1. 👤 **Upwork:** paste the profile from [`../04-outreach/marketplaces.md`](../04-outreach/marketplaces.md). Create the Catalog listing (3 tiers). Use one of your 10 reports, anonymized, as the portfolio sample. Set up the saved searches with email alerts.
2. 👤 **Fiverr:** create the gig (3 packages, requirements, description).
3. 👤 **Contra:** profile plus 2 services at direct prices.
4. 👤 **Reddit and Upwork alerts (20 minutes):**
   - Sign up for F5Bot with the keywords in [`reddit.md`](../04-outreach/reddit.md).
   - Create a Gmail app password and put `IMAP_USER` and `IMAP_PASSWORD` in `.env` (a separate alerts-only Gmail is best).
   - 🤖 Test it: `python scout.py run`. It should print how many alert emails it read.
5. 👤 **Reddit account:** set an honest profile. For the next 2 weeks, answer questions only; never mention the business.

## Day 7: Site live (about 30 minutes)

1. 👤 Merge the branch on GitHub (or ask Claude to open a pull request for you to merge) so `/ai-visibility/` goes live.
2. 👤 Open rankandreply.com/ai-visibility/ on your phone and click every button.

## Day 8: First lead batch (about 1 hour)

1. 👤 **Apollo:** run the Segment A search (filters in [`cold-email.md`](../04-outreach/cold-email.md) §2, United States only). Export 500 contacts.
2. 👤 **MillionVerifier:** upload, keep only "good" addresses, download to `business/data/leads/a-raw.csv`.
3. 🤖 Run:
   ```bash
   python autopilot.py leads --in ../data/leads/a-raw.csv
   ```
   This runs enrich, probe (each question asked twice) and firstline. Add `--yes` when it says the batch is over 300 paid calls.
4. 👤 Open `a-raw-ready.csv`. For 20 rows, read `first_line` next to `probe_answer` (the AI's actual answer). Delete any row where they don't match.

## Day 9: Second lead batch (about 1 hour)

Same as day 8, for **Segment B** (services, United States only, with `--region` for a state). 500 contacts.

## Day 10: Sequences loaded (about 1 hour)

1. 👤 In Instantly, create 4 campaigns:

   | Campaign | Segment | Sequence |
   |---|---|---|
   | A1 | A (software) | Sequence 1 |
   | A2 | A (software) | Sequence 2 |
   | B1 | B (services) | Sequence 1 |
   | B2 | B (services) | Sequence 2 |

   Paste the copy from [`cold-email.md`](../04-outreach/cold-email.md) §3, including the footer with the "business solicitation" line.
2. 👤 Upload the ready CSVs and map the variables. **Schedule the start for day 15.** Sending window 8am–5pm in the recipient's time zone, weekdays only.
3. 🤖 Critic review:
   ```bash
   python council.py ask "You are a busy VP of Marketing. Here's a cold email. What makes you delete it? What makes you reply? Rewrite the weakest sentence." --ai chatgpt --file ../04-outreach/cold-email.md
   ```

## Day 11: Deliverability test (about 30 minutes)

1. 👤 Send one test from each of 3 inboxes to your own Gmail, Outlook and Yahoo addresses. Check that they land in the **Primary** inbox and that SPF/DKIM/DMARC show "PASS" (Gmail → ⋮ → Show original).
2. 👤 Check each domain at mail-tester.com. The target is 9/10 or better.

## Day 12: Reply process dry run (about 30 minutes)

1. 🤖 Ask Claude: *"Make a fake replies CSV in business/data/replies/test.csv with columns email, first_name, company, website, reply_text and 8 realistic replies: 2 yes, 1 price, 1 question, 1 not now, 1 has agency, 1 unsubscribe, 1 out of office. Use real company websites for the yes rows."*
2. 🤖 Run `python autopilot.py replies --in ../data/replies/test.csv`.
3. 👤 Read the outbox. Are the labels right and the drafts sendable? Ask Claude to tune the prompts if not.

## Days 13–14: Pre-flight (about 30 minutes)

- [ ] Warmup health in Instantly: 95%+ landing in the inbox
- [ ] Campaigns scheduled for day 15, at 5 emails per inbox per day
- [ ] Footer with mailbox address, "business solicitation" line and opt-out line on every step
- [ ] Suppression list created (and shared across campaigns)
- [ ] Stripe links live on the page and in `.env`
- [ ] Onboarding form linked from Stripe
- [ ] `python scout.py run` works, and any good Upwork jobs have proposals submitted (at most 5 a week)

---

## Days 15–30: The daily routine (about 1.5 hours a day, any time)

**Once a day (30–45 min): replies**
1. 👤 Export new replies from Instantly to `../data/replies/<date>.csv`. The columns should be `email`, `first_name`, `company`, `website`, `reply_text`.
2. 🤖 Run:
   ```bash
   python autopilot.py replies --in ../data/replies/2026-10-28.csv
   ```
   It tags each reply, drafts answers with Claude, runs the report for every "yes", and writes ready-to-send emails to `business/data/outbox/<date>/`.
3. 👤 Open each outbox file:
   - Skim the PDF for every "yes" (2 minutes).
   - Send the email from the inbox they replied to.
   - Read any `unsorted` reply yourself.
   - Add every `no` to Instantly's blocklist.
4. 👤 Log each report and each sale in your pipeline sheet. Copy `business/02-plan/templates/pipeline.csv` to `business/data/pipeline.csv` once, and fill in that copy. `business/data/` is never pushed, which matters because this repo is public and real contacts must not go in it.

**Once a day (20 min): leads.** Run `autopilot.py leads` on a new verified Apollo export, then check 20 rows. At full volume each sending day uses about 200 new leads, so keep 3 days queued.

**Once a day (15–20 min): Reddit and Upwork.** Run `python scout.py run`, then open the `today.html` page it prints:
- **Reddit:** read the whole thread and the subreddit rules, rewrite the draft in your own words, and post. At most 3 a day.
- **Upwork:** check the job, edit the proposal, and submit by hand. At most 5 a week.

The full rules are in [`reddit.md`](../04-outreach/reddit.md).

**Ramp:**

| From day | Emails per inbox per day | Total per day |
|---|---|---|
| 15 | 5 | 150 |
| 19 | 10 | 300 |
| 23 | 15 | 450 |

Also on **day 15**, buy 5 more domains and 15 inboxes and start warming them. **Pause any inbox whose bounce rate goes over 2%.**

**Mondays (days 15, 22, 29): council review (45 min)**
```bash
python council.py debate "Here is this week's scoreboard. Which funnel step is weakest, why, and what single change should we make this week?" --file ../data/scoreboard.csv
```
(Copy `business/02-plan/templates/scoreboard.csv` to `business/data/scoreboard.csv` once and fill in that copy.)

**Mondays (10 min): your own posts.** Run `python scout.py posts`, read the 3 LinkedIn posts, and schedule them (LinkedIn's built-in scheduler or Buffer). They publish themselves through the week.

**Fridays:** fill in the scoreboard row for the week.

**Day 30:** the decision. Look at "yes" rate × report-to-paid rate for Segment A vs B. The winner gets 90% of volume. Then start [Phase 3](90-day-plan.md#phase-3-double-down-and-systematize-days-4690).
