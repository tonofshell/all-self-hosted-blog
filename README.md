# All Self Hosted

A personal blog documenting one person's attempt to migrate their critical services away from big-tech platforms and onto hardware they own and control — one painful lesson at a time.

Live at [allselfhosted.blog](https://allselfhosted.blog)

## Stack

- **Static site generator:** [Zensical](https://zensical.org)
- **Hosting:** GitHub Pages
- **Deployment:** GitHub Actions on push to `main`
- **Comments:** [giscus](https://giscus.app) (GitHub Discussions)
- **Color scheme:** Auto light/dark based on system preference; manual toggle available
- **Contributors:** GitHub avatar circles on each post, populated from git history via `scripts/get_contributors.py` in CI

## Local Development

```bash
uv sync
uv run zensical serve     # → http://localhost:8000
```

## Adding a Post

```bash
# Scaffold a new post
/new-post
```

Posts live in `docs/blog/` as `YYYY-MM-DD-slug.md` files. Supported front matter:

```yaml
---
title: Post Title
description: One-sentence summary for SEO and Open Graph.
date: YYYY-MM-DD
tags: [docker, homelab, networking]
comments: true
---
```
