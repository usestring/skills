# String Web Access skills

Agent Skills for [String Web Access](https://usestring.ai/web-access): search the web, fetch any URL and map a site, and get clean Markdown back. The skills follow the [Agent Skills](https://agentskills.io) format, so any agent that loads skills can use them, including Claude Code, Muse Code, Cursor and Codex.

This repository is the source of truth for String's skills. The [Claude Code](https://github.com/usestring/string-claude-plugin), [Cursor](https://github.com/usestring/string-cursor-plugin), [Gemini CLI](https://github.com/usestring/string-gemini-extension) and [Grok](https://github.com/usestring/string-grok-plugin) plugins carry copies that a workflow here keeps in sync. Change skills here, not in those repos.

## Skills

| Skill | What it's for |
| --- | --- |
| [`string-web-access`](skills/string-web-access) | Load it first for any multi-step web task. It covers when to search, fetch or drive a browser, and what to do about blocked or empty pages. |
| [`string-search`](skills/string-search) | Search the web and get structured results back. |
| [`string-fetch`](skills/string-fetch) | Fetch any page as clean, LLM-ready Markdown. |
| [`string-sitemap`](skills/string-sitemap) | Find every URL on a site. |
| [`string-request`](skills/string-request) | Send a POST, PUT or PATCH with a body to a URL. |

## Before you install

The skills drive String Web Access's MCP tools, so your agent needs the hosted server connected: `https://mcp.usestring.ai/v1/mcp` with an `Authorization: Bearer <your String API key>` header. Get a key at [portal.usestring.ai](https://portal.usestring.ai). The [setup docs](https://portal.usestring.ai/docs/mcp/remote) cover each client.

## Install

Any agent that supports skills:

```bash
npx skills add usestring/skills
npx skills add usestring/skills --skill string-web-access   # one skill only
```

Muse Code, one skill at a time:

```bash
git clone https://github.com/usestring/skills string-skills
muse skills install ./string-skills/skills/string-web-access --scope user
```

Claude Code: add the [String Web Access plugin](https://github.com/usestring/string-claude-plugin) marketplace, which bundles these skills with the MCP server, then install `string-web-access` from it.

```
/plugin marketplace add usestring/string-claude-plugin
```

## Keeping the plugins in sync

`.github/workflows/sync-plugins.yml` runs whenever anything under `skills/` changes on `main`. For each plugin repo listed in `.github/sync-targets.json`, it:

1. Copies `skills/` over, so the plugin's copy matches this repo exactly.
2. Bumps the plugin's patch version. The Grok marketplace and other listings only pick up a change when the version moves.
3. Opens a pull request with a GitHub-verified commit, then merges it.

If a sync adds or removes a skill, the pull request stays open so someone can update that plugin's README.

The workflow writes with the `SKILLS_SYNC_TOKEN` secret: a fine-grained token with Contents and Pull requests write access to the four plugin repos. You can also run it by hand from the Actions tab. A manual run only reports what would change unless you turn `dry_run` off. To test a change locally without writing anything:

```bash
DRY_RUN=true python3 scripts/sync_target.py usestring/string-claude-plugin
```

## License

MIT
