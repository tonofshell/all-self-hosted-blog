#!/usr/bin/env python3
"""Pre-build script: inject contributor GitHub logins into blog post front matter.

Calls the GitHub REST API for each post to find committers, then patches the
front matter with `contributors: [login, ...]` so the template can render
GitHub avatar circles with links. Changes are ephemeral (CI only — never commit).
"""

import os
import re
import sys
import time
import urllib.request
import urllib.error
import json
from pathlib import Path

REPO = "tonofshell/all-self-hosted-blog"
BLOG_DIR = Path(__file__).parent.parent / "docs" / "blog"
BOT_SUFFIXES = ("[bot]",)

FRONT_MATTER_RE = re.compile(r"^---\n(.*?\n)---\n", re.DOTALL)
CONTRIBUTORS_RE = re.compile(r"^contributors:.*$", re.MULTILINE)


def github_get(path: str, token: str) -> list | dict:
    url = f"https://api.github.com/{path.lstrip('/')}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def get_contributors(file_path: str, token: str) -> list[str]:
    """Return unique non-bot GitHub logins for commits touching file_path."""
    logins: list[str] = []
    seen: set[str] = set()
    page = 1
    while True:
        try:
            commits = github_get(
                f"repos/{REPO}/commits?path={file_path}&per_page=100&page={page}",
                token,
            )
        except urllib.error.HTTPError as e:
            print(f"  API error for {file_path}: {e}", file=sys.stderr)
            break
        if not commits:
            break
        for commit in commits:
            author = commit.get("author")
            if author and (login := author.get("login")):
                if not any(login.endswith(s) for s in BOT_SUFFIXES) and login not in seen:
                    seen.add(login)
                    logins.append(login)
        if len(commits) < 100:
            break
        page += 1
        time.sleep(0.1)
    return logins


def patch_contributors(md_path: Path, logins: list[str]) -> None:
    """Inject or replace `contributors:` line in the front matter."""
    text = md_path.read_text(encoding="utf-8")
    contributors_line = f"contributors: [{', '.join(logins)}]"

    match = FRONT_MATTER_RE.match(text)
    if not match:
        print(f"  No front matter found in {md_path.name}, skipping", file=sys.stderr)
        return

    front_matter = match.group(1)
    if CONTRIBUTORS_RE.search(front_matter):
        new_fm = CONTRIBUTORS_RE.sub(contributors_line, front_matter)
    else:
        new_fm = front_matter.rstrip("\n") + f"\n{contributors_line}\n"

    new_text = f"---\n{new_fm}---\n" + text[match.end():]
    md_path.write_text(new_text, encoding="utf-8")


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN not set — skipping contributor injection", file=sys.stderr)
        return

    posts = sorted(BLOG_DIR.glob("*.md"))
    if not posts:
        print("No posts found in docs/blog/", file=sys.stderr)
        return

    for post in posts:
        rel = f"docs/blog/{post.name}"
        print(f"Processing {rel}...")
        logins = get_contributors(rel, token)
        if logins:
            print(f"  Contributors: {logins}")
            patch_contributors(post, logins)
        else:
            print(f"  No contributors found")


if __name__ == "__main__":
    main()
