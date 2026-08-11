# Cloudflare Turnstile 绕过方案对比

## 方案选择指南

### 场景1: 简单网站，无Cloudflare
→ 使用 `Fetcher` (scrapling) 或 `curl_cffi`

### 场景2: Cloudflare JS Challenge
→ 使用 `StealthyFetcher` (scrapling) 或 `SeleniumBase`

### 场景3: Cloudflare Turnstile (CAPTCHA)
→ 使用 `cloudflare-turnstile` 技能中的方案

### 场景4: 重度JS渲染 + 登录
→ 使用 `DynamicFetcher` (scrapling) 或 Playwright

## Scrapling 方案

```python
from scrapling.fetchers import Fetcher, StealthyFetcher, DynamicFetcher

# 静态页面
page = Fetcher.get('https://example.com', impersonate='chrome')

# Cloudflare保护
page = StealthyFetcher.fetch(
    'https://protected-site.com',
    headless=True,
    solve_cloudflare=True,
)

# 重度JS
page = DynamicFetcher.fetch('https://spa-site.com')
```

## SeleniumBase 方案

```python
from seleniumbase import SB

# UC模式（推荐）
with SB(uc=True) as sb:
    sb.uc_open_with_reconnect("https://example.com")
    sb.sleep(3)
    html = sb.get_page_source()

# undetected模式
with SB(uc=True, undetectable=True) as sb:
    sb.uc_open_with_reconnect("https://example.com")
```

## curl_cffi 方案

```python
from curl_cffi import requests

# TLS指纹伪装
response = requests.get(
    "https://example.com",
    impersonate="chrome"  # 或 "edge", "safari" 等
)
```

## nodriver 方案

```python
import nodriver as uc

async def main():
    browser = await uc.start()
    page = await browser.get("https://example.com")
    await asyncio.sleep(5)
    # 页面已绕过检测
```

## 常见问题

### Turnstile未解决
- 尝试增加等待时间
- 检查是否需要点击验证框
- 尝试其他绕过方案

### IP被封
- 使用代理池
- 控制请求频率
- 轮换User-Agent

### 页面内容为空
- 检查是否需要等待JS渲染
- 尝试使用DynamicFetcher
- 检查网络连接
