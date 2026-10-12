# Reddit and Upwork: finding buyers, and posting without getting banned

## The short version

| | **Look** (finding posts) | **Post** |
|---|---|---|
| **Reddit** | **Automated.** F5Bot emails you when your keywords appear on Reddit. `scout.py` reads those emails, searches reddit.com through Perplexity (or Claude), scores each thread, and drafts a reply | **You, by hand**, from your own account, after rewriting the draft in your own words. **Reddit Ads** is the one legitimate way to post without typing it yourself (Phase 3 test) |
| **Upwork** | **Automated.** Upwork's saved-search email alerts → `scout.py` drafts a proposal for each new job | **You submit by hand.** Bots that submit proposals get accounts banned |

Your part: **about 15–20 minutes a day**, plus 10 minutes on Mondays:
- **Daily:** run `python scout.py run` and open the page it prints (`today.html`). Every post is listed with an **Open** button (goes to the thread or job) and a **Copy** button (copies the draft). Open, read, copy, rewrite in your own words, post. Tick "done".
- **Mondays:** run `python scout.py posts`. You get 3 posts for your own LinkedIn profile. Schedule all 3 at once, and they publish on their own through the week.

## Can a bot post for me anywhere?

**Not where business buyers are.** In 2026 every major platform has moved against automated replies:

| Platform | Can the bot find posts? | Can a bot post replies? | What we do |
|---|---|---|---|
| Reddit | Yes, via F5Bot emails and Perplexity search (Reddit's own API needs approval) | No. Reddit's spam policy covers bots and AI used for promotion | You post by hand |
| Hacker News | Yes. F5Bot covers it for free | No | You post by hand |
| X | Yes, via Syften (paid) | No. Since Feb 2026 X's API blocks automated replies unless the person @mentioned you ([X developers via Tekedia](https://www.tekedia.com/x-restricts-programmatic-bot-replies-to-boost-genuine-users-interaction/)) | You reply by hand |
| Stack Exchange, Bluesky | Yes, via Syften (paid) | Many Stack Exchange sites ban AI-written answers | You post by hand |
| LinkedIn | No (its user agreement bans bots and scraping) | **Your own posts: yes**, through LinkedIn's built-in scheduler or Buffer. Comments and DMs: no | **3 posts a week on autopilot** (below) |
| Upwork | Yes, via its email alerts | No. Bots that submit proposals get banned | You submit by hand |

So the bot does the searching, scoring and writing. Your own LinkedIn posts publish themselves once scheduled. Replies to other people's posts are yours to send.

## Your own posts on autopilot (LinkedIn)

`python scout.py posts` writes 3 posts a week:
- **A data post** built only on real numbers from your reports, such as "of 6 companies I checked this month, the median was named in 15% of answers." It never names or hints at which companies you checked. If there are no reports yet, it skips this post.
- **A how-to**, for example how to check what ChatGPT says about your company yourself.
- **An answer** to a question people asked online that week, paraphrased, never quoting anyone.

Schedule them once: on desktop, LinkedIn > Start a post > paste > clock icon, or connect LinkedIn to Buffer. They go out Monday, Wednesday and Friday at 8:00 am. Read each one first and change anything that doesn't sound like you.

Why it's worth 10 minutes a week: when someone gets your cold email or sees your Reddit reply and looks you up, they find a profile with useful, specific posts. That makes everything else convert better.

## Why the AI doesn't post on Reddit for you

- **Reddit closed its API to self-service in November 2025.** Every app now needs explicit approval under its [Responsible Builder Policy](https://support.reddithelp.com/hc/en-us/articles/42728983564564-Responsible-Builder-Policy). A marketing tool is unlikely to be approved.
- **Reddit's RSS feeds are reported to shut down on November 13, 2026** ([report](https://www.newsbytesapp.com/news/science/reddit-is-killing-rss-feeds-over-scraping-concerns/story)). Reddit already returns errors to many automated clients. A tool built on either would break.
- **Reddit actively removes this exact behavior:**
  - Its spam policy (updated March 2026) treats bots and generative AI used for spam as spam.
  - It removes about 100,000 bot accounts a day.
  - In July 2026 it announced a crackdown on marketers seeding posts so AI chatbots repeat them, catching about 25,000 spammy posts and comments a day ([The Next Web](https://thenextweb.com/news/reddit-ai-marketing-slop-geo-crackdown), [eMarketer](https://www.emarketer.com/content/reddit-geo-crackdown-could-raise-stakes-ai-visibility-strategies)).
- **A banned account is a lost channel.** Reddit is the most-cited site in AI answers (11.3% of responses, per Semrush via eMarketer). That's why marketers spam it, and why Reddit polices it hard.

So the AI does all the looking and drafting, and the posting stays human. A real person posting genuinely helpful answers is welcome on Reddit. A bot is not.

## One-time setup (about 30 minutes)

1. **F5Bot (free Reddit alerts).** Sign up at f5bot.com with the email the scout will read, and add these keywords:
   ```
   recommended by ChatGPT
   show up in ChatGPT
   ChatGPT recommends
   AI search visibility
   generative engine optimization
   answer engine optimization
   GEO agency
   AEO agency
   AI Overviews traffic
   LLM visibility
   ```
   F5Bot also watches Hacker News for the same keywords at no cost. It throttles very common keywords, so keep them specific.
   **Optional, paid:** Syften (about $20–40/month) reportedly also watches X, Bluesky, Stack Exchange and more. If you add it, point its email alerts at the same inbox; the scout already reads `syften.com` emails.
2. **Upwork saved searches with email alerts:** see [`marketplaces.md`](marketplaces.md).
3. **Let the scout read those alert emails** (choose one):
   - **Automatic:** turn on 2-Step Verification in your Google account, create an **App password** named "scout", and put `IMAP_USER` and `IMAP_PASSWORD` in `business/tools/.env`. The scout opens the inbox **read-only**, fetches only emails from `upwork.com` and `f5bot.com`, and never marks, moves or deletes anything. You can revoke the app password any time. Better still, send the alerts to a separate Gmail address used only for alerts, and give the scout that one.
   - **Manual:** save the alert emails as `.eml` files into `business/data/scout/eml/` and run `python scout.py run --eml-dir ../data/scout/eml`.
4. **Your Reddit account:**
   - Use a real account with an honest profile ("Kaleb. I run Rank and Reply, which measures how AI assistants recommend businesses").
   - **For the first 2 weeks, only answer questions; never mention the business.** That builds the history that keeps comments from being filtered as spam.
5. **Optional:** edit `business/tools/scout_queries.txt`, the searches run against reddit.com. The best queries sound like a buyer, not a marketer.

## Every day (15–20 minutes)

```bash
python scout.py run
```

Then open the page it prints: `business/data/outbox/<date>/today.html`. Each item has the link, what the alert showed, a score (buyer, peer or irrelevant), the draft and a Copy button. The same drafts are also saved as `scout-*.txt` files.

**Reddit (at most 3 replies a day):**
1. Open the link and read the **whole thread**. The alert only shows part of it, and someone may already have answered.
2. Read the subreddit's rules (sidebar or "About"). If they ban self-promotion or AI-written content, keep your reply 100% advice with no mention of the business, or skip it.
3. **Rewrite the draft in your own words.** Never paste it unedited. Some communities ban AI-written posts, and your own voice is what makes it credible.
4. Post. Don't send DMs unless they ask.

**Upwork:**
1. Open the job and check it's fixed-price, still open, and within the rules in [`marketplaces.md`](marketplaces.md).
2. Edit the draft and submit by hand. At most 5 a week.

## Our Reddit rules (these protect the account)

1. **Helpful first.** Every reply must be worth upvoting even if the last line were deleted.
2. **Disclose.** If you mention Rank and Reply, say it's yours.
3. **One in ten.** At most 1 in every 10 of your comments mentions the business.
4. **No links** unless someone asks and the subreddit allows them.
5. **No alt accounts, no vote manipulation**, and no asking friends to upvote.
6. **Never post for clients.** We don't seed Reddit to improve a client's AI visibility. That's exactly what Reddit is removing, and it puts the client's brand at risk. (This is also in the delivery rules.)
7. **Never invent experience.** No "I've helped dozens of companies" until it's true.
8. **If a moderator removes a comment or warns you, stop posting in that subreddit.**

## Where to look

Check each subreddit's rules before posting. Communities change, and some ban vendors entirely.

| Who | Subreddits to watch | What you're there for |
|---|---|---|
| Software founders and marketers (Segment A buyers) | r/SaaS, r/startups, r/Entrepreneur, r/marketing, r/DigitalMarketing, r/content_marketing | Answer "why doesn't ChatGPT mention us?" questions |
| Managed IT and service-firm owners (Segment B buyers) | r/msp, r/smallbusiness | Same, for service businesses |
| Agency owners (white-label partners) | r/agency, r/DigitalMarketing | Agencies asking how to offer AI search work |
| SEO peers | r/SEO, r/bigseo | Learn, and build credibility. These are rarely buyers |

## Reddit Ads: the legitimate way to "post" at scale (Phase 3 test)

- **What it is:** Self-serve Reddit Ads lets you run promoted posts targeted at communities and interests. The minimum is reported at $5/day; B2B clicks are estimated at about $0.50–4 ([Stackmatix](https://stackmatix.com/blog/reddit-ads-cost-guide-2026), [Omneky](https://www.omneky.com/blog/how-much-does-reddit-ads-cost)). Check live minimums in Ads Manager.
- **The test (from day 46):** a promoted post offering the free report, targeted at communities like r/SaaS, r/startups and r/marketing. Run it at $15/day for 14 days, about $210.
- **The finish line:** a cost per "yes, send the report" under about $40. If it beats cold email on cost per paying client, scale it.
- **The rules:** ads must follow Reddit's ad policies. Same rule as everywhere: no guaranteed-ranking claims.

## What to expect

Reddit is a slow, trust-building channel. Expect a handful of good conversations a month, not a flood. Its real value:
- **Credibility:** people who've seen your helpful answers reply to your emails.
- **Market research:** you'll see exactly how buyers phrase the problem, which feeds the cold-email copy and the buyer questions in the reports.
- **Occasional buyers:** people who ask for help outright.

Sources for this page: [`../01-research/sources/reddit-upwork-access.md`](../01-research/sources/reddit-upwork-access.md).
