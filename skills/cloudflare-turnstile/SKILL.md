---
name: cloudflare-turnstile
description: >
  Cloudflare Turnstile验证码绕过工具集。使用此技能绕过Cloudflare保护的网站，
  包括Turnstile验证码、JS挑战和反爬虫检测。支持多种绕过方案：
  SeleniumBase、CDP、curl_cffi、nodriver等。
  触发词：cloudflare、turnstile、验证码绕过、反爬虫、anti-bot
---

# Cloudflare Turnstile 绕过技能

## 功能概述

本技能提供多种绕过Cloudflare Turnstile验证码的方法，适用于被Cloudflare保护的网站。

## 🎯 适用场景

- 网站显示"Checking your browser before accessing..."
- 需要通过Cloudflare Turnstile验证
- 遇到Cloudflare JS Challenge
- 网站有反爬虫检测
- 需要绕过Cloudflare保护进行数据采集

## 📦 支持的绕过方案

| 方案 | 文件 | 适用场景 | 难度 |
|------|------|----------|------|
| **SeleniumBase** | `bypass_seleniumbase.py` | 最稳定，推荐首选 | ⭐⭐ |
| **CDP** | `bypass_cdp.py` | Chrome DevTools Protocol | ⭐⭐⭐ |
| **curl_cffi** | `bypass_curl_cffi.py` | 轻量级，TLS指纹伪装 | ⭐⭐ |
| **nodriver** | `bypass_nodriver.py` | 无驱动浏览器 | ⭐⭐⭐ |
| **简化版** | `simple_bypass.py` | 快速测试 | ⭐ |

## 🚀 快速开始

### 1. 安装依赖

```bash
cd /opt/data/skills/cloudflare-turnstile
pip install -r requirements.txt
```

### 2. 使用SeleniumBase方案（推荐）

```python
from bypass_seleniumbase import CloudflareBypass

bypass = CloudflareBypass()
result = bypass.solve("https://example.com")
print(result)
```

### 3. 命令行使用

```bash
# 使用SeleniumBase方案
python bypass_seleniumbase.py https://example.com

# 使用CDP方案
python bypass_cdp.py https://example.com

# 使用curl_cffi方案
python bypass_curl_cffi.py https://example.com
```

## 📋 方案详解

### 方案1: SeleniumBase（推荐 ⭐⭐⭐⭐⭐）

**优点**: 最稳定，成功率高，支持最新Cloudflare版本

```python
from seleniumbase import SB

with SB(uc=True) as sb:
    sb.uc_open_with_reconnect("https://example.com")
    sb.sleep(3)
    # 页面已绕过Cloudflare
    html = sb.get_page_source()
```

### 方案2: CDP (Chrome DevTools Protocol)

**优点**: 直接控制Chrome，灵活性高

```python
import subprocess
import json

# 启动Chrome with CDP
subprocess.Popen([
    'google-chrome',
    '--remote-debugging-port=9222',
    '--no-sandbox'
])

# 连接CDP进行操作
```

### 方案3: curl_cffi

**优点**: 轻量级，TLS指纹伪装，无需浏览器

```python
from curl_cffi import requests

# 使用浏览器TLS指纹
response = requests.get(
    "https://example.com",
    impersonate="chrome"
)
print(response.text)
```

### 方案4: nodriver

**优点**: 无驱动浏览器，更难被检测

```python
import nodriver as uc

async def main():
    browser = await uc.start()
    page = await browser.get("https://example.com")
    # 页面已绕过Cloudflare
```

## ⚙️ 配置说明

### 代理配置

编辑 `proxy.txt` 文件，每行一个代理：

```
http://proxy1:port
socks5://proxy2:port
http://user:pass@proxy3:port
```

### 超时设置

```python
# 修改超时时间
TIMEOUT = 30  # 秒
```

## 🔧 故障排除

| 问题 | 解决方案 |
|------|----------|
| `TimeoutError` | 增加超时时间，检查网络连接 |
| `验证码未解决` | 尝试其他绕过方案 |
| `代理连接失败` | 检查proxy.txt中的代理配置 |
| `Chrome版本过低` | 更新Chrome到最新版本 |

## 📊 方案对比

| 特性 | SeleniumBase | CDP | curl_cffi | nodriver |
|------|--------------|-----|-----------|----------|
| 稳定性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 速度 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 资源占用 | 高 | 高 | 低 | 中 |
| 难度 | 低 | 中 | 低 | 中 |
| 成功率 | 高 | 高 | 中 | 高 |

## 🎯 最佳实践

1. **首选 Solverr**: Docker一键部署，整合 FlareSolverr + Camoufox，自动故障转移
2. **次选 SeleniumBase UC Mode**: 最稳定的单机方案
3. **不要用 curl_cffi**: TLS伪装无法绕过 Turnstile（无JS运行时、无DOM、无交互能力）
4. **使用代理**: 避免IP被封，住宅代理效果最佳
5. **添加延迟**: 模拟人类行为，避免触发更严格验证
6. **错误处理**: 捕获异常并重试

## 📝 使用示例

### 示例1: 绕过Cloudflare并获取页面内容

```python
from bypass_seleniumbase import CloudflareBypass

bypass = CloudflareBypass()
html = bypass.get_page("https://protected-site.com")
print(html[:500])
```

### 示例2: 使用代理绕过

```python
from curl_cffi import requests

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

### 示例3: 批量绕过

```python
import asyncio
from nodriver import uc

async def bypass_multiple(urls):
    browser = await uc.start()
    for url in urls:
        page = await browser.get(url)
        await asyncio.sleep(5)
        # 处理页面
    await browser.stop()

urls = ["https://site1.com", "https://site2.com"]
asyncio.run(bypass_multiple(urls))
```

## 🔗 相关资源

- Cloudflare Turnstile文档: https://developers.cloudflare.com/turnstile/
- SeleniumBase: https://github.com/seleniumbase/SeleniumBase
- curl_cffi: https://github.com/lexiforest/curl_cffi
- nodriver: https://github.com/ultrafunkamsterdam/nodriver

## ⚠️ 适用范围

本技能**仅适用于 Cloudflare 保护的网站**。以下防护系统**不适用**：

- **DDoS-Guard** — 需要使用 `Playwright + Stealth` 方案（详见 `anti-bot-web-scraping` 技能）
- **Akamai Bot Manager** — 需要特殊处理
- **DataDome** — 需要特殊处理

**识别方法**：用 `curl -sI <url>` 检查响应头：
- `server: cloudflare` → 本技能适用
- `server: ddos-guard` → 使用 `anti-bot-web-scraping` 技能中的 DDoS-Guard 部分（Playwright + Stealth）

### 🔧 最新工具推荐 (2026-08-09)

**Solverr** — 最全面的 Cloudflare 绕过方案：
```bash
# Docker部署
docker run -d -p 8191:8191 --shm-size=512m ghcr.io/unseensnick/solverr:latest

# 使用
curl -sX POST 'http://localhost:8191/v1' \
  -H 'Content-Type: application/json' \
  --data '{"cmd":"request.get","url":"https://example.com/","maxTimeout":60000}'
```

**Turnstile-Solver-NEW** — 本地API解算器：
```bash
git clone https://github.com/D3-vin/Turnstile-Solver-NEW.git
cd Turnstile-Solver-NEW && pip install -r requirements.txt
python api.py  # 服务启动在 http://0.0.0.0:5072
```

## ⚠️ 注意事项

1. **合法使用**: 仅用于合法的数据采集和测试
2. **尊重robots.txt**: 遵守网站的爬虫协议
3. **控制频率**: 避免对目标网站造成压力
4. **IP轮换**: 使用代理池避免IP被封
5. **错误处理**: 做好异常处理和重试机制

## 📅 更新日志

- **v1.2.0** (2026-08-09): 网络调研更新 - 添加 Solverr 和 Turnstile-Solver
  - 🆕 添加 Solverr 推荐（Docker一键部署，FlareSolverr + Camoufox双引擎）
  - 🆕 添加 Turnstile-Solver-NEW 推荐（本地API解算器）
  - ❌ 纠正：curl_cffi TLS伪装无法绕过 Turnstile
  - 📝 更新最佳实践，首选 Solverr
  - 📝 添加最新工具推荐部分
- **v1.1.0** (2026-08-09): 更新DDoS-Guard说明
  - 纠正：DDoS-Guard 现在可以通过 Playwright + Stealth 绕过
  - 更新适用范围说明，指引用户使用正确的技能
- **v1.0.0** (2026-08-08): 初始版本
  - 支持SeleniumBase、CDP、curl_cffi、nodriver四种方案
  - 内置代理配置
  - 完整的错误处理
