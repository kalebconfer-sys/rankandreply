# Running the council with just your subscriptions (no API keys)

Use this when you'd rather use the chat apps you already pay for. It takes about 10 minutes per decision.

**How it works:**
1. Paste the same **brief** into ChatGPT, Gemini and Perplexity, each in a new chat.
2. Copy their three answers into one message to Claude using the **synthesis** prompt.
3. Claude writes the decision. Save it in `business/data/decisions/`.

---

## The brief (paste into ChatGPT, Gemini and Perplexity)

Replace the parts in [brackets]. Attach or paste the file it mentions.

```
You're one of four AI advisers on a small business. Your role: [ROLE].

The business: "AI Visibility" by Rank and Reply. We measure whether ChatGPT, Gemini, Perplexity
and Claude recommend a B2B company when buyers ask for recommendations, then fix it for a monthly
fee (free snapshot → $490 Fix Plan → $1,500/month Retainer). Sold by cold email and Upwork/Fiverr
only. The founder does not do sales calls unless a buyer asks. Month-to-month, no ranking promises.

The question: [QUESTION]

Context: [PASTE THE NUMBERS, EMAIL, PAGE OR DOC]

Rules: be specific and concrete. Cite a source for any fact about the market. Say plainly when
you're guessing. Give your answer, the single biggest risk you see, and one thing you'd do this week.
Under 300 words.
```

**Roles to paste in:**
- **ChatGPT:** "Critic: the skeptical buyer and the investor who has seen 1,000 failed side businesses. Find the hole before the market does."
- **Gemini:** "Analyst: read all the material and pull out patterns, counts and outliers. Show your numbers."
- **Perplexity:** "Scout: check every claim against the live web right now and cite URLs. Flag anything outdated."

## The synthesis (paste into Claude with the three answers)

```
You're the Chair of a four-AI council for the business in the brief below. Three advisers answered
the same question. Write the decision:
1. The call, in one sentence
2. The evidence it rests on
3. Disagreements that remain, and who holds them
4. Three next actions, each with an owner (a named AI or the founder) and a finish line
5. The result that would prove this decision wrong

Brief: [PASTE THE BRIEF]
ChatGPT (Critic): [PASTE]
Gemini (Analyst): [PASTE]
Perplexity (Scout): [PASTE]
```

---

## Standing questions worth running

| When | Question |
|---|---|
| Before launch (day 5) | "Here's our cold email and 10 real snapshot results. Is the hook true, strong and safe? What makes a busy founder reply, and what makes them mark it as spam?" |
| Every Monday | "Here's this week's scoreboard. Which funnel step is weakest, why, and what single change should we make?" |
| Day 30 | "Segment A vs B numbers attached. Which do we double down on, and what would change your mind?" |
| Before any price change | "Here are the last 20 reports and who bought. Should the Fix Plan be $290, $490 or $790? What does the data say, and what's a guess?" |
| When something feels off | "Here are 10 replies that said no. What are they really telling us?" |
