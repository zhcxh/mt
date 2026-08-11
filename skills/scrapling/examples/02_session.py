"""
02_session.py
-------------
Session-based scraping: login, persistent cookies, multiple requests.
Best for: authenticated pages, multi-step workflows, proxy rotation.

Install: pip install "scrapling[fetchers]"
"""

import time

from scrapling.fetchers import FetcherSession


def main():
    # Context manager handles session cleanup automatically
    with FetcherSession(impersonate="chrome") as session:
        # Step 1: Perform login
        login_resp = session.post(
            "https://quotes.toscrape.com/login",
            data={"username": "admin", "password": "admin"},
        )
        print(f"Login status: {login_resp.status}")

        # Step 2: Cookies are carried automatically on subsequent requests
        page = session.get("https://quotes.toscrape.com/")
        quotes = page.css(".quote span.text::text").getall()
        print(f"Got {len(quotes)} quotes after login")

        # Step 3: Polite crawl — respect the server with a short delay
        for path in ["/page/2/", "/page/3/"]:
            page = session.get(f"https://quotes.toscrape.com{path}")
            count = len(page.css(".quote").getall())
            print(f"{path} → {count} quotes")
            time.sleep(1)  # be polite


# For stealth sessions:
#   from scrapling.fetchers import StealthySession
#   with StealthySession(...) as session: ...
#
# For full browser sessions:
#   from scrapling.fetchers import DynamicSession
#   with DynamicSession(...) as session: ...

if __name__ == "__main__":
    main()
