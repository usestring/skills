#!/usr/bin/env python3
"""Mirror this catalog's skills/ into one plugin repository.

Usage: sync_target.py <owner/repo>

The target's settings come from .github/sync-targets.json. With DRY_RUN=true the script
only reports what would change. Otherwise it needs GH_TOKEN with Contents and Pull requests
write access to the target, and it lands the change as one verified commit on a branch, opens
a pull request, and merges it unless the set of skills changed.
"""

import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CATALOG = Path(__file__).resolve().parent.parent
UMBRELLA = "string-web-access"
COMMIT_MUTATION = """
mutation($input: CreateCommitOnBranchInput!) {
  createCommitOnBranch(input: $input) { commit { oid url } }
}
"""


def run(*cmd, cwd=None, stdin=None):
    result = subprocess.run(cmd, cwd=cwd, input=stdin, text=True, capture_output=True)
    if result.returncode != 0:
        sys.exit(f"{' '.join(cmd)} failed:\n{result.stderr.strip()}")
    return result.stdout


def gh_json(*args, stdin=None):
    return json.loads(run("gh", "api", *args, stdin=stdin))


def skill_names(root):
    if not (root / "skills").is_dir():
        return []
    names = sorted(p.name for p in (root / "skills").iterdir() if (p / "SKILL.md").is_file())
    # The escalation skill is the one agents should load first, so manifests list it first.
    if UMBRELLA in names:
        names.remove(UMBRELLA)
        names.insert(0, UMBRELLA)
    return names


def bump_patch(path):
    text = path.read_text(encoding="utf-8")
    match = re.search(r'("version"\s*:\s*")(\d+)\.(\d+)\.(\d+)(")', text)
    if not match:
        sys.exit(f"no semantic version found in {path}")
    old = f"{match.group(2)}.{match.group(3)}.{match.group(4)}"
    new = f"{match.group(2)}.{match.group(3)}.{int(match.group(4)) + 1}"
    path.write_text(text[: match.start(2)] + new + text[match.end(4):], encoding="utf-8")
    return old, new


def set_skill_list(path, names):
    """Rewrite every "skills": [...] array in a JSON manifest, keeping its indentation."""
    text = path.read_text(encoding="utf-8")

    def replace(match):
        line_start = text.rfind("\n", 0, match.start()) + 1
        indent = re.match(r"[ \t]*", text[line_start:]).group(0)
        items = ",\n".join(f'{indent}  "./skills/{name}"' for name in names)
        return f"{match.group(1)}[\n{items}\n{indent}]"

    updated, count = re.subn(r'("skills"\s*:\s*)\[[^\]]*\]', replace, text)
    if count == 0:
        sys.exit(f'no "skills" array found in {path}')
    path.write_text(updated, encoding="utf-8")


def add_changelog_entry(path, version, catalog_sha):
    text = path.read_text(encoding="utf-8")
    entry = f"## {version}\n\n- Synced skills from usestring/skills@{catalog_sha[:7]}.\n\n"
    first = text.find("\n## ")
    if first == -1:
        path.write_text(text.rstrip("\n") + "\n\n" + entry, encoding="utf-8")
    else:
        path.write_text(text[: first + 1] + entry + text[first + 1:], encoding="utf-8")


def changed_paths(repo_dir):
    status = run("git", "status", "--porcelain", "-uall", cwd=repo_dir)
    additions, deletions = [], []
    for line in status.splitlines():
        code, path = line[:2], line[3:]
        if "D" in code:
            deletions.append(path)
        else:
            additions.append(path)
    return additions, deletions


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    repo = sys.argv[1]
    targets = json.loads((CATALOG / ".github" / "sync-targets.json").read_text(encoding="utf-8"))
    target = next((t for t in targets if t["repo"] == repo), None)
    if target is None:
        sys.exit(f"{repo} is not listed in .github/sync-targets.json")

    dry_run = os.environ.get("DRY_RUN", "false").lower() == "true"
    catalog_sha = os.environ.get("GITHUB_SHA") or run("git", "rev-parse", "HEAD", cwd=CATALOG).strip()
    if not dry_run and not os.environ.get("GH_TOKEN"):
        sys.exit("GH_TOKEN is empty. Add the SKILLS_SYNC_TOKEN secret, or run with DRY_RUN=true.")

    with tempfile.TemporaryDirectory() as tmp:
        clone = Path(tmp) / "target"
        run("git", "clone", "--quiet", "--depth", "1", f"https://github.com/{repo}.git", str(clone))
        before = skill_names(clone)
        shutil.rmtree(clone / "skills", ignore_errors=True)
        shutil.copytree(CATALOG / "skills", clone / "skills")

        if not run("git", "status", "--porcelain", "-uall", "--", "skills", cwd=clone).strip():
            print(f"{repo}: skills already match usestring/skills@{catalog_sha[:7]}")
            return

        after = skill_names(clone)
        old_version, new_version = bump_patch(clone / target["version_file"])
        for manifest in target.get("skill_lists", []):
            set_skill_list(clone / manifest, after)
        if target.get("changelog"):
            add_changelog_entry(clone / target["changelog"], new_version, catalog_sha)

        additions, deletions = changed_paths(clone)
        added = sorted(set(after) - set(before))
        removed = sorted(set(before) - set(after))
        skill_set_changed = bool(added or removed)

        print(f"{repo}: version {old_version} -> {new_version}")
        for path in additions:
            print(f"  write  {path}")
        for path in deletions:
            print(f"  delete {path}")
        if skill_set_changed:
            print(f"  skill set changed: added {added or '-'}, removed {removed or '-'}")
        if dry_run:
            return

        branch = f"sync/skills-{catalog_sha[:7]}"
        base_oid = run("git", "rev-parse", "HEAD", cwd=clone).strip()
        existing = gh_json(f"repos/{repo}/pulls?state=open&head={repo.split('/')[0]}:{branch}")
        if existing:
            print(f"{repo}: {existing[0]['html_url']} is already open for this catalog commit")
            return
        gh_json(f"repos/{repo}/git/refs", "-f", f"ref=refs/heads/{branch}", "-f", f"sha={base_oid}")

        catalog_url = f"https://github.com/usestring/skills/commit/{catalog_sha}"
        payload = {
            "query": COMMIT_MUTATION,
            "variables": {
                "input": {
                    "branch": {"repositoryNameWithOwner": repo, "branchName": branch},
                    "expectedHeadOid": base_oid,
                    "message": {
                        "headline": f"Sync skills from usestring/skills@{catalog_sha[:7]}",
                        "body": f"Mirrors skills/ from {catalog_url} and bumps the version to {new_version}.",
                    },
                    "fileChanges": {
                        "additions": [
                            {"path": p, "contents": base64.b64encode((clone / p).read_bytes()).decode()}
                            for p in additions
                        ],
                        "deletions": [{"path": p} for p in deletions],
                    },
                }
            },
        }
        commit = gh_json("graphql", "--input", "-", stdin=json.dumps(payload))
        print(f"{repo}: committed {commit['data']['createCommitOnBranch']['commit']['url']}")

        body = [
            f"Mirrors `skills/` from [usestring/skills@{catalog_sha[:7]}]({catalog_url}). "
            "That repository is the source of truth for these files, so edit skills there rather than here.",
            "",
            f"- Version: {old_version} → {new_version}",
            f"- Files written: {len(additions)}, deleted: {len(deletions)}",
        ]
        if skill_set_changed:
            body += [
                f"- Skills added: {', '.join(added) or 'none'}; removed: {', '.join(removed) or 'none'}",
                "",
                "The set of skills changed, so the README's skill table needs a hand update. "
                "This PR was left open instead of merging automatically.",
            ]
        if target.get("resubmit_note"):
            body += ["", target["resubmit_note"]]
        pr = gh_json(
            f"repos/{repo}/pulls",
            "-f", f"title=Sync skills from usestring/skills@{catalog_sha[:7]}",
            "-f", f"head={branch}",
            "-f", "base=main",
            "-f", "body=" + "\n".join(body),
        )
        print(f"{repo}: opened {pr['html_url']}")
        if skill_set_changed:
            return

        gh_json("-X", "PUT", f"repos/{repo}/pulls/{pr['number']}/merge", "-f", "merge_method=squash")
        run("gh", "api", "-X", "DELETE", f"repos/{repo}/git/refs/heads/{branch}")
        print(f"{repo}: merged {pr['html_url']}")


if __name__ == "__main__":
    main()
