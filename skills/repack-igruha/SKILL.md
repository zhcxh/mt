---
name: repack-igruha
description: "Repack-igruha (Торрент-Игруха) 俄语游戏Repack站爬取：Playwright+Stealth绕过DDoS-Guard，搜索下载PC游戏BT种子/磁力链接。触发词：igruha, 游戏下载, game torrent, repack, 俄语游戏"
version: "1.0.0"
author: hermes-agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [scraping, games, torrent, igruha, ddos-guard]
  requires:
    bins: [python3]
    python_packages: [playwright, playwright-stealth]
---

# Repack-igruha (Торрент-Игруха) 爬取技能

搜索和获取 repack-igruha.net 上的PC游戏BT种子/磁力链接资源。

## 站点信息

- **站点**: https://repack-igruha.net
- **类型**: 俄语游戏资源分享站 (PC游戏Repack)
- **语言**: 俄语
- **反爬虫**: DDoS-Guard (JS Challenge + CAPTCHA)

## ⚠️ 反爬虫现状

| 方面 | 状态 |
|:---|:---|
| 所有页面 | DDoS-Guard保护 |
| 绕过方案 | Playwright + Stealth ✅ 有效 |
| curl_cffi | ❌ 无效 (TLS伪装被拦截) |
| nodriver | ❌ 浏览器连接问题 |

**结论**: Playwright + Stealth 是唯一有效的绕过方案。

## 🔧 使用方法

### 1. 安装依赖

**⚠️ Pitfall: `pmi_env` 没有 pip，用 `anti_bot_env`（已有 playwright + playwright-stealth）：**

```bash
source /opt/data/anti_bot_env/bin/activate
python3 -c "from playwright_stealth import Stealth; print('OK')"
```

### 2. 基础爬取脚本

```python
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

CHROME = '/opt/data/home/.agent-browser/browsers/chrome-150.0.7871.115/chrome'

async def scrape_igruha(url='https://repack-igruha.net/'):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            executable_path=CHROME,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
            ]
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='ru-RU',
        )
        
        page = await context.new_page()
        s = Stealth()
        await s.apply_stealth_async(page)
        
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(10)  # 等待DDoS-Guard验证
        
        title = await page.title()
        if 'DDoS-Guard' in title:
            print("❌ DDoS-Guard验证失败")
            await browser.close()
            return None
        
        content = await page.inner_text('body')
        links = await page.eval_on_selector_all('a', 'els => els.map(e => ({text: e.textContent.trim(), href: e.href}))')
        
        await browser.close()
        return {'title': title, 'content': content, 'links': links}

# 运行
result = asyncio.run(scrape_igruha())
if result:
    print(f"标题: {result['title']}")
    print(f"内容长度: {len(result['content'])} 字符")
    print(f"链接数量: {len(result['links'])}")
```

### 3. 搜索游戏

**⚠️ Pitfall: 搜索URL不是 `?s=keyword`，正确格式是：**

```
https://repack-igruha.net/index.php?do=search&subaction=search&story=关键词
```

用 `?s=` 会返回首页而非搜索结果。**用英文名搜索效果更好。**

```python
async def search_game(keyword):
    """搜索游戏（英文名效果更好）"""
    url = f'https://repack-igruha.net/index.php?do=search&subaction=search&story={keyword}'
    return await scrape_igruha(url)

# 搜索示例 — 用英文名
result = asyncio.run(search_game('Stellaris'))   # ✅ 群星
result = asyncio.run(search_game('Cyberpunk'))   # ✅ 赛博朋克
result = asyncio.run(search_game('GTA'))         # ✅ GTA
```

**⚠️ Pitfall: 搜索结果中游戏名在 `<img>` 标签内，需用 `href` 匹配：**

```python
links = await page.eval_on_selector_all('a', '''
    els => els.map(e => ({
        text: e.textContent.trim().substring(0, 120), 
        href: e.href
    })).filter(l => l.text.length > 10 && l.href.includes('repack'))
''')
```

### 4. 获取游戏详情

```python
async def get_game_detail(game_url):
    """获取游戏详情页"""
    return await scrape_igruha(game_url)

# 从搜索结果中获取详情
for link in result['links']:
    if 'repack' in link['href'].lower():
        detail = asyncio.run(get_game_detail(link['href']))
        print(detail['content'][:500])
        break
```

### 5. 下载种子

**⚠️ Pitfall: 详情页没有磁力链接，只有下载按钮：**

```
https://repack-igruha.net/index.php?do=download&id=XXXXX
```

下载链接在页面中以 `Скачать торрент`（下载种子）按钮形式出现。

```python
# 提取下载链接
download_links = await page.eval_on_selector_all('a', '''
    els => els.map(e => ({
        text: e.textContent.trim(), 
        href: e.href
    })).filter(l => l.href.includes('download'))
''')

for link in download_links:
    print(f"📥 {link['text']}")
    print(f"   🔗 {link['href']}")
```

## 📁 资源类型

Repack-igruha 主要提供：
- PC游戏 Repack（压缩版）
- BT种子/磁力链接
- 多语言版本（含俄语）
- 游戏封面/截图

## ⚠️ 注意事项

1. **请求频率**: 每次请求间隔 5-10 秒
2. **Cookie**: DDoS-Guard 会设置7个cookie，有效期有限
3. **User-Agent**: 必须使用真实 Chrome UA
4. **locale**: 设置为 `ru-RU` 匹配站点语言
5. **等待时间**: 页面加载后需等待 10 秒让 DDoS-Guard 验证完成

## 🔗 相关技能

- `anti-bot-web-scraping` — 反爬虫绕过通用方案
- `cloudflare-turnstile` — Cloudflare验证码绕过
- `bt1lou-search` — BT之家搜索（中文影视资源）
- `acgnx-se` — AcgnX动漫资源站
