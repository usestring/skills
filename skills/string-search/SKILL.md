---
name: string-search
description: |
  Search the web with String Web Access and get structured Google results back. Use when the
  user wants to search the web, find articles or sources, look up current information, check
  recent news, or says "search for", "find me", "look up", "what's the latest on", "who is",
  or asks anything needing information from the live internet rather than training data.
  Returns organic results with position, title, URL, snippet and display URL.
---

# String search

Google results, structured.

## When to use

You have a question but no URL yet. This is step one of the
[escalation rule](../string-web-access/SKILL.md): **search** → fetch → browser.

Do not use it when you already have the URL — go straight to
[string-fetch](../string-fetch/SKILL.md) and save a round trip.

## Call it

```json
{ "query": "anthropic claude pricing per million tokens" }
```

`query` is the only parameter. Be specific and descriptive — this is a real Google query, so
everything you know about writing one applies.

## What comes back

An array of organic results, each with:

| Field | What it is |
| --- | --- |
| `position` | Rank in the results |
| `title` | Page title |
| `url` | Full URL — pass this to `web_access_fetch` |
| `snippet` | Google's extract, often enough on its own |
| `displayUrl` | The breadcrumb Google shows |

## Read the snippets first

The snippet frequently answers the question outright. Fetching every result by reflex is the
most common way to make a research task slow and expensive. Scan the snippets, decide which
two or three pages actually earn a fetch, then fetch those.

## Writing a good query

- **One question per search.** Two topics in one query returns results for neither.
- **Use the words the page would use**, not the words the user used. A page about pricing
  says "pricing", not "how much does it cost".
- **Add a site when you know it**: `site:docs.stripe.com webhook signature`.
- **Add a year for anything time-sensitive** — otherwise you get whatever ranks, which skews
  old.
- **Search again rather than fetching hopefully.** A second, sharper query is cheaper than
  three speculative fetches.

## Limits

Results are organic Google results only — no ads, no knowledge panel, no "people also ask".
If you need the content of a result, that is a separate `web_access_fetch` call.
