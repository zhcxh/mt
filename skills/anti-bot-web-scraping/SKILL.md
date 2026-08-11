---
name: anti-bot-web-scraping
description: >
  反爬虫绕过和网页抓取技能集。使用此技能绕过Cloudflare Turnstile、bot检测、
  CAPTCHA验证码等反爬虫保护，进行合法的数据采集和网页自动化。
  触发词：爬虫、scraping、反爬虫、cloudflare、captcha、验证码绕过、bot检测
tags: [scraping, anti-bot, cloudflare, captcha, stealth, automation]
version: 1.11.0
---

# 反爬虫绕过与网页抓取技能

## 功能概述

提供多种绕过网站反爬虫保护的方法，包括Cloudflare Turnstile、bot检测、CAPTCHA验证码等。

## 🎯 适用场景

- 网站显示"Checking your browser before accessing..."
- 需要通过Cloudflare Turnstile验证
- 遇到Cloudflare JS Challenge
- 网站有bot检测（如reCAPTCHA、hCaptcha）
- 需要绕过反爬虫保护进行数据采集
- 需要自动化登录、签到等操作

## 📦 推荐工具组合

| 工具 | 用途 | Cloudflare | DDoS-Guard | 推荐度 |
|------|------|-----------|-----------|--------|
| **Solverr** | Docker一键部署，双引擎自动切换 | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| **Camoufox** | 反检测Firefox，编译级指纹修改 | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| **Playwright + Stealth** | 浏览器自动化 + 反检测插件 | ❌ | ✅ **有效** | ⭐⭐⭐⭐ |
| **cloudflare-bypass-2026** | 5种绕过方案集合 | ✅ | ❓ | ⭐⭐⭐⭐ |
| **Turnstile-Solver** | 本地API解算器 | ✅ | ❓ | ⭐⭐⭐⭐ |
| **scrapling** | 高性能爬取，内置Cloudflare绕过 | ❌ | ❌ | ⭐⭐⭐ |
| **curl_cffi** | 轻量级，TLS指纹伪装 | ❌ | ❌ | ⭐ |
| **puppeteer-extra-stealth** | Node.js浏览器自动化 | ❌ | ❌ | ⭐⭐ |

> ⚠️ **实测结论 (2026-08-09)**: curl_cffi 的 TLS 伪装对 Cloudflare/DDoS-Guard 均无效。Solverr 是目前最全面的解决方案。

## 🚀 快速开始

### 激活环境

```bash
cd /opt/data && source anti_bot_env/bin/activate
```

### 测试安装

```bash
# 测试scrapling
python -c "from scrapling.fetchers import Fetcher; print('✅ Scrapling OK')"

# 测试curl_cffi
python -c "from curl_cffi import requests; print('✅ curl_cffi OK')"

# 测试SeleniumBase
python -c "from seleniumbase import SB; print('✅ SeleniumBase OK')"
```

## 📋 工具详解

### 方案0: Solverr（推荐 ⭐⭐⭐⭐⭐）— 最全面的解决方案

**GitHub**: https://github.com/unseensnick/Solverr
**特点**: 整合 FlareSolverr (Chrome引擎) + Byparr (Camoufox隐身引擎)，**同时支持 Cloudflare + DDoS-Guard**

```bash
# Docker一键部署
git clone https://github.com/unseensnick/Solverr.git
cd Solverr
docker compose up -d

# 或直接运行
docker run -d -p 8191:8191 --shm-size=512m ghcr.io/unseensnick/solverr:latest
```

**使用方式** (兼容 FlareSolverr API):
```bash
# 绕过 Cloudflare
curl -sX POST 'http://localhost:8191/v1' \
  -H 'Content-Type: application/json' \
  --data '{"cmd":"request.get","url":"https://share.acgnx.se/","maxTimeout":60000}'

# 绕过 DDoS-Guard
curl -sX POST 'http://localhost:8191/v1' \
  -H 'Content-Type: application/json' \
  --data '{"cmd":"request.get","url":"https://repack-igruha.net/","maxTimeout":60000}'
```

**工作原理**:
1. Chrome引擎 (默认) → Selenium + undetected-chromedriver
2. 失败自动切换 → Camoufox点击解决
3. 可选 → 付费CAPTCHA API
4. 保持session温暖，重复请求跳过挑战

> ⚠️ **Docker部署注意**: Solverr镜像约2.3GB，拉取时间较长。在fnOS等NAS上部署时，Docker操作可能超时。建议：
> 1. 先测试小镜像确认Docker正常工作
> 2. 使用 `docker pull` 预拉取镜像
> 3. 如果Docker不可用，考虑本地部署（需要Xvfb + Chrome）

### 方案0b: Camoufox — 反检测浏览器

**GitHub**: https://github.com/daijro/camoufox
**网站**: https://camoufox.com

```bash
pip install camoufox
python -m camoufox fetch
```

**特点**:
- 基于Firefox，在编译级别修改指纹
- 专为爬虫和AI代理设计
- 被Solverr、Byparr等项目采用
- 比Chromium更难被检测

> ⚠️ **实测注意**: Camoufox 单独使用无法绕过 Cloudflare/DDoS-Guard。它需要配合 playwright-captcha 等工具使用（如 Solverr 的 Stealth 引擎）。单独使用时仍会遇到验证页面。

### 方案0c: cloudflare-bypass-2026 — 5种绕过方案

**GitHub**: https://github.com/1837620622/cloudflare-bypass-2026 (413 stars)

| 方案 | 脚本 | 策略 | Turnstile | 适用场景 |
|------|------|------|-----------|---------|
| 1 | `bypass.py` | SeleniumBase UC Mode | ✅ | 默认主路径 |
| 2 | `simple_bypass.py` | UC + 代理轮换 | ✅ | 批量任务 |
| 3 | `bypass_nodriver.py` | nodriver CDP | ✅ | 无chromedriver |
| 4 | `bypass_curl_cffi.py` | TLS指纹/Cookie复用 | ❌ | 仅旧版Challenge |
| 5 | `bypass_cdp.py` | SeleniumBase CDP Mode | ✅ | UC后继路径 |

**关键结论**: curl_cffi 无法通过 Turnstile — 无JS运行时、无DOM、无交互能力、TLS只是信号之一。

### 方案0d: Turnstile-Solver-NEW — API解算器

**GitHub**: https://github.com/D3-vin/Turnstile-Solver-NEW (296 stars)

```bash
git clone https://github.com/D3-vin/Turnstile-Solver-NEW.git
cd Turnstile-Solver-NEW
pip install -r requirements.txt
python api.py  # 服务启动在 http://0.0.0.0:5072
```

**使用**:
```bash
# 解算Turnstile
curl "http://localhost:5072/turnstile?url=https://example.com&sitekey=0x4AAAAAAA"

# 获取cf_clearance (IUAM模式)
curl "http://localhost:5072/cf_clearance?url=https://example.com"
```

### 方案1: scrapling（推荐 ⭐⭐⭐⭐⭐）

**优点**: 内置Cloudflare Turnstile绕过，智能元素重定位

```python
from scrapling.fetchers import Fetcher, StealthyFetcher

# 简单请求
page = Fetcher.get('https://example.com', impersonate='chrome')

# 隐身请求（绕过Cloudflare）
page = StealthyFetcher.fetch(
    'https://protected-site.com',
    headless=True,
    solve_cloudflare=True,  # 自动解决Cloudflare Turnstile
    block_images=True,      # 加速加载
)

# CSS选择器
titles = page.css('h2.product-title::text').getall()

# XPath
links = page.xpath('//a[@class="item"]/@href').getall()

# 文本搜索
el = page.find_by_text('Add to Cart', tag='button')

# 导出
page.css('.product').to_json('products.json')
```

**Fetcher选择指南**:

| 目标网站 | Fetcher | 原因 |
|----------|---------|------|
| 静态HTML、简单API | `Fetcher` | 最快，TLS指纹伪装 |
| Cloudflare/反爬虫 | `StealthyFetcher` | 无头浏览器，绕过JS挑战 |
| 重度JS、SPA、登录 | `DynamicFetcher` | 完整Playwright/Chrome控制 |
| 多页爬取 | `Spider` 类 | 并发，支持暂停/恢复 |

### 方案2: playwright-bot-bypass（推荐 ⭐⭐⭐⭐⭐）

**优点**: 浏览器自动化，绕过bot检测

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent="Mozilla/5.0 ...",
        viewport={"width": 1920, "height": 1080}
    )
    page = context.new_page()
    
    # 注入反检测脚本
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        delete navigator.__proto__.webdriver;
    """)
    
    page.goto('https://example.com')
    # 页面已绕过bot检测
```

### 方案3: cloudflare-turnstile（推荐 ⭐⭐⭐⭐⭐）

**优点**: Cloudflare Turnstile专用绕过

```python
from seleniumbase import SB

# SeleniumBase方案（推荐）
with SB(uc=True) as sb:
    sb.uc_open_with_reconnect("https://example.com")
    sb.sleep(3)
    html = sb.get_page_source()

# curl_cffi方案（轻量级）
from curl_cffi import requests
response = requests.get(
    "https://example.com",
    impersonate="chrome"
)

# nodriver方案（无驱动）
import nodriver as uc
async def main():
    browser = await uc.start()
    page = await browser.get("https://example.com")
```

### 方案4: curl_cffi（轻量级 ⭐⭐⭐⭐）

**优点**: 无需浏览器，TLS指纹伪装

```python
from curl_cffi import requests

# 使用浏览器TLS指纹
response = requests.get(
    "https://example.com",
    impersonate="chrome"  # 伪装成Chrome
)

# 使用代理
proxies = {
    "http": "http://proxy:port",
    "https": "http://proxy:port"
}
response = requests.get(
    "https://example.com",
    impersonate="chrome",
    proxies=proxies
)
```

## 🔧 故障排除

| 问题 | 解决方案 |
|------|----------|
| `ModuleNotFoundError` | 激活虚拟环境: `source anti_bot_env/bin/activate` |
| `TimeoutError` | 增加超时时间，检查网络连接 |
| `验证码未解决` | 尝试其他绕过方案 |
| `代理连接失败` | 检查代理配置 |
| `Chrome版本过低` | 更新Chrome到最新版本 |

## 📊 方案对比 (实测 2026-08-09)

| 方案 | Cloudflare | DDoS-Guard | 速度 | 资源占用 | 推荐度 |
|------|-----------|-----------|------|---------|--------|
| **Solverr (Docker)** | ✅ | ✅ | 中 | 高 | ⭐⭐⭐⭐⭐ |
| **Camoufox** | ✅ | ✅ | 中 | 中 | ⭐⭐⭐⭐⭐ |
| **Playwright + Stealth** | ❌ | ✅ | 中 | 高 | ⭐⭐⭐⭐ |
| **cloudflare-bypass-2026** | ✅ | ❓ | 中 | 高 | ⭐⭐⭐⭐ |
| **Turnstile-Solver** | ✅ | ❓ | 快 | 中 | ⭐⭐⭐⭐ |
| curl_cffi (TLS伪装) | ❌ | ❌ | 快 | 低 | ⭐ |
| puppeteer-extra-stealth | ❌ | ❌ | 中 | 高 | ⭐⭐ |
| scrapling Fetcher | ❌ | ❌ | 快 | 低 | ⭐⭐ |
| RSS Feed | ✅ (列表) | ❌ | 快 | 低 | ⭐⭐⭐ |

> ⚠️ **关键发现**: curl_cffi 的 TLS 伪装看似轻量高效，但对 Cloudflare/DDoS-Guard 完全无效。Solverr 是最全面的解决方案。

## 🎯 最佳实践 (实测验证)

1. **首选 Solverr**: Docker一键部署，同时支持 Cloudflare + DDoS-Guard，自动故障转移
2. **DDoS-Guard → Playwright + Stealth**: 如不部署Solverr，这是唯一有效的轻量方案
3. **Cloudflare → RSS Feed**: 唯一可用数据源，资源详情页仍被拦截
4. **不要用 curl_cffi**: TLS伪装对 Cloudflare/DDoS-Guard 完全无效，浪费时间
5. **先探测再绕过**: 用 `curl -sI <url>` 检查响应头，快速识别反爬虫系统类型
6. **控制请求频率**: 即使绕过成功，也要添加延迟避免触发更严格验证
7. **寻找替代数据源**: RSS Feed、API端点、sitemap.xml 可能绕过前端保护

## ⚠️ 注意事项

1. **合法使用**: 仅用于合法的数据采集和测试
2. **尊重robots.txt**: 遵守网站的爬虫协议
3. **控制频率**: 避免对目标网站造成压力
4. **IP轮换**: 使用代理池避免IP被封
5. **错误处理**: 做好异常处理和重试机制

## 🔍 Solverr 实测结果 (2026-08-09)

**部署**: fnOS Docker (192.168.31.118:8191)

| 站点 | 结果 | 说明 |
|------|------|------|
| httpbin.org | ✅ 成功 | 无挑战 |
| nowsecure.nl | ✅ 成功 | 179KB HTML，基础 Cloudflare |
| share.acgnx.se | ⚠️ 超时 | Cloudflare Turnstile 太强 |
| repack-igruha.net | ⚠️ 超时 | DDoS-Guard CAPTCHA 太强 |

**结论**: Solverr 可以绕过**基础 Cloudflare**，但对强防护站点（Turnstile + CAPTCHA）超时。

**替代方案**:
- **FlareSolverr** (`flaresolverr/flaresolverr:latest`): 更小镜像 (~800MB)，单引擎，相同 API
- **Playwright + Stealth**: 绕过 DDoS-Guard 有效
- **RSS Feed**: 绕过 Cloudflare 获取列表

## ✅ Sina News Search — Most Reliable Chinese News Search (2026-08-11 实测)

**关键发现**: search.sina.com.cn 在长时间研究会话中**从未触发CAPTCHA**，是中文新闻/政策研究的最可靠搜索引擎。

**优势**:
- 无CAPTCHA限制
- 支持时间排序 (sort=time)
- 50页深度分页
- 结果包含来源标注（羊城派、财联社、21世纪经济报道等）
- 摘要包含关键数据点

**使用方法**:
```
browser_navigate(url="https://search.sina.com.cn/search?q=查询内容&tp=news&range=all&sort=time")
```

**最佳策略**: 中文政策研究时，先用Sina News搜索获取最新新闻文章，再用Baidu搜索获取AI摘要聚合数据（仅一次机会）。

> 📄 详细指南: `references/chinese-fiscal-data-research.md` 中的 "Chinese News Search Engine Hierarchy" 部分

## 📁 文件位置

### 技能文件
- **scrapling**: `/opt/data/skills/scrapling/`
- **playwright-bot-bypass**: `/opt/data/skills/playwright-bot-bypass/`
- **cloudflare-turnstile**: `/opt/data/skills/cloudflare-turnstile/`

### 虚拟环境
- **anti_bot_env**: `/opt/data/anti_bot_env/`

### 已安装工具
- **Camoufox**: `/opt/data/home/.cache/camoufox/browsers/official/152.0.4-beta.28-924f3109`
- **cloudflare-bypass-2026**: `/opt/data/cloudflare-bypass-2026/`

## ⚠️ 已知无法绕过的防护系统

### Cloudflare Turnstile (share.acgnx.se 实测)
Cloudflare Managed Challenge 是目前最难绕过的反爬虫系统之一。

**实测结果**: 所有方法均失败
| 方法 | 结果 | 原因 |
|------|------|------|
| Playwright + Stealth | ❌ 403 | Turnstile自动验证失败 |
| curl_cffi (23种TLS伪装) | ❌ 403 | JS Challenge需要真实浏览器环境 |
| puppeteer-extra-stealth | ❌ 403 | 同上 |
| scrapling StealthyFetcher | ❌ 403 | 缺少patchright模块 |

**唯一绕过方案**: RSS Feed
```bash
# 测试RSS Feed是否可访问
curl -s https://share.acgnx.se/rss.xml | head -20
# Status: 200, 50条资源, 50KB
```

### DDoS-Guard (repack-igruha.net 实测)
DDoS-Guard **可以** 通过 Playwright + Stealth 绕过！

**✅ 有效方案: Playwright + Stealth**
```python
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

CHROME = '/opt/data/home/.agent-browser/browsers/chrome-150.0.7871.115/chrome'

async def scrape_ddos_guard(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            executable_path=CHROME,
            args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
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
        if 'DDoS-Guard' not in title:
            content = await page.inner_text('body')
            return content
        return None
```

**❌ 无效方案**:
| 方法 | 结果 | 原因 |
|------|------|------|
| curl_cffi (所有TLS伪装) | ❌ 403 | JS Challenge + CAPTCHA |
| Camoufox (单独使用) | ❌ CAPTCHA页面 | 需要配合playwright-captcha |
| puppeteer-extra-stealth | ❌ CAPTCHA页面 | 显示"Sorry, we could not verify" |
| scrapling Fetcher | ❌ 403 | 无法执行JS |

> ⚠️ **playwright-stealth API**: 使用 `Stealth` 类的 `apply_stealth_async(page)` 方法，不是 `stealth_async(page)`。导入方式: `from playwright_stealth import Stealth`

**DDoS-Guard 技术细节**:
- Cookie: 7个 `__ddg*` cookies (会话、IP、时间戳、验证状态)
- JS Challenge: `view.js` (61KB混淆) + `index.js` (191KB webpack)
- CAPTCHA: 图片选择验证 (如 "选择所有人行横道")
- 全站保护: 所有路径返回403，无API后门或RSS Feed

### Cloudflare Managed Challenge (share.acgnx.se 实测)

**挑战机制**:
- 页面标题: "Just a moment..."
- 挑战类型: Cloudflare Turnstile (Managed Challenge)
- JS加载: `/cdn-cgi/challenge-platform/h/b/orchestrate/chl_page/v1`
- CSP Nonce: 每次请求生成唯一nonce

**TLS指纹测试**: 所有impersonation (chrome/safari/firefox) 都返回403，Cloudflare不依赖TLS指纹。

**关键发现: RSS Feed绕过**:
```
URL: https://share.acgnx.se/rss.xml
Status: 200 ✅
Size: 50,435 bytes
Items: 50条资源 (标题、链接、发布时间)
```
- RSS Feed可绕过Cloudflare获取资源列表
- 但资源详情页 (show-*.html) 仍被Cloudflare拦截
- 无法通过RSS获取下载链接 (magnet/torrent)

**404页面信息泄露**: 非保护路径返回404但暴露技术栈:
- jQuery
- Meta tags (keywords: BT,動畫,漫畫,遊戲)
- Telegram频道链接

## ⚠️ 常见陷阱

### CSS选择器失效时的DOM文本提取
当网站使用动态class名或CSS选择器返回空结果时，可以遍历所有DOM元素，按文本内容筛选：
```javascript
const els = document.querySelectorAll('*');
const data = [];
els.forEach(el => {
  const text = el.textContent;
  if (text && text.includes('关键标记') && text.length < 300) {
    data.push(text.trim());
  }
});
const unique = [...new Set(data)];
// 然后用正则解析结构化数据
```
**适用场景**: 房天下等使用动态class名的中国网站，价格/面积等数据嵌在文本中而非独立元素。

### SPA 网站（React/Vue/Angular + 搜索API）
许多企业网站（如 PMI.org）是 SPA：HTML shell 可以通过 curl_cffi 获取（200状态），
但实际数据通过客户端 JS 调用搜索 API（如 Coveo/Algolia/ElasticSearch）加载。
**特征**：HTML 返回200但内容只有空容器 `<div id="root"></div>`，
搜索 token 在 SSR HTML 中被截断（如 `eyJhbG...cekU`），无法直接使用。

**解决方法**：
1. 首选：headed 浏览器 + 真实 display（Xvfb）
2. 次选：SeleniumBase `uc=True`（undetected-chromedriver）
3. 不要浪费时间在 headless Playwright 上——Cloudflare JS Challenge 无法绕过

### 远程桌面/iframe 内的浏览器
fnOS fygo-browser 等远程浏览器运行在 iframe 内，虽然能加载受保护页面，
但外层工具无法操作 iframe 内的 DOM。仅适用于手动验证/截图，不适用于自动化抓取。

### TLS指纹伪装的局限性 (实测验证)
curl_cffi 的 `impersonate` 参数可以伪装TLS指纹，但**对 Cloudflare/DDoS-Guard 完全无效**。

**实测数据 (2026-08-09)**:
- 测试了 23 种 TLS impersonation (chrome99-chrome131, safari15-17, firefox, edge)
- 所有 impersonation 对 share.acgnx.se (Cloudflare) 返回 403
- 所有 impersonation 对 repack-igruha.net (DDoS-Guard) 返回 403

**原因**: 这些系统不仅检查TLS指纹，还检查:
- JavaScript执行环境 (需要真实浏览器)
- 浏览器API完整性 (navigator, webdriver等)
- Canvas/WebGL指纹
- 行为分析 (鼠标移动、点击模式)

**结论**: TLS指纹伪装只能绕过简单的bot检测，对于 Cloudflare/DDoS-Guard 无效。不要浪费时间尝试。

### RSS Feed绕过技巧
某些Cloudflare保护的网站（如 share.acgnx.se）的RSS Feed可能绕过前端保护:
```bash
# 测试RSS Feed是否可访问
curl -s https://example.com/rss.xml | head -20
curl -s https://example.com/feed | head -20
curl -s https://example.com/atom.xml | head -20
```

**适用场景**:
- 内容网站 (博客、新闻、资源站)
- 需要获取资源列表但不需要详情页
- RSS Feed通常不经过前端反爬虫系统

**限制**:
- RSS Feed可能不包含完整信息 (如下载链接)
- 资源详情页仍需绕过Cloudflare
- 不适用于所有网站

> 💡 **通用策略**: 在尝试绕过反爬虫之前，先探测替代数据源：RSS/Atom Feed、API端点、sitemap.xml、GraphQL endpoint。这些通常不经过前端保护层。

### 中国房产平台从云端IP完全不可访问 (2026-08-11 实测)
**问题**: 从云服务器IP (AWS/GCP/Azure等) 访问中国房产平台 (贝壳/链家/安居客/58/房天下) 及百度搜索，**全部被拦截**。
**测试结果**:
- ke.com/lianjia.com: "Forbidden" + 拦截 ID
- anjuke.com/58.com: CAPTCHA验证页面
- fang.com: 空响应/重定向
- 百度搜索: 连接关闭
- Bing CN: 返回无关结果（编码问题导致中文查询完全失效，显示无关英文结果）
- DuckDuckGo/Google: CAPTCHA
- CORS代理/Web Archive: 同样失败
**结论**: 从非中国IP无法获取中国房产数据。必须使用中国住宅IP/VPN，或让用户手动搜索后分享结果。
**不要浪费时间**尝试: CORS代理、Google Translate代理、Web Archive缓存。
**参考**: `references/chinese-platform-bot-detection.md` 有完整的失败记录。

### ✅ 百度搜索 — 中国境内IP的最佳中文搜索 (2026-08-11 实测)

**关键发现**: 百度搜索**从中国境内IP（住宅/企业）可以正常使用**，不需要特殊绕过。之前记录的"百度搜索被拦截"仅适用于**海外/云端IP**。

**实测环境**: Linux主机 (6.18.18.c938-trim)，中国境内IP

**使用方法**:
```
# 浏览器导航（推荐，完整渲染搜索结果）
browser_navigate(url="https://www.baidu.com/s?wd=搜索关键词")

# curl方式（可能被拦截，不如浏览器可靠）
curl -sL "https://www.baidu.com/s?wd=%E6%90%9C%E7%B4%A2%E5%85%B3%E9%94%AE%E8%AF%8D" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
```

**搜索结果特征**:
- 搜索结果摘要包含**大量有价值数据**（数字、同比变化、政策引用）
- 很多时候**不需要点击进入文章**，摘要本身就包含关键数据点
- "大家还在搜"相关搜索词精准
- 热搜榜提供实时话题参考
- 结果来源标注（"官方"、"权威媒体"等）

**数据提取技巧**:
- 搜索结果中的 `<emphasis>` 标签包裹的内容通常是关键数据
- 摘要中的百分比、万亿/亿等数字可以直接引用
- 来源标注（"第一财经"、"央广网"、"财政部"等）可用于验证可信度
- 多次搜索不同关键词组合可以覆盖不同维度的数据

**⚠️ 注意**: 如果从海外/云端IP访问百度，会返回CAPTCHA或空结果。此时应使用360搜索 (so.com) 作为替代。

### ✅ 中国 government fiscal data websites (2026-08-11 实测)

**关键发现**: 中国财政/住建部等政府网站的URL结构脆弱，经常返回404或空页面，且内容依赖JS渲染。

**已测试的网站**:
| 网站 | URL模式 | 问题 |
|------|---------|------|
| 财政部 (mof.gov.cn) | `/gkml/caizhengshuju/` | 列表页可访问，文章URL经常404 |
| 国务院 (gov.cn) | 各种 | 政策文件可访问 |
| 住建部 | 各种 | 政策解读可访问 |
| 自然资源部 | 各种 | 公报数据可访问 |

**绕过策略**:
1. **不要直接构造文章URL** — 通过搜索结果点击进入，而非手动拼接URL
2. **使用浏览器而非curl** — 政府网站常依赖JS渲染，curl获取的是空壳HTML
3. **利用Baidu搜索摘要** — 很多时候搜索摘要已包含政府文件的关键数据
4. **使用 `browser_console` 提取数据** — 对JS渲染的页面，用JS提取DOM内容

**典型工作流**:
```
1. Baidu搜索 "财政部 2024年 土地出让金 数据"
2. 从搜索摘要提取关键数字（如"48,699亿元，下降16%"）
3. 如需更多细节，点击搜索结果进入原文
4. 如果原文404，尝试搜索其他关键词组合获取相同数据
```

### ✅ 360搜索 (so.com) — 云端中文搜索的最佳替代方案 (2026-08-11 实测)
**关键发现**: 当百度、搜狗、必应(中文)均失败时，360搜索(so.com)是从云端IP搜索中文内容的**唯一可靠替代**。

**优势**:
- 不触发CAPTCHA（单次会话，3-5次搜索内）
- 支持中文查询，返回相关中文结果
- 有AI摘要功能（自动综合多个来源）
- 整合360百科词条内容
- 返回安居客、搜狐焦点等房产网站的摘要片段
- "为您推荐"相关搜索词精准（中文长尾词）

**⚠️ 重要发现 (2026-08-11)**: 360搜索在**同一会话中多次搜索后会触发CAPTCHA**。建议：
- 单次会话控制搜索次数（3-5次以内）
- 如果触发CAPTCHA，切换到百度搜索（中国境内IP可用）
- 使用不同关键词组合，避免重复搜索

**使用方法**:
```
# 浏览器导航（推荐，最可靠）
browser_navigate(url="https://www.so.com/s?q=查询内容")

# curl方式（可能偶尔空结果）
curl -sL "https://www.so.com/s?q=%E6%9F%A5%E8%AF%A2%E5%86%85%E5%AE%B9" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
```

**搜索结果特征**:
- AI摘要框：自动综合多个来源的回答
- 360百科词条：直接显示在搜索结果中
- "为您推荐"相关搜索词（精准的中文长尾词）
- 安居客/搜狐焦点/楼盘网等房产网站的摘要
- 360地图集成

**⚠️ 注意**: 360搜索的curl方式可能偶尔返回空结果，浏览器方式更可靠。

### ✅ 政府/政协提案数据库 — 被低估的权威信息源 (2026-08-11 实测)
**关键发现**: 广州市政协提案数据库 (www.gzzx.gov.cn) 提供了比任何房产平台都更精确的本地信息。

**实际案例**: 搜索"一品湖山 对口学校 地铁距离"时：
- 房产平台：给出模糊的"离地铁站较远"
- 政协提案：精确记载"距离最近的地铁站3号线北延线同和站3.4公里"、片区内7个住宅区名称、5所学校名称、约7万居民

**适用场景**:
- 查找精确的地铁/公交距离
- 了解片区内的学校、医院等公共设施
- 获取人口数据和区域规划信息
- 了解市政基础设施建设计划

**搜索方法**:
```
# 360搜索 + site:gov.cn
browser_navigate(url="https://www.so.com/s?q=查询内容+site:gov.cn")

# 直接访问政协提案
browser_navigate(url="https://www.gzzx.gov.cn")
# 导航到: 提案工作 → 提案公开 → 搜索
```

**其他政府信息源**:
- 区政府官网 (www.by.gov.cn 白云区)
- 市教育局 (www.gzeduc.gov.cn) — 学区划分
- 市住建局 — 房产政策
- 街道办事处官网 — 户口/社区信息

### 替代端点探测
在尝试绕过反爬虫之前，先探测替代端点:
```python
# 探测常见端点
endpoints = ['/api/', '/api/v1/', '/feed', '/rss', '/sitemap.xml', 
             '/.well-known/', '/login', '/search', '/wp-json']

for ep in endpoints:
    r = requests.get(f'https://{site}{ep}', impersonate='chrome', timeout=10)
    print(f'{ep}: {r.status_code}')
    time.sleep(2)  # 控制频率
```

**发现**:
- 有些端点可能返回200 (如RSS Feed)
- 有些端点返回404但暴露技术栈信息
- DDoS-Guard通常保护所有路径，Cloudflare可能只保护主页

## 📚 研究回退策略 (Research Fallback Strategies)

当中国网站和搜索引擎阻止自动访问时（尤其是从云端IP），使用以下回退策略：

**快速决策树**:
1. 尝试直接搜索（百度、谷歌、必应）→ 如果被阻止 →
2. 尝试直接访问网站（安居客、房天下等）→ 如果被阻止 →
3. 尝试Wikipedia API（获取地理/行政数据）→ 如果可用 → 用作基线数据
4. 尝试政府/官方来源 → 如果可用 → 用于政策/法规数据
5. 从训练知识编译 → 明确标记为"编译知识"而非"实时数据"

**关键策略**:
- **Wikipedia API**: 可靠获取中国区县、城市、行政区划数据
- **编译知识**: 用于政策框架、一般价格范围、基础设施信息
- **用户协助**: 当自动访问完全失败时，请用户手动搜索并分享结果

> 📄 详细指南: `references/research-fallback-strategies.md`

## 📁 参考文档

- **Chinese平台反爬虫检测**: `references/chinese-platform-bot-detection.md` - 中国平台(链家/贝壳/安居客)的bot检测模式及Baidu搜索替代方案
- **Chinese租金回报率计算**: `references/chinese-rental-yield-calculation.md` - 中国房产租金回报率计算方法、市场基准、Baidu搜索模式
- **Chinese fiscal data research**: `references/chinese-fiscal-data-research.md` - 中国财政/房地产数据研究方法论：数据源层级、搜索关键词模板、百度搜索优化、常见数据模式与陷阱
- **Chinese房产研究方法论**: `references/chinese-property-research.md` - 从云端IP研究中国房产的完整方法论，含360搜索、政府来源、数据清单
- **scrapling使用指南**: `references/scrapling-guide.md`
- **Cloudflare绕过方案**: `references/cloudflare-bypass.md`
- **反爬虫检测绕过**: `references/anti-detection.md`
- **PMI.org 抓取笔记**: `references/pmi-org-scraping.md`
- **ACGNX/IGRUHA分析**: `references/anti-crawler-analysis-acgnx-igruha.md`
- **DDoS-Guard绕过实测**: `references/ddos-guard-bypass-playwright-stealth.md` (2026-08-09 新增)
- **网络调研绕过方案**: `references/network-research-bypass-methods.md` (2026-08-09 新增)
- **研究回退策略**: `references/research-fallback-strategies.md` (2026-08-11 新增) - 当中国网站阻止访问时的回退策略，包括Wikipedia API、编译知识、用户协助等
- **fnOS Docker部署笔记**: `references/fnos-docker-deployment.md` (2026-08-09 新增)
- **安居客数据提取**: `references/anjuke-data-extraction.md` (2026-08-11 新增) - 安居客(Anjuke) DOM提取方法，strong标签价格提取、社区均价采集

## 更新日志

- **v1.12.0** (2026-08-11): 安居客数据提取方法文档
  - 🆕 `references/anjuke-data-extraction.md` — 安居客DOM提取方法，strong标签价格提取、社区均价采集、数据解析模式
  - 📝 记录安居客页面结构和URL模式
  - 📝 添加与其他中国房产平台的对比（安居客/房天下/链家/贝壳）
  - 📝 记录常见陷阱（动态class名、价格格式、分页、验证码）
- **v1.11.0** (2026-08-11): 360搜索CAPTCHA发现 + 望庐花园案例
  - 🆕 **360搜索CAPTCHA**: 发现360搜索在同一会话多次搜索后会触发CAPTCHA
  - 🆕 **望庐花园案例**: 添加配售型保障房研究案例（备案名vs推广名、学区特殊政策）
  - 🆕 **搜索引擎切换策略**: 完善360搜索→百度→新浪新闻的切换逻辑
  - 📝 更新 `references/chinese-property-research.md` 添加望庐花园完整研究流程
  - 📝 更新主SKILL.md中360搜索部分，添加CAPTCHA注意事项
- **v1.10.0** (2026-08-11): Sina News search as most reliable Chinese news engine
  - 🆕 **Sina News Search (search.sina.com.cn)**: Confirmed as most reliable Chinese news/policy search engine — never triggered CAPTCHA during extended research sessions
  - 🆕 **Chinese News Search Engine Hierarchy**: Added reliability ranking table (Sina > Baidu first-hit > 360 > Sogou > others)
  - 🆕 **Baidu AI Summary strategy**: Documented one-shot optimization — plan query carefully before first search
  - 📝 Updated `references/chinese-fiscal-data-research.md` with search engine hierarchy and Sina News templates
  - 📝 Added Sina News section to main SKILL.md
- **v1.9.0** (2026-08-11): Chinese fiscal data research + Baidu from Chinese IPs
  - 🆕 **百度搜索 from Chinese residential IPs**: Confirmed working without CAPTCHA from Chinese境内IP (contradicts earlier "Baidu blocks all cloud IPs" finding — distinction is IP location)
  - 🆕 **Chinese government fiscal data websites**: Documented MOF URL fragility and JS-heavy rendering issues; search-snippet extraction as primary strategy
  - 🆕 `references/chinese-fiscal-data-research.md` — Complete methodology for Chinese fiscal/property market data research: source hierarchy, search query templates, Baidu optimization, common data patterns and pitfalls
  - 📝 Updated main SKILL.md with Baidu from Chinese IPs section and government website section
- **v1.8.0** (2026-08-11): 360搜索替代方案 + 政府信息源
  - 🆕 **360搜索 (so.com)**: 云端中文搜索的最佳替代方案，不触发CAPTCHA
  - 🆕 **政府/政协提案数据库**: 被低估的权威信息源，提供比房产平台更精确的本地数据
  - 📝 更新中国平台IP封锁部分，增加Bing CN编码问题说明
  - 📝 添加360搜索使用方法和结果特征
  - 📝 添加政府信息源列表（政协、区府、教育局、住建局）
  - 📝 创建 `references/chinese-property-research.md` — 中国房产研究完整方法论
- **v1.7.0** (2026-08-11): Research fallback strategies documentation
  - 📝 添加 `references/research-fallback-strategies.md` - 当中国网站阻止访问时的回退策略
  - 📝 记录Wikipedia API作为可靠的地理/行政区划数据来源
  - 📝 添加编译知识使用指南（明确标记为非实时数据）
  - 📝 添加用户协助研究模板
  - 📝 添加房地产研究特定模式（政策研究、价格研究）
  - 📝 更新主SKILL.md，添加研究回退策略快速决策树
- **v1.6.0** (2026-08-11): Chinese platform cloud IP blocking documented
  - ⚠️ **关键发现**: 从云服务器IP访问中国房产平台(贝壳/链家/安居客/58/房天下)及百度搜索**全部被拦截**
  - 📝 添加 `references/chinese-platform-bot-detection.md` 中的IP位置依赖性说明
  - 📝 更新"Fallback Strategy"为按IP位置分策略(中国住宅IP vs 云端IP)
  - 📝 添加常见陷阱: 中国房产平台从云端IP完全不可访问
  - 📝 记录CORS代理、Web Archive、Google Translate代理均失败
  - 📝 明确建议: 不要浪费时间尝试这些无效方案
- **v1.5.2** (2026-08-11): Chinese rental yield calculation reference
  - 📝 添加 `references/chinese-rental-yield-calculation.md` - 中国房产租金回报率计算方法
  - 📝 记录4种计算方法 (成交价/挂牌价/单价/租售比)
  - 📝 添加中国市场基准数据 (一线城市1.7-2.0%, 二线2.0-2.5%)
  - 📝 添加Baidu搜索查询模式模板
  - 📝 添加分析模板和常见陷阱
- **v1.5.1** (2026-08-11): Fang.com extraction techniques
  - 📝 Updated `references/chinese-platform-bot-detection.md` with confirmed Fang.com regional URL structure
  - 📝 Added browser console JavaScript extraction technique for Fang.com price data
  - 📝 Added listing data text pattern regex for parsing
  - 📝 Added Baidu price trend data extraction pattern
  - 📝 Added Fang.com URL encoding pitfall
- **v1.5.0** (2026-08-11): 中国平台反爬虫检测文档
  - 📝 添加 `references/chinese-platform-bot-detection.md` - 中国房产平台(链家/贝壳/安居客/房天下)的bot检测模式
  - 📝 记录Baidu搜索+AI摘要作为有效替代方案
  - 📝 添加中国房产数据点中英对照表
  - 📝 添加建筑类型楼层范围推断指南
- **v1.4.0** (2026-08-09): fnOS Docker 部署经验
  - 📝 添加 `references/fnos-docker-deployment.md` - fnOS Docker 部署完整笔记
  - 📝 记录 Solverr 镜像拉取超时问题及解决方案
  - 📝 记录 fnOS Docker 操作验证 (alpine 拉取成功)
  - 📝 记录 Session 过期时间和重新登录方法
  - 📝 添加 fnOS Docker 镜像列表快照
- **v1.3.1** (2026-08-09): 实测修正更新
  - ⚠️ **纠正**: Camoufox 单独使用无法绕过 Cloudflare/DDoS-Guard，需要配合 playwright-captcha
  - 📝 添加 playwright-stealth API 使用说明 (`Stealth` 类 + `apply_stealth_async`)
  - 📝 添加 Docker 部署注意事项 (镜像大小、超时问题)
  - 📝 添加通用替代数据源策略 (RSS/API/sitemap)
  - 📝 更新参考文档中的 Camoufox 说明
- **v1.3.0** (2026-08-09): 网络调研更新 - 发现 Solverr、Camoufox 等新方案
  - 🆕 **Solverr**: Docker一键部署，整合 FlareSolverr + Camoufox，同时支持 Cloudflare + DDoS-Guard
  - 🆕 **Camoufox**: 反检测Firefox，编译级指纹修改
  - 🆕 **cloudflare-bypass-2026**: 5种绕过方案集合 (413 stars)
  - 🆕 **Turnstile-Solver-NEW**: 本地API解算器 (296 stars)
  - 📝 更新工具推荐表，Solverr 成为首选方案
  - 📝 更新方案对比表，添加 Solverr/Camoufox
  - 📝 更新最佳实践，首选 Solverr
  - 📝 添加 references/network-research-bypass-methods.md
- **v1.2.0** (2026-08-09): 重大更新 - Playwright + Stealth 成功绕过 DDoS-Guard
  - ✅ **新发现**: Playwright + Stealth 实测成功绕过 DDoS-Guard (repack-igruha.net)
  - ❌ **纠正**: curl_cffi TLS伪装对 Cloudflare/DDoS-Guard 完全无效 (23种impersonation均失败)
  - ❌ **纠正**: puppeteer-extra-stealth 对 DDoS-Guard 无效 (显示CAPTCHA页面)
  - 📝 更新工具推荐表，标注各工具对 Cloudflare/DDoS-Guard 的有效性
  - 📝 更新方案对比表，基于实测数据
  - 📝 更新最佳实践，强调 Playwright + Stealth 是 DDoS-Guard 唯一有效方案
  - 📝 添加 Playwright + Stealth 完整代码示例
- **v1.1.0** (2026-08-09): 新增DDoS-Guard技术细节和RSS Feed绕过技巧
  - 添加DDoS-Guard cookie结构、JS Challenge文件分析
  - 添加Cloudflare Managed Challenge实测数据 (share.acgnx.se)
  - 新增RSS Feed绕过技巧和替代端点探测方法
  - 新增TLS指纹伪装局限性说明
  - 添加请求频率建议
  - 添加ACGNX/IGRUHA详细分析参考文档
- **v1.0.0** (2026-08-08): 初始版本
  - 集成scrapling、playwright-bot-bypass、cloudflare-turnstile
  - 支持多种Cloudflare绕过方案
  - 提供完整使用示例和故障排除
