# Chinese Fiscal & Property Market Data Research Guide

## Data Sources Hierarchy

### Tier 1: Official Government Data (最权威)
| Source | URL | Content |
|--------|-----|---------|
| 财政部 (MOF) | mof.gov.cn/gkml/caizhengshuju/ | Fiscal revenue/expenditure, land transfer revenue |
| 自然资源部 | mnr.gov.cn | Land use statistics, natural resources bulletins |
| 国家统计局 (NBS) | stats.gov.cn | GDP, CPI, investment data |
| 住建部 | mohurd.gov.cn | Housing policy, market stabilization |
| 中国人民银行 (PBOC) | pbc.gov.cn | Interest rates, LPR, mortgage rates |
| 国务院 | gov.cn | Policy documents, central economic work conference |

### Tier 2: Authoritative Chinese Media (权威媒体)
| Source | Type | Data Quality |
|--------|------|-------------|
| 新华社/新华网 | State news agency | Policy announcements, official data |
| 人民日报 | Party newspaper | Policy interpretation |
| 财新 | Financial media | In-depth analysis, expert quotes |
| 第一财经 | Financial media | Detailed fiscal data, market analysis |
| 央广网 | State broadcasting | Data compilation, city-level analysis |
| 中国房地产报 | Industry paper | Property-specific data |

### Tier 3: Research/Analysis (研究分析)
| Source | Type | Value |
|--------|------|-------|
| 任泽平研究报告 | Economist | Land finance dependency analysis |
| 中指院 (China Index Academy) | Research institute | City-level land revenue rankings |
| 三个皮匠报告 | Research aggregator | Industry reports compilation |
| 克而瑞 (CRIC) | Property data | Market transaction data |

## Key Data Points & How to Find Them

### 1. National Land Transfer Revenue (全国土地出让金)
**Search queries**:
- `全国土地出让金 2024 2025 同比 数据`
- `地方政府性基金 国有土地使用权出让收入`
- `财政部 土地出让收入 年度`

**Typical data format**: "X万亿元，同比下降Y%"
**Key sources**: 财政部年度财政收支报告, 自然资源部年度公报

### 2. City-Level Land Revenue (城市土地出让金)
**Search queries**:
- `[城市名] 土地出让金 2024 2025 同比`
- `[城市名] 土拍 收金 数据`
- `300城 宅地出让金 排名`

**Key cities to track**: 北京、上海、广州、深圳、杭州、成都、南京、武汉

### 3. Land Finance Dependency Ratio (土地财政依赖度)
**Search queries**:
- `土地财政依赖度 排名 城市`
- `土地出让金 地方财政 占比`
- `房地产税收 地方财政贡献`

**Formula**: 土地财政依赖度 = 土地出让金 / 地方一般公共预算收入 × 100%

### 4. Local Government Debt (地方政府债务)
**Search queries**:
- `地方政府债务 余额 2024 2025`
- `政府法定负债率`
- `地方政府专项债`

**Key metric**: 政府法定负债率 = 政府债务余额 / GDP × 100%
**Threshold**: 国际警戒线 60%，中国2024年末为 60.9%

### 5. Property Market Policy (房地产政策)
**Search queries**:
- `取消限购 城市 列表 2024 2025`
- `房贷利率 LPR 下调`
- `止跌回稳 政策`
- `保交房 白名单`

### 6. Mortgage Rate Data (房贷利率)
**Search queries**:
- `房贷利率 最新 2025 2026`
- `LPR 下调 房贷`
- `首套房利率 二套房利率`

## Baidu Search Optimization

### Query Patterns for Fiscal Data
```
# Annual data
"[年份]年 全国 土地出让金 收入 数据"

# YoY comparison
"[城市] 土地出让金 同比 下降 万亿"

# Policy analysis
"[政策关键词] 房地产 市场 信号 分析"

# Expert commentary
"[专家名] 土地财政 报告 分析"
```

### Extracting Data from Search Snippets
Baidu search results often contain key data in the snippet without needing to click through:
- Look for `<emphasis>` tags in the snapshot — these highlight key terms/numbers
- Numbers with 万亿/亿/百分比 are usually the core data points
- Source labels ("第一财经"、"财政部") indicate credibility
- Dates in snippets help verify data currency

## Common Data Patterns

### Land Revenue Trend (2021-2025)
```
2021: ~8.71万亿 (peak)
2022: ~6.69万亿 (-23.3%)
2023: ~5.80万亿 (-13.2%)
2024: ~4.87万亿 (-16.0%)
2025: ~4.15万亿 (estimated, -15%)
```

### Guangzhou Land Revenue
```
2024: 772.74亿 (-34.65%)
2025: 506.6亿 (-34.4%, 20-year low)
```

### Key Policy Timeline
```
2024-09-26: 中央政治局会议 "止跌回稳"
2024-10-17: 住建部+四部门 "组合拳"
2024: 广州全面取消"三限"
2025: 中央经济工作会议 "防范系统性风险"
2026: 房贷利率降至 2.76% 历史低位
```

## Chinese News Search Engine Hierarchy for Policy Research

### Reliability Ranking (实测 2026-08-11)

| Engine | URL | Reliability | CAPTCHA | Best For |
|--------|-----|-------------|---------|----------|
| **Sina News Search** | search.sina.com.cn | ⭐⭐⭐⭐⭐ | Never blocked | Chinese news/policy articles |
| **Baidu (first hit)** | baidu.com | ⭐⭐⭐⭐ | After 1st search | AI summary + aggregated data |
| **360 Search** | so.com | ⭐⭐⭐ | Rarely | General Chinese queries |
| **Sogou** | sogou.com | ⭐⭐ | Anti-spider | WeChat articles only |
| **Bing CN** | bing.com | ⭐ | Encoding issues | Irrelevant for Chinese |
| **DuckDuckGo** | duckduckgo.com | ⭐ | No Chinese results | English queries only |
| **Google** | google.com | ❌ | Always blocked | Not usable from Chinese IP |

### Sina News Search — Recommended for Policy Research

**Why it's best**: Never triggered CAPTCHA during extended research sessions. Returns clean news results with source attribution, dates, and snippets. Supports time-sorted results.

**Search templates**:
```
# Policy research
browser_navigate(url="https://search.sina.com.cn/search?q=广州+收购商品房+安置房+资金+2024&tp=news&range=all&sort=time")

# Fiscal data
browser_navigate(url="https://search.sina.com.cn/search?q=财政部+土地出让金+2024+同比+数据&tp=news&range=all&sort=time")

# Housing policy
browser_navigate(url="https://search.sina.com.cn/search?q=保障性住房+再贷款+使用率+收储&tp=news&range=all&sort=time")
```

**Result features**:
- Source labels (羊城派, 21世纪经济报道, 财联社, etc.)
- Publication dates
- Snippet with key data points
- Pagination (50 pages deep)
- Time-sorted option (sort=time)

### Baidu AI Summary — Best for Aggregated Data

**Key insight**: Baidu's AI summary on the first search provides excellent aggregated data across multiple sources, often containing the exact numbers you need. After the first search, CAPTCHA kicks in.

**Strategy**: Make the first Baidu search count — use a precise query that targets the specific data point you need. The AI summary often contains:
- Specific fund amounts
- Utilization rates
- Unit counts
- Policy timelines
- Cross-source data compilation

**Example**: Searching `广州 收购商品房 安置房 资金使用率 2024 2025` on Baidu returned an AI summary with exact figures: 40.53亿元 total, 24.06亿元 used, 59.4% utilization, 1377 units purchased, 14.43亿元 spent.

### Search Strategy for Chinese Policy Research

1. **First**: Try Sina News search (search.sina.com.cn) with time-sorted results
2. **Second**: If Sina doesn't have enough data, try Baidu (one shot, make it count)
3. **Third**: Try 360 search (so.com) for general context
4. **Never waste time on**: Google, DuckDuckGo, Bing CN for Chinese content

## Pitfalls

1. **MOF article URLs are fragile** — don't construct URLs manually; use search results
2. **Government sites are JS-heavy** — use browser, not curl
3. **Different metrics for same concept** — "土地出让金" vs "国有土地使用权出让收入" vs "出让成交价款" may differ slightly in scope
4. **Year-end vs cumulative data** — be careful whether data is full-year or partial-year
5. **Central vs local budgets** — distinguish between 中央预算 and 地方预算
6. **一般公共预算 vs 政府性基金** — land revenue is in 政府性基金, not 一般公共预算
7. **Sina News search pagination** — results go 50 pages deep; use time-sorted for recency
8. **Baidu AI summary is one-shot** — plan your query carefully before the first search
