# rankandreply.com

Marketing site for Rank and Reply — Google Business Profile posts and review
replies for home-services contractors, operated by RevivaCatch LLC (PA).

Static, hosted on GitHub Pages. No build step, no dependencies: three HTML files
with inline CSS. Edit and push.

| File | Purpose |
|---|---|
| `index.html` | The whole marketing site |
| `privacy-policy.html` | **Required by Google.** The OAuth consent screen won't pass review without a live privacy policy carrying the Limited Use disclosure and naming every third party that touches Google user data |
| `terms-of-service.html` | Service terms — flat fee, no contract, no guaranteed results |
| `CNAME` | Custom domain for Pages |

## Things not to break

- **The privacy policy is load-bearing, not boilerplate.** It names Anthropic and
  Telegram as processors of Google user data because they genuinely are, and it
  carries the Google API Services User Data Policy Limited Use language verbatim.
  A reviewer who finds an undisclosed transfer rejects the API application.
- **No results claims anywhere.** There are no clients yet, so there are no case
  studies, no testimonials, and no lead-volume numbers. The lead-mix figures on
  the page are published industry benchmarks, framed as such.
- The pricing on the page ($800 / $1,500) is quoted in outreach. Change both
  together or neither.

The bot that does the actual work lives at `C:\Users\kaleb\content-bot`.
