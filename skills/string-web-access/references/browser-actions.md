# Browser actions

`web_access_interact` opens `url` in a real browser session, runs its `actions` in order, and
returns the page as it stands after the last step. Use it only when the content does not exist
in the document until something happens to the page — a consent gate, a search form, a "load
more" button, a tab that renders on click, rows that only appear once scrolled into view.

It is the slowest and most expensive path. Try a plain fetch, then `executeJS`, before this.

## Constraints

- At most **50 actions**. There is no screenshot step.
- Besides `url` and `actions`, it takes `format` (`markdown`, or `json` for the page's HTML) and
  `countryCode`, and no `headers`. A browser session is always a GET; a request with a body
  belongs to `web_access_request`.

## Action types

| Type | Key fields |
| --- | --- |
| `wait` | `selector` + `timeout` (waits for the element), or `milliseconds` (max 30000) |
| `click` | `selector`; `all: true` clicks every match rather than the first |
| `write` | `text` — types into the focused element |
| `press` | `key`, e.g. `"Enter"` |
| `scroll` | `direction` (`up`/`down`/`left`/`right`), `amount` in pixels; `selector` scrolls that element |
| `hover` | `selector` |
| `selectOption` | `selector`, `value` (or an array for a multi-select) |
| `navigate` | `url` — keeps the session's cookies and state |

## Prefer waiting on a selector

`wait` with a `selector` returns as soon as the element appears. `wait` with `milliseconds`
always burns the full duration, and is a guess that breaks when the site is slow. Use the
selector form unless there is genuinely nothing to wait for.

## Patterns

**Past a consent gate**

```json
{
  "url": "https://example.com/article",
  "actions": [
    { "type": "click", "selector": "button[data-testid='accept-all']" },
    { "type": "wait", "selector": "article", "timeout": 10000 }
  ]
}
```

**Submit a search form**

```json
{
  "url": "https://example.com",
  "actions": [
    { "type": "click", "selector": "input[name='q']" },
    { "type": "write", "text": "annual report" },
    { "type": "press", "key": "Enter" },
    { "type": "wait", "selector": ".results", "timeout": 15000 }
  ]
}
```

**Load more, then capture**

```json
{
  "url": "https://example.com/products",
  "actions": [
    { "type": "scroll", "direction": "down", "amount": 2000 },
    { "type": "click", "selector": "button.load-more" },
    { "type": "wait", "selector": ".product-card:nth-child(40)", "timeout": 15000 }
  ]
}
```

## Multi-step flows across pages

`navigate` carries cookies and session state forward, so a login on step one still applies on
step five. Keep flows as short as they can be — every action is latency, and a 30-step
sequence is far more likely to break on a selector than a 5-step one.
