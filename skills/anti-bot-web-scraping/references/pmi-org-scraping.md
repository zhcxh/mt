# PMI.org Anti-Bot Scraping Notes

## Site Profile
- **URL**: `https://www.pmi.org`
- **Protection**: Cloudflare (JS Challenge + Turnstile, Turnstile `enabled: false` in config)
- **SPA Framework**: React + Coveo Headless Search
- **Data Source**: Coveo Cloud Search API (OrganizationId: `projectmanagementinstituteproductionlqzthlnw`)

## What Works

### curl_cffi (first request only)
```python
from curl_cffi import requests
session = requests.Session(impersonate='chrome')
r = session.get('https://www.pmi.org/learning/authorized-training-partners/find', timeout=30)
# Status: 200 — returns full HTML shell (325KB)
# But: SPA data (training partners) is loaded client-side via Coveo JS
# Caveat: Subsequent requests from same session may get 403
```

### Coveo Search Token
- Embedded in HTML as `"AccessToken":"eyJhbG...cekU"` (truncated with `...`)
- Client-side JS replaces with real token at runtime
- Cannot extract valid token from static HTML alone
- Coveo Cloud API endpoint: `https://{orgId}.org.coveo.com/rest/search/v2`
- Requires Bearer auth — 401 without token

## What Does NOT Work

### Playwright Headless
- Consistently blocked by Cloudflare "Just a moment..." challenge
- Even with anti-detection scripts (`navigator.webdriver`, chrome runtime mock)
- Waited up to 60s — challenge never completes

### Hermes Browser Tools
- Returns "Error | PMI" / "Something unexpected happened..."
- No residential proxies = aggressive bot detection

### Google Cache
- Blocked: "unusual traffic from your computer network"

### Direct Coveo API
- 401 without valid access token
- Token is session-bound and truncated in SSR HTML

## fnOS Chrome Browser (fygo-browser) Workaround
The fnOS Chrome browser (installed via App Center) CAN load PMI pages
successfully because it's a real Chrome instance. However:
- Runs inside an iframe → cannot interact with page content via outer browser tools
- CDP endpoint not exposed on standard ports
- The Chrome browser has "CDP 自动化能力" per description, but endpoint location unknown
- Useful for: manual browsing / screenshots. Not useful for: programmatic scraping

## Region Filter (ATP Page)
The ATP search page has a Location filter with regions:
- Asia Pacific (49), Europe (73), Middle East and North Africa (33)
- North America (881), South Asia (10), Sub-Saharan Africa (11)
- Afghanistan falls under "South Asia" or "Middle East and North Africa"

## Recommendation
For PMI.org scraping, the only reliable approach is a **real browser session**
(not headless) with proper fingerprinting. Consider:
1. Running headed Playwright on a machine with display (Xvfb)
2. Using SeleniumBase with `uc=True` (undetected-chromedriver)
3. Using the fnOS Chrome browser for manual verification
