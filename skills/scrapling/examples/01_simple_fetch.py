"""
01_simple_fetch.py
------------------
Basic HTTP fetch using Scrapling's Fetcher.
Best for: static HTML pages, simple APIs, no JavaScript required.

Install: pip install "scrapling[fetchers]"
"""

from scrapling.fetchers import Fetcher


def main():
    # TLS fingerprint impersonates Chrome — helps avoid basic bot detection
    page = Fetcher.get("https://quotes.toscrape.com", impersonate="chrome")

    # --- CSS selectors ---
    quotes = page.css(".quote")
    for quote in quotes:
        text = quote.css("span.text::text").get()
        author = quote.css(".author::text").get()
        tags = quote.css(".tag::text").getall()
        print(f"{author}: {text}")
        print(f"  tags: {', '.join(tags)}")
        print()

    # --- XPath ---
    all_authors = page.xpath("//small[@class='author']/text()").getall()
    print(f"Authors on this page: {all_authors}")

    # --- Text search (robust against CSS class changes) ---
    next_btn = page.find_by_text("Next", tag="a")
    if next_btn:
        print(f"Next page link: {next_btn.attrib.get('href')}")

    # --- Export to JSON ---
    page.css(".quote").to_json("quotes.json")
    print("Saved to quotes.json")


if __name__ == "__main__":
    main()
