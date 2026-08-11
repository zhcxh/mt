"""
06_hybrid_spider.py
-------------------
Multi-session spider: route different URLs through different fetcher types
within a single crawl (e.g., HTTP for normal pages, stealth for protected ones).
Best for: crawls that mix public and Cloudflare-protected pages.

Install: pip install "scrapling[fetchers]" && scrapling install
"""

from scrapling.spiders import Response, Spider


class HybridSpider(Spider):
    name = "hybrid"
    # Start on a normal page
    start_urls = ["https://quotes.toscrape.com"]

    def configure_sessions(self):
        """
        Return a mapping of session-id → session config.
        The "default" session handles start_urls and any request
        that doesn't specify a sid.
        """
        return {
            "default": {
                "type": "fetcher",
                "impersonate": "chrome",
            },
            "stealth": {
                "type": "stealthy",
                "headless": True,
                "solve_cloudflare": True,
                "block_images": True,
            },
        }

    async def parse(self, response: Response):
        # Extract items from the normal page
        for quote in response.css(".quote"):
            yield {
                "text":   quote.css("span.text::text").get("").strip(),
                "author": quote.css(".author::text").get("").strip(),
                "via":    "default-session",
            }

        # Follow a protected URL through the stealth session
        # In a real spider, swap this URL for the actual protected target
        yield response.follow(
            "https://quotes.toscrape.com/page/2/",
            callback=self.parse_protected,
            sid="stealth",          # <-- use the stealth session for this one
        )

    async def parse_protected(self, response: Response):
        for quote in response.css(".quote"):
            yield {
                "text":   quote.css("span.text::text").get("").strip(),
                "author": quote.css(".author::text").get("").strip(),
                "via":    "stealth-session",
            }


if __name__ == "__main__":
    results = HybridSpider().start()
    for item in results[:5]:
        print(f"[{item['via']}] {item['author']}: {item['text'][:60]}")
    print(f"\nTotal: {len(results)}")
