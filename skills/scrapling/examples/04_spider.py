"""
04_spider.py
------------
Multi-page spider with pagination, concurrency, and JSON export.
Best for: crawling entire sites, collecting large datasets.

Install: pip install "scrapling[fetchers]"
"""

import asyncio
import json

from scrapling.spiders import Response, Spider


class QuoteSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com"]
    concurrency = 5          # parallel in-flight requests
    # Uncomment to enable pause/resume:
    # crawldir = "./checkpoints/quotes"

    async def parse(self, response: Response):
        # Yield items from the current page
        for quote in response.css(".quote"):
            yield {
                "text":   quote.css("span.text::text").get("").strip(),
                "author": quote.css(".author::text").get("").strip(),
                "tags":   quote.css(".tag::text").getall(),
                "source": response.url,
            }

        # Follow pagination automatically
        next_href = response.css("li.next a::attr(href)").get()
        if next_href:
            yield response.follow(next_href, callback=self.parse)


def run_sync():
    """Collect everything, then process."""
    spider = QuoteSpider()
    results = spider.start()           # blocks until done; returns list
    print(f"Total items: {len(results)}")
    with open("quotes_all.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Saved to quotes_all.json")


async def run_streaming():
    """Process items as they arrive — useful for large crawls."""
    spider = QuoteSpider()
    count = 0
    async for item in spider.stream():
        count += 1
        if count <= 3:
            print(f"[{count}] {item['author']}: {item['text'][:60]}…")
    print(f"Total streamed: {count}")


if __name__ == "__main__":
    # run_sync()
    asyncio.run(run_streaming())
