# Response formats

`format` decides what comes back from `web_access_fetch`. The default is `markdown`.

## markdown — the default

Navigation, ads, cookie banners and boilerplate are stripped; what remains is the content, as
Markdown. This is what you want for reading, summarizing, answering a question, or feeding a
page into further reasoning. It is also the smallest of the three, which matters when you are
fetching several pages into one context.

## raw — the verbatim body

The exact bytes the destination returned, untouched. Use it when the markup itself is the
data:

- Mining embedded JSON out of a `<script>` tag — `__NEXT_DATA__`, `application/ld+json`,
  a Redux preload
- Reading a meta tag, a canonical link, or structured data
- Fetching a file that is not a web page: XML, CSV, an existing `sitemap.xml`
- Diffing markup between two fetches

Not combinable with `actions`.

## json — the full envelope

Returns `{ statusCode, headers, data }`. Use it when the response *about* the request matters
as much as the body:

- Checking whether a page 404s, 301s or 403s
- Reading `content-type` before deciding how to parse
- Following or inspecting redirect and caching headers
- Hitting a JSON API where you want to confirm the status alongside the payload

## Picking

Start with `markdown`. Move to `raw` when you need something Markdown conversion removed, and
to `json` when the status or headers are part of the answer. Fetching `raw` "just in case"
costs context for no benefit — a large page's markup can be many times the size of its
Markdown.
