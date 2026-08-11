"""
05_adaptive.py
--------------
Adaptive selectors: Scrapling learns element positions and relocates them
automatically when the site structure changes.
Best for: long-running scrapers that must survive site redesigns.

Install: pip install "scrapling[fetchers]"
"""

from scrapling.fetchers import Fetcher


def main():
    page = Fetcher.get("https://quotes.toscrape.com", impersonate="chrome")

    # --- Adaptive CSS selector ---
    # Scrapling stores a fingerprint of this element. If the site moves it,
    # the selector still works on the next run.
    first_quote_text = page.css("span.text", adaptive=True).get()
    print(f"First quote (adaptive): {first_quote_text}")

    # --- find_similar: locate sibling elements by structure ---
    # Useful when list items share structure but not a common class name.
    first_card = page.css(".quote:first-child")
    all_cards = first_card.find_similar()
    print(f"Found {len(all_cards)} similar quote cards via find_similar()")

    # --- DOM traversal ---
    quote = page.css(".quote")
    if quote:
        author_el = quote.css(".author")
        if author_el:
            parent = author_el.parent          # .quote element
            sibling = author_el.next_sibling   # next element after author
            print(f"Parent tag: {parent.tag if parent else 'none'}")
            print(f"Next sibling: {sibling.tag if sibling else 'none'}")

    # --- below_elements: find elements visually below a landmark ---
    header = page.css("div.col-md-8 h1")
    if header:
        below = header.below_elements()
        print(f"Elements below header: {len(below)}")


if __name__ == "__main__":
    main()
