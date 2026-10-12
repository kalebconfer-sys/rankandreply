# The AI team: who does what

Five AIs, one human. Each AI has one job it is best at. The human does only what an AI legally or physically can't: owning accounts, paying for things, clicking "submit" where a platform requires a person, and getting on a call with a buyer who has already said yes in writing.

| Seat | AI | Best at | Owns in this business |
|---|---|---|---|
| **Chair** | Claude | Reasoning, writing, code, building the deliverable | Final calls; writes every client deliverable; builds automations; writes outreach copy; synthesizes the council |
| **Scout** | Perplexity | Live web search with citations | Each morning: new Upwork/forum posts that match our offer; verifies prices, competitors and facts before we rely on them |
| **Critic** | ChatGPT | A strong second opinion with different training | Red-teams every plan, offer and email before it ships; plays the skeptical buyer; drafts objection replies |
| **Analyst** | Gemini | Huge context, cheap per token, free tier | Reads big lead lists and 50 job posts at once; finds patterns in replies; weekly numbers review |
| **Worker** | Local model (Ollama) | Free, unlimited, private | Bulk jobs: scoring and filtering leads, first-draft personalization lines, tagging replies (interested / not now / unsubscribe) |
| **Owner** | You | Legal identity, money, judgment | Accounts and payments; approve anything that goes out under your name; video calls with buyers who already agreed to buy |

## How they work together

1. **The Scout finds.** Perplexity (or Claude with web search) pulls fresh buyer signals: job posts, forum threads, businesses showing a specific gap.
2. **The Worker sorts.** The local model scores every lead against the ideal-customer checklist for free. Only the top slice goes to paid models.
3. **The Chair writes.** Claude writes the personalized email, the proposal or the deliverable.
4. **The Critic attacks.** ChatGPT reads it as the buyer and as a spam filter, then sends back the three weakest points.
5. **The Chair fixes and ships.** You approve, or a rule you've already set approves for you.
6. **The Analyst reviews.** Once a week, Gemini reads every send, reply and sale, and the council debates what to change.

## Two ways to run the council

**With API keys (automated):** `python business/tools/council.py debate "question" --file some-doc.md` runs every AI with a key, has each one critique the others, and has Claude write the decision. See `business/tools/README.md`.

**With just your subscriptions (no keys, copy-paste):** use `council-prompts.md`. Paste the same brief into ChatGPT, Gemini and Perplexity, paste their three answers back into Claude, and Claude writes the decision. It takes about 10 minutes and costs nothing extra.

## Rules every AI follows

- **No invented proof.** No fake testimonials, case studies, client counts or results. Until there are real clients, we sell the deliverable, the price and the guarantee.
- **Cite or flag.** Any number used in a decision has a source link, or is marked as an estimate.
- **Platform rules are hard limits.** Upwork forbids bots that submit proposals and forbids taking clients off-platform before a contract. LinkedIn forbids automated scraping and messaging. We follow both.
- **Email law is a hard limit.** Every cold email has a real sender, an honest subject line, a physical mailing address and a working one-click opt-out. Opt-outs are honored permanently.
- **The human approves anything sent under their name** until a sequence has run clean for two weeks. After that, approved templates can send on their own.
