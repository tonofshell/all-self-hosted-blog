# All Self Hosted Blog

This is a personal blog documenting the journey of the author (Adam Shelton) through their attempts to migrate all the critical services in their life to platforms they host and maintain (within reason). 

## How you help
Your job is to foremost to lend a helping hand maintaining the blog. You should avoid creating blog content unless specifically asked. The author would prefer to keep text content of the blog itself entirely human generated. You can step into create and maintain the (very barebones) infrastructure hosting this blog (ironically) in a _**public**_ GitHub repo and GitHub pages, proofread content, or insert code/config examples and/or diagrams when asked. Add relevant information to this file as needed.

## Guardrails
- **DO NOT** change or alter blog content in any way unless asked to proofread or weigh in on content or add specific examples/diagrams.
- When adding examples/diagrams/logs or proofreading, check for and avoid sensitive personally identifiable information (e.g IP addresses, internal domain names, passwords/credentials, etc.) This is a **PUBLIC** git repo, so take all countermeasures to avoid committing this information in the first place (any suggestions here are welcome).
- **DO NOT** plagiarize! If you integrate content from elsewhere, place footnotes with the proper attribution to the original author. 

## Technical Information
- All blog entries are Markdown files, diagrams should be in the Mermaid.js format in those Markdown files.
- Keep the technical architecture as simple as possible, this is a blog not a space ship.
- **Static site generator:** [Zensical](https://zensical.org) — config file is `zensical.toml` (TOML format)
- **Dependency management:** `uv` — run `uv sync` to install deps; lockfile is `uv.lock`
- **Dev server:** `uv run zensical serve` → http://localhost:8000
- **Build:** `uv run zensical build` → outputs to `site/` (gitignored)
- **Blog posts:** Markdown files in `docs/blog/posts/`; require `date: YYYY-MM-DD` in front matter; add `comments: true` to enable giscus on a post; use `/new-post` to scaffold a new post
- **Diagrams:** Mermaid fences (` ```mermaid `) are natively supported via the superfences extension — no extra setup
- **Comments:** giscus — configured in `overrides/partials/comments.html`; the `data-repo-id` and `data-category-id` placeholders must be replaced with values from [giscus.app](https://giscus.app) after enabling GitHub Discussions on the repo
- **Deployment:** GitHub Actions via `cssnr/zensical-action@v1` → GitHub Pages → `allselfhosted.blog`; trigger: push to `main`

## Color Palette — Rust & Coast

Custom colors defined in `docs/stylesheets/extra.css`. The modern Zensical theme header does not use the primary color variable by default, so `.md-header` is targeted directly.

### Light mode (`[data-md-color-scheme="default"]`)
| Role | Hex | WCAG contrast on white |
|------|-----|------------------------|
| Primary (links, active nav) | `#C0390A` | 7.9:1 ✓✓ |
| Primary light variant | `#E64A19` | — |
| Primary dark variant | `#8D1A00` | — |
| Accent (buttons, highlights) | `#4F3B8C` | 7.5:1 ✓✓ |
| Header background | `#C0390A` (direct `.md-header` override) | — |

### Dark mode (`[data-md-color-scheme="slate"]`)
| Role | Hex |
|------|-----|
| Primary (links, active nav) | `#F05A20` |
| Primary light variant | `#FF7043` |
| Primary dark variant | `#C0390A` |
| Accent (buttons, highlights) | `#1CB89E` |
| Header background | `#1C0902` (direct `.md-header` override) |

### Notes
- `--md-primary-fg-color` drives text links and interactive elements; `--md-accent-fg-color` drives buttons and hover highlights
- The modern Zensical theme uses `--md-default-bg-color--light` for the header background, not `--md-primary-fg-color` — do not remove the direct `.md-header` CSS rules or the header will revert to the default neutral color
- To change the palette in future, update both `[data-md-color-scheme]` blocks in `extra.css` and the direct `.md-header` overrides below them

## Proofreading Guidelines
- **ALWAYS** check with the author before making changes (even minimal ones).
- Try to make edits in way that respect the tone and style of the author as reflected in their other articles.
