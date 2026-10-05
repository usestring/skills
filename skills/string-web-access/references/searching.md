# Writing search queries

`web_access_search` runs a real Google query, so query craft transfers directly.

## Principles

**One question per query.** Two topics in one search returns results that serve neither. Run
two searches.

**Use the page's vocabulary, not the user's.** Someone asks "how much does it cost"; the page
says "pricing". Someone asks "is it down"; the page says "status" or "incident". Translate
before searching.

**Date anything time-sensitive.** Without a year, rankings favour whatever has accumulated
links, which skews old. `kubernetes ingress best practices 2026` beats the undated version.

**Scope to a site when you know it.** `site:docs.stripe.com webhook signature` goes straight
there instead of through five aggregators.

**Exclude noise.** `-pinterest -quora` removes the usual suspects from product research.

**Quote exact phrases** when the wording matters — an error string, a product name, a legal
term.

## Sharpen rather than fetch hopefully

When results look off, the instinct is to fetch the top three and hope. A second, sharper
query is cheaper and usually better. Reformulate when:

- The results are about the right words but the wrong topic — your vocabulary is off
- Everything is a listicle or an aggregator — add `site:` or a more specific term
- The results are old — add the year
- You get the company but wanted the concept, or vice versa — add a disambiguating word

## Then read the snippets

Search returns `position`, `title`, `url`, `snippet` and `displayUrl`. The snippet answers the
question outright more often than people expect. Scan all of them, pick the two or three URLs
that genuinely earn a fetch, and skip the rest.
