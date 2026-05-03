#!/usr/bin/env python3
"""Interactively scaffold a new blog post and open it in $EDITOR."""

import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

BLOG_DIR = Path(__file__).parent.parent / "docs" / "blog"


def prompt(label: str, required: bool = False) -> str:
    suffix = "" if required else " (optional, enter to skip)"
    while True:
        value = input(f"{label}{suffix}: ").strip()
        if value or not required:
            return value
        print("  This field is required.")


def slugify(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug)
    return slug.strip("-")


def parse_tags(raw: str) -> list[str]:
    return [t.strip() for t in raw.split(",") if t.strip()]


def build_front_matter(title: str, description: str, tags: list[str]) -> str:
    lines = ["---", f"title: {title}"]
    if description:
        lines.append(f"description: {description}")
    lines.append(f"date: {date.today()}")
    if tags:
        lines.append(f"tags: [{', '.join(tags)}]")
    lines += ["comments: true", "---", ""]
    return "\n".join(lines)


def open_in_editor(path: Path) -> None:
    editor = os.environ.get("EDITOR") or os.environ.get("VISUAL")
    if not editor:
        for candidate in ("nano", "vim", "vi"):
            if subprocess.run(["which", candidate], capture_output=True).returncode == 0:
                editor = candidate
                break
    if not editor:
        print(f"No editor found. Open manually: {path}")
        return
    subprocess.run([editor, str(path)])


def main() -> None:
    print("New blog post\n")

    title = prompt("Title", required=True)
    description = prompt("Description")
    raw_tags = prompt("Tags (comma-separated)")

    slug = slugify(title)
    filename = f"{date.today()}-{slug}.md"
    post_path = BLOG_DIR / filename

    if post_path.exists():
        print(f"\nFile already exists: {post_path}")
        sys.exit(1)

    tags = parse_tags(raw_tags)
    front_matter = build_front_matter(title, description, tags)

    BLOG_DIR.mkdir(parents=True, exist_ok=True)
    post_path.write_text(front_matter, encoding="utf-8")

    print(f"\nCreated: {post_path.relative_to(Path(__file__).parent.parent)}")
    open_in_editor(post_path)


if __name__ == "__main__":
    main()
