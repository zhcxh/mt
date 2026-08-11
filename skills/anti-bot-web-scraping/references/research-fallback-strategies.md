# Research Fallback Strategies When Live Data is Unavailable

## Overview
When Chinese websites and search engines block automated access (especially from cloud IPs), use these fallback strategies to gather information.

## Fallback Strategy Decision Tree

```
Start Research Task
    │
    ├─ Try direct search (Baidu, Google, Bing)
    │   └─ If blocked (CAPTCHA, 403, timeout) →
    │
    ├─ Try direct website access (Anjuke, Fang.com, etc.)
    │   └─ If blocked →
    │
    ├─ Try Wikipedia API (for geographic/administrative data)
    │   └─ If available → Use as baseline data
    │
    ├─ Try government/official sources
    │   └─ If available → Use for policy/regulatory data
    │
    └─ Compile from training knowledge
        └─ Clearly mark as "compiled from knowledge" not "live data"
```

## Strategy 1: Wikipedia API (Recommended for Geographic Data)

Wikipedia APIs are generally accessible and provide reliable baseline data for Chinese districts, cities, and administrative areas.

### Baiyun District Example
```bash
# Get full article extract
curl -s "https://en.wikipedia.org/w/api.php?action=query&titles=Baiyun,_Guangzhou&prop=extracts&exintro=false&explaintext=true&format=json"

# Get specific sections
curl -s "https://en.wikipedia.org/w/api.php?action=parse&page=Baiyun,_Guangzhou&prop=wikitext&format=json"
```

### Data Available from Wikipedia:
- Population (census data)
- Area (km²)
- Administrative subdivisions (subdistricts, towns)
- Transportation (metro lines, stations)
- Notable landmarks
- Historical information

### Limitations:
- May not have recent price data
- Policy information may be outdated
- English Wikipedia may have less detail than Chinese sources

## Strategy 2: Government/Official Sources

### Guangzhou Government Website
```bash
# Try policy documents
curl -s "https://www.gz.gov.cn/zwgk/fggw/sfbgt/"

# Try housing bureau
curl -s "https://zj.gz.gov.cn/"
```

### Limitations:
- Often require Chinese language search
- May have bot detection
- Content may be in PDF format

## Strategy 3: Compiled Knowledge from Training Data

When live data is unavailable, use compiled knowledge but **clearly mark it**.

### What to Include:
- Policy frameworks and regulations (change slowly)
- General price ranges and trends
- Infrastructure information (metro lines, schools)
- Administrative boundaries

### What NOT to Include:
- Current specific prices (change frequently)
- Recent policy changes (need verification)
- Availability of specific units

### How to Mark:
```markdown
> ⚠️ **Note**: This information is compiled from training data and may not reflect current conditions. 
> Verify with local real estate agents for up-to-date pricing.
```

## Strategy 4: User-Assisted Research

When automated access fails completely, ask the user to help:

1. **Ask user to search manually** on their device (which may have Chinese residential IP)
2. **Ask user to share screenshots** of relevant search results
3. **Ask user to copy/paste** specific data points

### Template:
```markdown
I'm unable to access Chinese real estate websites from this server due to bot detection. 
Could you please:
1. Search for "[specific query]" on Baidu/Anjuke/Fang.com
2. Share the key findings (prices, policies, etc.)
3. I'll compile the analysis based on your input
```

## Strategy 5: Alternative Data Sources

### RSS/Atom Feeds
Some sites expose RSS feeds that bypass frontend protections:
```bash
curl -s "https://example.com/rss.xml"
curl -s "https://example.com/feed"
curl -s "https://example.com/atom.xml"
```

### API Endpoints
Look for API endpoints in page source:
```bash
curl -s "https://example.com/api/v1/properties"
curl -s "https://example.com/wp-json/wp/v2/posts"
```

### Sitemap XML
May contain structured data:
```bash
curl -s "https://example.com/sitemap.xml"
curl -s "https://example.com/robots.txt"
```

## Real Estate Research Specific Patterns

### Policy Research (限购/贷款/公积金/税费)

**Key data points to gather:**
1. Purchase restrictions (限购政策)
   - Who can buy (户籍/非户籍)
   - How many properties allowed
   - Social security requirements
   
2. Mortgage policies (贷款政策)
   - Minimum down payment (首付比例)
   - Maximum loan term (贷款年限)
   - Interest rates (利率)
   
3. Provident fund policies (公积金)
   - Maximum loan amount (最高贷款额度)
   - Interest rates (利率)
   - Withdrawal rules (提取条件)
   
4. Tax policies (税费)
   - Deed tax (契税)
   - Value-added tax (增值税)
   - Income tax (个人所得税)

**Sources to check (in order):**
1. People's Bank of China (央行) - for national policies
2. Local Housing Bureau (住建局) - for local implementation
3. Local Provident Fund Center (公积金中心) - for fund policies
4. Tax Bureau (税务局) - for tax policies

### Price Research (房价/售价/均价)

**Key data points:**
1. Average price by district (区域均价)
2. New development prices (新盘售价)
3. Second-hand home prices (二手房价格)
4. Price trends (价格走势)

**Sources to check:**
1. Anjuke (安居客) - `guangzhou.anjuke.com/market/`
2. Fang.com (房天下) - `gz.fang.com/house/`
3. Lianjia (链家) - `gz.lianjia.com/`
4. Beike (贝壳) - `gz.ke.com/`

**When blocked, use:**
- Wikipedia API for district/area data
- Compiled knowledge for general price ranges
- User-assisted research for specific prices

## Common Pitfalls

1. **Don't assume live data is available** - Chinese platforms have aggressive bot detection
2. **Don't waste time on multiple search engines** - If one blocks, others likely will too
3. **Do use Wikipedia API** - It's reliable and provides good baseline data
4. **Do mark compiled knowledge clearly** - Don't present it as live data
5. **Do ask for user help** - When automated access fails completely
6. **Do check for RSS/API alternatives** - May bypass frontend protections

## Example: Guangzhou Baiyun District Research

### What Worked:
- Wikipedia API for Baiyun District demographics and transport
- Compiled knowledge for policy framework
- Anjuke partial data extraction for price trends

### What Failed:
- Baidu search (CAPTCHA)
- Google search (CAPTCHA)
- Bing search (returned unrelated results)
- DuckDuckGo search (CAPTCHA)
- Direct Anjuke/Fang.com access (bot detection)

### Lesson:
Start with Wikipedia API for geographic data, then use compiled knowledge for policies and prices. Ask user for specific current data if needed.

## References

- Chinese Platform Bot Detection: `chinese-platform-bot-detection.md`
- Chinese Rental Yield Calculation: `chinese-rental-yield-calculation.md`
