---
name: acgnx-se
description: "AcgnX末日動漫資源庫 (share.acgnx.se) 搜索爬取：RSS Feed获取最新动漫BT种子/磁力链接。触发词：acgnx, 动漫资源, anime torrent, 动漫下载"
version: "1.0.0"
author: hermes-agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [scraping, anime, torrent, acgnx]
  requires:
    bins: [curl, python3]
---

# AcgnX末日動漫資源庫 爬取技能

搜索和获取 share.acgnx.se 上的动漫BT种子/磁力链接资源。

## 站点信息

- **站点**: https://share.acgnx.se
- **类型**: ACG (Anime, Comic, Game) 资源分享站
- **语言**: 中文
- **反爬虫**: Cloudflare Turnstile (Managed Challenge)

## ⚠️ 反爬虫现状

| 方面 | 状态 |
|:---|:---|
| RSS Feed | ✅ 可访问，无需绕过 |
| 资源详情页 | ❌ Cloudflare拦截 |
| 下载链接 | ❌ 需访问详情页 |

**结论**: RSS Feed 是唯一可靠的数据源，可获取最新50条资源列表。

## 🔧 使用方法

### 1. 获取最新资源列表 (RSS Feed)

```bash
curl -s https://share.acgnx.se/rss.xml
```

### 2. 解析RSS获取结构化数据

```python
import requests
import xml.etree.ElementTree as ET

resp = requests.get('https://share.acgnx.se/rss.xml', timeout=15)
root = ET.fromstring(resp.content)

items = []
for item in root.findall('.//item'):
    title = item.find('title').text or ''
    link = item.find('link').text or ''
    pub_date = item.find('pubDate').text or ''
    desc = item.find('description').text or ''
    items.append({
        'title': title,
        'url': link,
        'date': pub_date,
        'description': desc[:200]
    })

for i, item in enumerate(items[:10], 1):
    print(f"[{i}] {item['date'][:16]}")
    print(f"    📌 {item['title']}")
    print(f"    🔗 {item['url']}")
    print()
```

### 3. 搜索特定关键词

RSS Feed 本身不支持搜索。如果需要搜索，需要用浏览器绕过 Cloudflare：

```python
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

CHROME = '/opt/data/home/.agent-browser/browsers/chrome-150.0.7871.115/chrome'

async def search_acgnx(keyword):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            executable_path=CHROME,
            args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
        )
        page = await context.new_page()
        s = Stealth()
        await s.apply_stealth_async(page)
        
        # 搜索URL
        url = f'https://share.acgnx.se/search?keyword={keyword}'
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(10)  # 等待Cloudflare验证
        
        content = await page.inner_text('body')
        await browser.close()
        return content
```

**⚠️ Pitfall**: 浏览器方式不稳定，Cloudflare可能仍会拦截。优先使用RSS Feed。

### 4. 获取磁力链接

RSS Feed 中的链接指向资源详情页，详情页被 Cloudflare 拦截。

**Workaround**: 从 RSS 描述中提取磁力链接（如果有的话）：

```python
import re

# 从描述中提取磁力链接
magnet_pattern = r'magnet:\?xt=urn:btih:[a-zA-Z0-9]+'
magnets = re.findall(magnet_pattern, description)
```

## 📁 资源类型

AcgnX 主要提供：
- 动漫 BT 种子/磁力链接
- 中英双语字幕资源
- 多版本（BD/MKV/WEB-DL）

## ⚠️ 注意事项

1. **请求频率**: RSS Feed 可每5-10分钟请求一次
2. **不要频繁访问详情页**: 会触发 Cloudflare 更严格验证
3. **Cookie**: Cloudflare 管理，无需手动处理
4. **下载链接**: 需要访问详情页才能获取，目前无法自动化

## 🔗 相关技能

- `anti-bot-web-scraping` — 反爬虫绕过通用方案
- `cloudflare-turnstile` — Cloudflare验证码绕过
- `bt1lou-search` — BT之家搜索（更完整的BT资源站）
