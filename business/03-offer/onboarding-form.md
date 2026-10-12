# Onboarding form

Build this once in Tally (free) or Google Forms. Set it as Stripe's "after payment" redirect, so every buyer lands on it the moment they pay. No call.

**Title:** Let's get you into the answer

1. Company name *
2. Website *
3. Your email for approvals and reports *
4. Who buys from you? (job title, company size, industry) *
5. Up to 5 competitors you lose deals to *
6. The questions buyers ask before they buy. List up to 5, in their words *
7. Anything we must never say, claim or compare against? (legal, partners, sensitive competitors)
8. How should we publish pages? *
   - Invite us as an editor on our site (WordPress / Webflow / other) and we'll publish drafts for your approval
   - Send us the pages and we'll publish them ourselves
9. Paste 2–3 links to writing you like in your own voice
10. Which review sites or directories are you already listed on? (G2, Capterra, Clutch, industry directories...)
11. Anything else we should know?

**Confirmation message:** "Thanks. Your first report and plan arrive within 5 business days. Questions? Just reply to any email from us. You'll never need to book a call."

**Automation:** Form submission → a row in the Clients sheet → council runs `visibility.py snapshot --questions` with their questions plus generated ones. Until n8n or Zapier is wired up in phase 3, you run this step by hand.
