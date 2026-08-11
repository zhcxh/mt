---
name: scrapling
description: >
  Expert guide for building Python web scrapers with the Scrapling library
  (https://github.com/D4Vinci/Scrapling). Use this skill whenever the user
  wants to scrape a website, extract data from web pages, bypass anti-bot
  protections (Cloudflare, CAPTCHAs), crawl multiple pages, or automate
  browser interactions for data collection. Triggers on: web scraping,
  crawling, data extraction from websites, bypassing Cloudflare, stealth
  fetching, spider, scrapling, screen scraping, site monitoring, price
  tracking, content aggregation, or any task that involves pulling structured
  data from web pages. Always use this skill even if the user doesn't
  explicitly mention "Scrapling" - if they want to scrape the web with Python,
  this is the right tool.
---

# Scrapling Skill

Scrapling is an adaptive Python web scraping library that handles everything
from simple HTTP requests to stealth browser automation and large-scale
concurrent crawling.

## Step 0: Pick the Right Fetcher

This is the most important decision. Match the fetcher to the target site:

| Target Site | Fetcher | Why |
|---|---|---|
| Static HTML, simple APIs | `Fetcher` | Fastest, TLS fingerprint spoofing |
| Cloudflare / anti-bot walls | `StealthyFetcher` | Headless browser, bypasses JS challenges |
| Heavy JS, SPAs, login flows | `DynamicFetcher` | Full Playwright/Chrome control |
| Multi-page crawls | `Spider` class | Concurrent, with pause/resume |

When in doubt: start with `Fetcher`. If you get blocked, step up to `StealthyFetcher`.

## Step 1: Install

```bash
# Parser only (no fetching)
pip install scrapling

# Full install with fetchers + browsers
pip install "scrapling[fetchers]"
scrapling install          # downloads browser binaries
```

For everything: `pip install "scrapling[all]"`

## Step 2: Patterns

### Pattern A: Simple Fetch (Static Sites)

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://example.com', impersonate='chrome')

# CSS selectors
titles = page.css('h2.product-title::text').getall()
price  = page.css('.price::text').get()

# XPath
links = page.xpath('//a[@class="item"]/@href').getall()

# Text search
el = page.find_by_text('Add to Cart', tag='button')

# Export
page.css('.product').to_json('products.json')
```

### Pattern B: Session (Cookies, Login, Proxy Rotation)

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate='chrome') as session:
    # Login
    session.post('https://example.com/login', data={'user': 'x', 'pass': 'y'})

    # Subsequent requests carry cookies automatically
    page = session.get('https://example.com/dashboard')
    data = page.css('.data-row').getall()
```

For stealth sessions use `StealthySession`; for full browser sessions use `DynamicSession`.

### Pattern C: Stealth Fetch (Cloudflare / Anti-Bot)

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch(
    'https://protected-site.com',
    headless=True,
    solve_cloudflare=True,   # auto-solve Cloudflare Turnstile
    block_images=True,       # faster loads
)

items = page.css('.item').getall()
```

### Pattern D: Spider (Multi-Page Crawl)

```python
from scrapling.spiders import Spider, Response

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/products"]
    concurrency = 10          # parallel requests

    async def parse(self, response: Response):
        # Extract items on this page
        for card in response.css('.product-card'):
            yield {
                "title": card.css('h2::text').get(),
                "price": card.css('.price::text').get(),
                "url":   card.css('a::attr(href)').get(),
            }

        # Follow pagination
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

# Run synchronously
ProductSpider().start()

# Or stream results as they arrive
import asyncio
async def main():
    async for item in ProductSpider().stream():
        print(item)

asyncio.run(main())
```

### Pattern E: Pause & Resume (Long Crawls)

```python
class BigCrawl(Spider):
    name = "big"
    start_urls = [...]

    async def parse(self, response: Response):
        ...

# crawldir enables checkpoint persistence
BigCrawl().start(crawldir='./checkpoints/big-crawl')
# Re-run the same command to resume from where it stopped
```

### Pattern F: Adaptive Selectors (Sites That Change Layout)

```python
# adaptive=True: Scrapling remembers the element and relocates it
# automatically if the page structure changes next time
title = page.css('h1.product-title', adaptive=True).get()

# Find similar siblings (useful for lists without a shared class)
first_item = page.css('.item:first-child')
all_similar = first_item.find_similar()
```

## Selector Reference

```python
# Selection
page.css('selector')              # returns ResultSet
page.css('selector::text')        # text content
page.css('selector::attr(href)')  # attribute value
page.xpath('//div[@id="x"]')
page.find('div', class_='foo')    # BeautifulSoup-style
page.find_all('span')
page.find_by_text('Buy Now', tag='button')

# Extraction
el.get()                          # first result as string/element
el.getall()                       # all results as list

# DOM traversal
el.parent
el.next_sibling
el.previous_sibling
el.below_elements()               # elements visually below this one
el.find_similar()                 # sibling elements with same structure

# Export
page.css('.row').to_json('out.json')
page.css('.row').to_jsonl('out.jsonl')
```

## Common Gotchas

**Cloudflare Turnstile limitation (2026-08-09 实测)**: `StealthyFetcher` 的 `solve_cloudflare=True` 需要 `patchright` 模块，且对现代 Cloudflare Turnstile (Managed Challenge) 可能无效。实测中所有请求返回 403。

**更有效的替代方案**:
- DDoS-Guard → 使用 `Playwright + Stealth` (详见 `anti-bot-web-scraping` 技能)
- Cloudflare → 使用 Solverr (Docker) 或 RSS Feed 绕过
- 不要依赖 `solve_cloudflare=True` 作为唯一方案

**Rate limiting**: add delays between requests in sessions:
```python
import time
for url in urls:
    page = session.get(url)
    time.sleep(1)
```

**JavaScript-rendered content**: if `Fetcher` returns empty elements that
you can see in a browser, switch to `DynamicFetcher`.

**Selector not finding elements**: use browser DevTools to confirm the
selector, then try `page.find_by_text()` as a fallback - it's more robust
than structural selectors when a site rewrites its CSS classes.

**Large crawls**: always pass `crawldir` so a crash doesn't lose progress.

## Multi-Session Spider Routing

Route different URLs through different fetcher types within one spider:

```python
from scrapling.spiders import Spider, Response

class HybridSpider(Spider):
    name = "hybrid"
    start_urls = ["https://normal-site.com"]

    def configure_sessions(self):
        return {
            "default": {"type": "fetcher"},
            "stealth":  {"type": "stealthy", "solve_cloudflare": True},
        }

    async def parse(self, response: Response):
        yield response.follow(
            'https://protected-page.com',
            callback=self.parse_protected,
            sid="stealth",   # use the stealth session for this URL
        )

    async def parse_protected(self, response: Response):
        yield {"data": response.css('.result').getall()}
```

## Quick Decision Tree

```
Want to scrape a website?
├── Single page, no JS needed?        → Fetcher.get()
├── Need cookies / login?             → FetcherSession
├── Cloudflare or anti-bot?           → StealthyFetcher (solve_cloudflare=True)
├── Heavy JS / SPA / need clicks?     → DynamicFetcher
└── Many pages / crawl?               → Spider class
    ├── May be interrupted?           → add crawldir=
    └── Mix of protected + normal?    → configure_sessions()
```

## Overlap Notice

**scrapling** (this skill) 和 **scrapling-official**（从 GitHub 安装的库作者官方技能）内容高度重叠。
- 本技能：实战 gotchas（Cloudflare Turnstile 实测无效）、决策树、模式精简
- scrapling-official：完整 CLI 文档、references/ 目录、examples/、spider 模板

建议 curator 合并：保留本技能的 gotchas 和决策树，采纳 official 的 CLI/references/examples。

## Docs

Full reference: https://scrapling.readthedocs.io
GitHub: https://github.com/D4Vinci/Scrapling
