---
name: string-sitemap
description: |
  Discover every URL on a website with String Web Access. Use when the user wants a site's
  full URL list, asks to crawl or map a site, needs to find all pages of a given kind
  (every blog post, every product, every docs page), or when a task needs coverage of a whole
  site rather than one page. Runs as a quoted, approved, asynchronous job — quote first,
  approve the cost, then poll and page through results.
---

# String sitemap

Every URL on a site, as an async job.

## When to use

You need breadth, not depth: all the product pages, every post in an archive, the full docs
tree. Typically to seed a batch of [fetch](../string-fetch/SKILL.md) calls.

Do not use it to find one page — that is a [search](../string-search/SKILL.md).

## The four steps

Unlike fetch and search, this is a job, not a request. It costs real crawl budget, so it is
quoted and approved before it runs.

1. **Quote** — submit the site and get an estimated cost back.
2. **Approve** — consent to that cost explicitly.
3. **Poll** — check status until the crawl completes.
4. **Page** — read results, which come back paginated.

Always surface the quote to the user and let them approve it. Do not auto-approve a crawl on
someone's behalf.

## Working with the results

A large site returns a lot of URLs. Before fetching any of them:

- **Filter by path.** `/blog/`, `/products/`, `/docs/` — the structure usually encodes the
  content type, and this is the cheapest filter you will get.
- **Decide how many you actually need.** A representative twenty often answers the question
  as well as two thousand.
- **Fetch in batches and extract as you go**, rather than fetching everything and then
  reading.

## When not to reach for it

If the site publishes an `/sitemap.xml`, a single [fetch](../string-fetch/SKILL.md) of that
file is faster and free. Try that first — sitemap discovery is for sites that do not, or
whose published sitemap is incomplete.
