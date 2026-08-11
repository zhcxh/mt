# scrapling — Claude Code Skill

> A Claude Code skill that turns any web-scraping request into production-ready
> [Scrapling](https://github.com/D4Vinci/Scrapling) code — from a single static
> fetch to a concurrent, Cloudflare-bypassing spider.

[![Skill](https://img.shields.io/badge/Claude%20Code-Skill-blue?logo=anthropic)](https://github.com/anthropics/claude-code)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://www.python.org/)
[![Scrapling](https://img.shields.io/badge/Scrapling-latest-orange)](https://github.com/D4Vinci/Scrapling)
[![CI](https://github.com/Chiragsd13/scrapling-skill/actions/workflows/validate.yml/badge.svg)](https://github.com/Chiragsd13/scrapling-skill/actions/workflows/validate.yml)

---

## What this skill does

When you describe a web-scraping task in Claude Code, this skill automatically:

- **Picks the right fetcher** (static HTTP, stealth browser, or full Playwright)
- **Generates a complete, runnable scraper** with proper error handling
- **Handles anti-bot** scenarios (Cloudflare Turnstile, TLS fingerprinting)
- **Scaffolds spiders** for multi-page crawls with pagination and pause/resume
- **Applies adaptive selectors** that survive site redesigns

## Triggers

The skill activates on phrases like:

- "scrape this website…"
- "extract data from…"
- "bypass Cloudflare and get…"
- "crawl all pages of…"
- "build a spider for…"
- "price monitor for…"
- "download product listings from…"

---

## Install the skill

```bash
# Clone into your Claude Code skills directory
git clone https://github.com/Chiragsd13/scrapling-skill \
  ~/.claude/skills/scrapling
```

Claude Code picks up new skills automatically — no restart needed.

---

## Scrapling quick-start

```bash
pip install "scrapling[fetchers]"
scrapling install          # downloads browser binaries (one-time)
```

### Simple fetch

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://example.com', impersonate='chrome')
titles = page.css('h1::text').getall()
print(titles)
```

### Cloudflare bypass

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch(
    'https://protected-site.com',
    headless=True,
    solve_cloudflare=True,
)
print(page.css('.content::text').get())
```

### Multi-page spider

```python
from scrapling.spiders import Spider, Response

class MySpider(Spider):
    name = "demo"
    start_urls = ["https://quotes.toscrape.com"]

    async def parse(self, response: Response):
        for q in response.css('.quote'):
            yield {
                "text":   q.css('span.text::text').get(),
                "author": q.css('.author::text').get(),
            }
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

MySpider().start()
```

See the [`examples/`](examples/) directory for all six patterns.

---

## Fetcher decision guide

| Scenario | Use |
|---|---|
| Static HTML / simple API | `Fetcher` |
| Login / cookies / proxy | `FetcherSession` |
| Cloudflare / JS challenge | `StealthyFetcher` |
| Heavy SPA / need clicks | `DynamicFetcher` |
| Multi-page crawl | `Spider` |
| Mix of protected + normal | `Spider` + `configure_sessions()` |

---

## Examples

| File | What it shows |
|---|---|
| [`01_simple_fetch.py`](examples/01_simple_fetch.py) | CSS, XPath, text-search selectors |
| [`02_session.py`](examples/02_session.py) | Login flow with persistent cookies |
| [`03_stealth.py`](examples/03_stealth.py) | Cloudflare bypass, block images |
| [`04_spider.py`](examples/04_spider.py) | Paginated crawl, JSON export |
| [`05_adaptive.py`](examples/05_adaptive.py) | Adaptive selectors + `find_similar()` |
| [`06_hybrid_spider.py`](examples/06_hybrid_spider.py) | Multi-session routing per URL |

---

## Skill file

The full skill instructions live in [`SKILL.md`](SKILL.md). Claude Code loads
this file when the skill triggers and uses it to guide code generation.

---

## Contributing

1. Fork → branch → PR
2. Keep examples runnable and self-contained
3. Keep `SKILL.md` under 500 lines

---

## Links

- Scrapling repo: https://github.com/D4Vinci/Scrapling
- Scrapling docs: https://scrapling.readthedocs.io
- Claude Code: https://claude.ai/code
