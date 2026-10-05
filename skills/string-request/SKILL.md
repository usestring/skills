---
name: string-request
description: |
  Send a POST, PUT or PATCH with a body to a URL, through String Web Access. Use when the user
  wants to submit something to an endpoint rather than read a page — calling a JSON API that
  needs a payload, posting to a webhook, updating a record. For reading a page, use
  string-fetch instead.
---

# String request

Send a POST, PUT or PATCH request to any URL, through String's Web Access API.

## When to use

The user wants to *send* something, not read something. If you only need a page's content,
this is the wrong tool — use [string-fetch](../string-fetch/SKILL.md).

This is deliberately separate from `web_access_fetch`. A tool that both reads and writes cannot
be marked read-only, and read-only tools run without asking the user first. Keeping the write
here is what lets a write prompt and a read not.

## Call it

```json
{
  "url": "https://api.example.com/items",
  "method": "POST",
  "body": { "name": "widget" }
}
```

`url` and `method` are required. `method` must be `POST`, `PUT` or `PATCH` — `GET` is refused,
because reads belong on `web_access_fetch`.

## Parameters

| Parameter | Use it when |
| --- | --- |
| `body` | A string is sent as-is; an object is JSON-stringified |
| `format` | Defaults to `json`, the `{ statusCode, headers, data }` envelope. A write's caller usually needs the status code more than prose |
| `headers` | The endpoint needs an auth header or a specific content type. Max 50 |
| `countryCode` | The endpoint is geo-gated. ISO 3166-1 alpha-2, e.g. `"US"` |
| `solveCaptcha` | Defaults true. Set false to fail fast instead of waiting on a challenge |

`executeJS` and `actions` are not available here. Both run a browser session, and a browser
session is always a GET.

## Care

This sends a real request to a real endpoint, and the caller chose that endpoint. Confirm the
URL and the payload with the user before sending anything that changes state, and never retry a
failed write in a loop — a timeout does not tell you the write did not land.
