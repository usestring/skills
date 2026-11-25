---
name: string-fetch
description: |
  Fetch any web page and get clean, LLM-ready Markdown back, via String Web Access. Use when
  the user gives you a URL, asks you to read, open, summarize or extract from a page, or when
  a search result needs its full content. Also supports custom headers and country-specific
  proxies. Reads only — to click, type or scroll before capture, use web_access_interact; to
  send a POST, PUT or PATCH, use string-request.
---

# String fetch

One URL in, clean Markdown out.

## When to use

You have a URL. This is step two of the
[escalation rule](../string-web-access/SKILL.md): search → **fetch** → browser.

These tools need no API key. If they are missing or ask for sign-in, see
[string-web-access](../string-web-access/SKILL.md).

## Call it

The common case is one parameter:

```json
{ "url": "https://example.com/pricing" }
```

Everything below is optional and should stay off unless a plain fetch has actually failed.

## Parameters

| Parameter | Use it when |
| --- | --- |
| `format` | `markdown` (default, for reading), `raw` (verbatim body), `json` (envelope with `statusCode`, `headers`, `data`) |
| `executeJS` | The body comes back empty or as a loading shell — the page is client-rendered. Cannot be combined with `headers` |
| `headers` | The site requires a specific header. Max 50. Not supported with `executeJS` |
| `countryCode` | The page is geo-gated or serves regional content. ISO 3166-1 alpha-2, e.g. `"US"` |

There is no `solveCaptcha` parameter. The connection's String key decides whether a challenge
page is attempted, and a key made at sign-in starts with solving off.

## Examples

```json
// Read a page
{ "url": "https://news.ycombinator.com" }

// A client-rendered app that returns an empty shell
{ "url": "https://app.example.com/dashboard", "executeJS": true }

// Regional pricing
{ "url": "https://example.com/pricing", "countryCode": "DE" }

// You need the status code and headers, not just the body
{ "url": "https://example.com/api/health", "format": "json" }
```

This tool only issues a GET. A JSON API that wants a POST belongs to
[string-request](../string-request/SKILL.md), and a page whose content only exists after a
click, scroll or form submit belongs to `web_access_interact`: see
[browser actions](../string-web-access/references/browser-actions.md).

## Choosing a format

`markdown` strips navigation, ads and boilerplate, which is what you want for reading and
what keeps the response small. Reach for `raw` only when you need the exact bytes — parsing
embedded JSON out of a `<script>` tag, checking a meta tag, diffing markup. Reach for `json`
when the destination's status code or headers are part of the answer.

## When it comes back wrong

An empty body usually means client-rendered content: set `executeJS: true`. Markup that says
"verify you are human" or "access denied" means you got a block page, not the page — retry
once, then vary `countryCode`. Content that only appears after interaction needs
`web_access_interact`.

Never wrap this in your own retry loop. An identical repeat re-rolls the same outcome.
Change a parameter instead.
