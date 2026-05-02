Create a new blog post scaffold for this Zensical blog.

Ask the user for:
- Post title (required)
- Short description (optional, 1 sentence)

Then:
1. Slugify the title (lowercase, spaces → hyphens, remove special chars)
2. Create `docs/blog/posts/<slug>.md` with this front matter:

```
---
title: <title>
description: <description or omit if not provided>
date: <today's date as YYYY-MM-DD>
comments: true
---
```

Leave the body completely empty after the front matter — the author writes all content.

Do NOT add any placeholder body text, section headers, or suggestions. The file should end immediately after the closing `---`.

Confirm the file path created and remind the author that `comments: true` enables giscus on this post.
