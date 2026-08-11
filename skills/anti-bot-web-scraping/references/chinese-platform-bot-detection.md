# Chinese Platform Bot Detection Patterns

## Overview
Chinese web platforms (real estate, e-commerce, social media) use different bot detection mechanisms than Western CDN protections (Cloudflare, DDoS-Guard). This document captures observed patterns and workarounds.

## Observed Platforms & Detection Mechanisms

### 58.com / Anjuke (安居客)
- **Detection Type**: JavaScript challenge + CAPTCHA
- **Trigger**: Automated browser access to search/listing pages
- **Response**: Redirects to verification page with "点击按钮进行验证" button
- **Workaround**: 360搜索摘要; Baidu search with AI summaries; direct API access if available

### Lianjia / Ke.com (链家/贝壳找房)
- **Detection Type**: Request fingerprinting + behavioral analysis
- **Trigger**: Automated browser with standard fingerprints
- **Response**: "访问已被拦截" (Access blocked) with 拦截 ID
- **Error Page**: Shows "Forbidden" with security check failure message
- **Workaround**: 360搜索摘要; avoid direct access

### Fang.com (房天下) — CONFIRMED WORKING (2026-08-11)
- **Detection Type**: Regional routing + bot detection
- **Trigger**: Using wrong regional subdomain
- **Response**: Redirects to wrong region (e.g., Beijing instead of Guangzhou)
- **Workaround**: Use regional subdomain URLs (see below)

#### Regional URL Structure
- Guangzhou: `gz.esf.fang.com/house/kw{URL_ENCODED_NAME}/`
- Beijing: `esf.fang.com/house/...` (default when no city prefix)
- Pattern: `{city_code}.esf.fang.com` where city_code = gz, bj, sh, sz, etc.
- Search URL: `https://gz.esf.fang.com/house/kw%E4%B8%80%E5%93%81%E6%B9%96%E5%B1%B1/`

#### Price Data Extraction (Browser Console Technique)
Fang.com listing pages embed prices in DOM text like "336万34870元/㎡". When CSS selectors return empty (the site uses dynamic class names), use this approach:

```javascript
// Step 1: Find all elements containing price data
const els = document.querySelectorAll('*');
const data = [];
els.forEach(el => {
  const text = el.textContent;
  if (text && text.includes('万') && text.includes('元/㎡') && text.length < 300) {
    data.push(text.trim());
  }
});
const unique = [...new Set(data)];

// Step 2: Parse with regex
unique.forEach(item => {
  const match = item.match(/(\d+)室(\d+)厅\s*\|\s*([\d.]+)㎡\s*\|\s*(高层|中层|低层)（共(\d+)层）\s*\|\s*(南向|北向|东南向|南北向)/);
  const priceMatch = item.match(/(\d+)万([\d,]+)元\/㎡/);
  if (match && priceMatch) {
    console.log({
      rooms: match[1] + '室' + match[2] + '厅',
      area: match[3] + '㎡',
      floor: match[4],
      totalFloors: match[5],
      orientation: match[6],
      totalPrice: priceMatch[1] + '万',
      unitPrice: priceMatch[2] + '元/㎡'
    });
  }
});
```

#### Listing Data Text Pattern
```
{小区名}{描述}{户型} {N}室{N}厅 | {面积}㎡ |{楼层} （共{总楼层}层） | {朝向} {总价}万{单价}元/㎡
```
Example: `一品湖山小区环境好高层视野开阔 3室2厅 | 137.7㎡ |中层 （共17层） | 南北向 一品湖山 南湖满五年...490万35585元/㎡`

### Baidu Baike (百度百科)
- **Detection Type**: Page availability varies by entry
- **Trigger**: Some property entries return 404
- **Response**: Error page with no content
- **Workaround**: Use Baidu search snippets which contain summarized content

### Bing CN (必应中文版)
- **Detection Type**: Encoding issues with Chinese queries
- **Trigger**: Chinese character queries from non-Chinese IPs
- **Response**: Returns completely unrelated English results (e.g., medical ICD codes instead of property info)
- **Workaround**: Use 360搜索 instead; Bing CN is unreliable for Chinese content from cloud IPs

### 360搜索 (so.com) — ✅ RELIABLE (2026-08-11)
- **Detection Type**: None observed (from cloud IPs)
- **Trigger**: N/A — works reliably
- **Response**: Full Chinese search results with AI summaries
- **优势**: 不触发CAPTCHA，支持中文查询，整合360百科，返回安居客/搜狐焦点摘要
- **使用**: `browser_navigate(url="https://www.so.com/s?q=查询内容")`
- **注意**: curl方式可能偶尔空结果，浏览器方式更可靠

## Effective Fallback Strategy

### ⚠️ Critical: IP Location Matters

**From cloud/server IPs (AWS, GCP, Azure, etc.):** ALL Chinese platforms AND Baidu search are blocked. The server IP `2600:1f14:3ac0:...` (US cloud) was blocked by every platform tested:

| Platform/Engine | Status | Error |
|----------------|--------|-------|
| ke.com / lianjia.com | ❌ Blocked | "Forbidden" with 拦截 ID |
| anjuke.com / 58.com | ❌ Blocked | CAPTCHA verification page |
| fang.com | ❌ Blocked | Empty response / redirect |
| Baidu Search | ❌ Blocked | Connection closed |
| Bing CN | ❌ Failed | Returns unrelated results (encoding issue) |
| DuckDuckGo | ❌ Blocked | CAPTCHA required |
| Google | ❌ Blocked | IP-based CAPTCHA |
| 小红书 (Xiaohongshu) | ❌ Blocked | IP risk detected |
| Web Archive | ❌ Blocked | 429 Too Many Requests |
| **360搜索 (so.com)** | ✅ **Works** | No CAPTCHA, full Chinese results |

**From residential Chinese IPs:** Baidu search with AI summaries works well and is the recommended fallback.

### Strategy by IP Location

**If you have a Chinese residential IP or VPN:**

1. **Baidu Search with AI Summaries**: Search `site:domain.com + keywords` or general queries
   - Baidu's AI often generates comprehensive summaries from multiple sources
   - Snippets contain key property details (developer, year, units, fees)
   - **Price trend data** often appears in Baidu search results (see below)

2. **Multiple Search Queries**: Use different keyword combinations:
   - Property name + "详情" (details)
   - Property name + "物业费" (management fee)
   - Property name + "周边配套" (surrounding amenities)
   - Property name + "开发商" (developer)
   - Property name + "售价 均价" (selling price, average price)

3. **Cross-reference Sources**: Compare information from:
   - Baidu AI summaries
   - Search result snippets
   - Different real estate platforms (if accessible)

**If you only have cloud/server IPs (no Chinese VPN):**

1. **360搜索 (so.com)**: 首选搜索引擎，不触发CAPTCHA
2. **政府/政协提案**: 最精确的本地信息来源
3. **Solverr/Docker**: Deploy Solverr with a Chinese proxy for browser automation
4. **User manually browses**: Ask the user to search on their own device and share results
5. **Accept data unavailability**: Honestly report that Chinese rental data cannot be accessed from this IP
6. **Do NOT waste time** trying: CORS proxies, Google Translate proxy, web archives — all blocked too

## Baidu Price Trend Data Extraction

Baidu search results often include property price trend summaries in a structured format. Example from search for "一品湖山 广州 白云 同和路 售价 均价":

```
36545 元/平 环比 0.07% 同比 1.81%
南湖商圈 36154元/平
白云区 25816元/平
上涨0.06% 下降0.62% 上涨0.07% 下降2.71%
```

This data includes:
- **Current average price** (元/平)
- **Month-over-month change** (环比)
- **Year-over-year change** (同比)
- **Area/commercial district average** (商圈)
- **District average** (区)

## Chinese Real Estate Property Data Points

When researching Chinese residential properties, typical data includes:

| Field | Chinese Term | Notes |
|-------|--------------|-------|
| Developer | 开发商 | Usually a group/co. Ltd. |
| Property Management | 物业公司/物业 | Often subsidiary of developer |
| Management Fee | 物业费 | 元/㎡·月 (yuan per sqm per month) |
| Total Units | 总户数 | Approximate |
| Building Types | 建筑类型 | 小高层/多层/别墅/洋房 |
| Floor Count | 层数/楼层 | May need inference from building type |
| Plot Ratio | 容积率 | Lower = less dense |
| Green Coverage | 绿化率 | Higher = more greenery |
| Year Built | 建成年份/竣工 | May have phases |
| Total Area | 占地面积/总建筑面积 | In 万平方米 |
| Subway Distance | 距地铁 | In kilometers |
| Schools | 周边学校 | Public and private |
| Medical | 医院 | Nearby hospitals |

## Building Type Floor Ranges (Inference)

If exact floor count not stated:

| Building Type | Chinese | Typical Floors |
|--------------|---------|----------------|
| 别墅 (Villa) | 别墅/联排别墅 | 2-3 |
| 多层洋房 | 多层 | 4-6 |
| 小高层 | 小高层 | 10-18 |
| 高层 | 高层 | 18-33 |
| 超高层 | 超高层 | 33+ |

## Pitfalls

1. **Don't waste time on direct access** to Lianjia/Ke.com/Anjuke without proper anti-bot setup
2. **360搜索 is the best cloud-IP fallback** for Chinese content search
3. **Government sources are underutilized** — 政协提案 databases have more precise local data than property platforms
4. **Bing CN fails for Chinese queries** from cloud IPs — encoding issues cause irrelevant results
5. **Cross-reference multiple searches** - different queries surface different details
6. **Watch for renamed properties** - some were renamed due to "大、洋、怪" place name rectification in 2019
7. **Phase differences** - properties may have multiple phases with different completion years
8. **Fang.com URL encoding**: Use UTF-8 percent encoding for Chinese characters in search URLs (e.g., `%E4%B8%80%E5%93%81%E6%B9%96%E5%B1%B1` for "一品湖山")
9. **CSS selectors may fail on Fang.com**: The site uses dynamic class names; fall back to text content search with `document.querySelectorAll('*')` and filter by price keywords
