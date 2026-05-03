# All Self Hosted

A personal blog documenting one person's attempt to migrate their critical services away from big-tech platforms and onto hardware they own and control — one painful lesson at a time.

Live at [allselfhosted.blog](https://allselfhosted.blog)

## Stack

- **Static site generator:** [Zensical](https://zensical.org)
- **Hosting:** GitHub Pages
- **Deployment:** GitHub Actions on push to `main`
- **Comments:** [giscus](https://giscus.app) (GitHub Discussions)

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

Posts live in `docs/blog/posts/` as Markdown files with `date: YYYY-MM-DD` in the front matter.
