# Source notes: automated access to Reddit and Upwork (2026-10-12)

Web searches run before building `scout.py`. Reddit itself can't be opened from the research environment, so these rest on Reddit's help-center page and on third-party reporting. Re-check the dates before relying on them.

## Reddit

| Claim | Source | Strength |
|---|---|---|
| API access requires a request and explicit approval (Responsible Builder Policy) | [Reddit Help](https://support.reddithelp.com/hc/en-us/articles/42728983564564-Responsible-Builder-Policy) | **Official** |
| Self-service API keys ended around Nov 11, 2025; approval takes weeks and can be refused without reasons | [fetchlayer.dev](https://fetchlayer.dev/blog/reddit-api-closed-2026), [postwire.io](https://postwire.io/platforms/reddit/approval/), [redditapis.com](https://www.redditapis.com/blogs/reddit-data-api-2026) | Third party; some sell alternatives |
| RSS feeds still work but end Nov 13, 2026; Reddit returns 403 to many automated clients | [NewsBytes](https://www.newsbytesapp.com/news/science/reddit-is-killing-rss-feeds-over-scraping-concerns/story), [pasqualepillitteri.it](https://pasqualepillitteri.it/es/news/19944/reddit-cierra-feeds-rss-scraping-ia), [redditapis.com](https://www.redditapis.com/blogs/reddit-rss-feed-vs-api-2026) | Consistent news reports; Reddit's own announcement not found |
| Spam policy (updated Mar 28, 2026) treats bots and generative AI used for spam as spam; [App] label for permitted automation (Mar 25, 2026); about 100,000 bot accounts removed per day | Search summaries of Reddit policy and announcements ([Digital Trends](https://www.digitaltrends.com/?p=5987835), [ppc.land](https://ppc.land/reddit-bots-threaten-ad-quality-heres-how-the-platform-fights-back/)) | Secondhand |
| July 6, 2026: crackdown on AI-marketing "GEO" seeding; about 25,000 spammy posts and comments caught daily | [The Next Web](https://thenextweb.com/news/reddit-ai-marketing-slop-geo-crackdown), [The Star](https://www.thestar.com.my/tech/tech-news/2026/07/07/reddit-is-cracking-down-on-ai-marketing-slop-with-its-own-ai), [eMarketer](https://www.emarketer.com/content/reddit-geo-crackdown-could-raise-stakes-ai-visibility-strategies) | Multiple outlets (Bloomberg-sourced) |
| Reddit is the top-cited domain in LLM answers (11.3% across ChatGPT Search, Perplexity, Google AI Mode, per Semrush) | [eMarketer](https://www.emarketer.com/content/reddit-geo-crackdown-could-raise-stakes-ai-visibility-strategies) | Vendor data via trade press |
| F5Bot (free keyword email alerts for Reddit, HN, Lobsters) still running in 2026; throttles keywords with more than 50 mentions/day. Syften about $20–100/mo | [redship.io](https://redship.io/blog/f5bot-alternatives-reddit-monitoring), [getairefs.com](https://getairefs.com/blog/f5bot-alternatives-2026/) | Vendor comparison blogs |
| Reddit Ads self-serve minimum about $5/day; B2B CPC estimates $0.50–4 | [Stackmatix](https://stackmatix.com/blog/reddit-ads-cost-guide-2026), [Omneky](https://www.omneky.com/blog/how-much-does-reddit-ads-cost), [Enrich Labs](https://www.enrichlabs.ai/blog/reddit-ads-complete-guide-2026) | Vendor blogs; check in Ads Manager |

## Upwork

| Claim | Source | Strength |
|---|---|---|
| RSS feeds discontinued after Aug 20, 2024; saved searches and email alerts are the official replacement | [Upwork Help](https://support.upwork.com/hc/en-us/articles/52052528243731-RSS-deprecation) | **Official** |
| Alert emails can be late (hours) and noisy | Freelancer comments via [upworkalerts.com](https://upworkalerts.com/blog/upwork-rss-feed-alternative), [snipework.com](https://snipework.com/blog/upwork-rss-feed-2026) | Anecdotal |
| Bots that auto-submit proposals risk bans; AI drafts a human reviews and sends are tolerated | [giguphq](https://giguphq.com/blog/upwork-ai-proposals-banned-2026) (see `marketplaces.md` sources) | Unverified against Upwork's ToS text |

## Perplexity search options used by scout.py

`search_domain_filter` (up to 20 domains) and `search_recency_filter` (hour/day/week/month/year), with results in `search_results` ([Perplexity docs](https://docs.perplexity.ai/guides/chat-completions-guide), [promptfoo](https://promptfoo.dev/docs/providers/perplexity)). The exact field set should be confirmed against the official docs on day 3.
