# DDoS-Guard 绕过: Playwright + Stealth 实测报告

## 测试日期: 2026-08-09

## 测试目标
- **repack-igruha.net** (俄语游戏Repack站)
- 反爬虫系统: DDoS-Guard

## 测试结果

### ✅ 成功方案: Playwright + Stealth

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

### 测试结果详情

| 测试项 | 结果 | 详情 |
|--------|------|------|
| 首页访问 | ✅ 成功 | 标题: "Торрент-Игруха - репаки от Игрухи и каталог игр для ПК" |
| 内容提取 | ✅ 成功 | 2867 字符, 206 个链接 |
| 游戏页面 | ✅ 成功 | 可访问详情页, 2151 字符 |
| Cookie获取 | ✅ 成功 | 11 个 cookies (含 DDoS-Guard 验证 cookie) |

### 获取的 Cookies

| Cookie | 值 (前30字符) | 用途 |
|--------|--------------|------|
| `__ddg9_` | `44.243.117.151...` | IP地址 |
| `__ddgid_` | `GFmuEE6WP4OvN5rM...` | 唯一ID |
| `__ddgmark_` | `CdoQCQMOoQ7jKFDQ...` | 标记 |
| `__ddg5_` | `JpBNr5i6wwq0oVJr...` | 验证状态 |
| `__ddg2` | `23VBIzgdVvKL1wEN...` | 设备识别 |
| `ddg_last_challenge` | `1786312192821...` | 最后挑战时间 |
| `__ddg1_` | `eaGrb9MELgd6pxNNdNl1...` | 主防护Cookie |
| `PHPSESSID` | `94fe762297a2ace5a2720adb039b7e...` | PHP会话 |

### ❌ 失败方案

| 方案 | 结果 | 原因 |
|------|------|------|
| curl_cffi (chrome) | ❌ 403 | JS Challenge无法执行 |
| curl_cffi (chrome120) | ❌ 403 | 同上 |
| curl_cffi (safari15_3) | ❌ 403 | 同上 |
| puppeteer-extra-stealth | ❌ CAPTCHA | 显示"Sorry, we could not verify" |
| scrapling Fetcher | ❌ 403 | 无法执行JS |

## 关键发现

1. **Playwright + Stealth 是 DDoS-Guard 唯一有效绕过方案**
2. **curl_cffi TLS 伪装完全无效** - 所有 impersonation 都被拦截
3. **puppeteer-extra-stealth 不如 Playwright + Stealth** - 前者显示 CAPTCHA，后者直接通过
4. **DDoS-Guard 验证需要真实浏览器环境** - 纯 HTTP 请求无法绕过

## 安装依赖

```bash
cd /opt/data && source anti_bot_env/bin/activate
pip install playwright-stealth
```

## 注意事项

1. **请求频率**: 即使绕过成功，也要添加延迟 (建议 5-10 秒)
2. **Cookie 维护**: 获取的 cookies 有效期有限，需要定期重新验证
3. **User-Agent**: 使用真实的 Chrome User-Agent
4. **viewport**: 设置合理的视口大小 (1920x1080)
5. **locale**: 根据目标网站设置合适的语言 (如 ru-RU)
