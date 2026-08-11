"""
03_stealth.py
-------------
Stealth fetch using a headless browser — bypasses Cloudflare Turnstile
and other JS-based anti-bot systems.
Best for: Cloudflare-protected sites, CAPTCHA walls, JS challenges.

Install: pip install "scrapling[fetchers]" && scrapling install
"""

from scrapling.fetchers import StealthyFetcher


def main():
    # solve_cloudflare=True attempts automatic Cloudflare Turnstile bypass
    # block_images=True speeds up loads by skipping image downloads
    page = StealthyFetcher.fetch(
        "https://quotes.toscrape.com",   # swap for your protected target
        headless=True,
        solve_cloudflare=True,
        block_images=True,
        network_idle=True,              # wait until network is quiet
    )

    print(f"Status: {page.status}")
    print(f"Final URL: {page.url}")

    quotes = page.css(".quote")
    print(f"Found {len(quotes)} quotes")

    for quote in quotes[:3]:
        print(quote.css("span.text::text").get())


# Tips:
# - headless=False opens a visible browser window (useful for debugging)
# - Use StealthySession for multiple requests through the same stealth session
# - If still blocked, try DynamicFetcher for full Playwright control

if __name__ == "__main__":
    main()
