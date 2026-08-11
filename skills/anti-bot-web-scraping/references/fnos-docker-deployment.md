# fnOS Docker 部署笔记

## 部署日期: 2026-08-09

## 目标
在 fnOS (TRIM NAS) 上部署 Solverr Docker 容器以绕过 Cloudflare/DDoS-Guard。

## 环境信息
- **fnOS 地址**: 192.168.31.118
- **WebSocket 端口**: 5566
- **协议**: ws:// (明文)
- **用户名**: aiamdin
- **密码位置**: `/opt/data/.env` → `password` 变量

## 连接命令
```bash
# 登录
cd /opt/data && source /opt/data/.env
./skills/trim-cli/scripts/trim-cli --host 192.168.31.118 --port 5566 --scheme ws --allow-insecure-ws login -u aiamdin -p "$password"

# Docker 操作
./skills/trim-cli/scripts/trim-cli --host 192.168.31.118 --port 5566 --scheme ws --allow-insecure-ws docker stats
./skills/trim-cli/scripts/trim-cli --host 192.168.31.118 --port 5566 --scheme ws --allow-insecure-ws docker image ls
./skills/trim-cli/scripts/trim-cli --host 192.168.31.118 --port 5566 --scheme ws --allow-insecure-ws docker image pull <image>
```

## 部署测试结果

### ✅ 成功操作
| 操作 | 镜像 | 结果 |
|------|------|------|
| Docker stats | - | ✅ 正常，22个容器运行中 |
| Docker image pull | alpine:latest | ✅ 成功 |
| Docker image ls | - | ✅ 正常，28个镜像 |

### ❌ 失败操作
| 操作 | 镜像 | 结果 | 原因 |
|------|------|------|------|
| Docker image pull | ghcr.io/unseensnick/solverr:latest | ❌ 超时 | 镜像约2.3GB，拉取时间过长 |

## Solverr 镜像拉取问题

**问题描述**:
- Solverr 镜像大小约 2.3GB
- fnOS Docker 拉取大镜像时会超时
- trim-cli 的 `docker image pull` 命令提交后返回 "request submitted"，但实际拉取可能失败

**错误信息**:
```
Error: failed to get docker data from 192.168.31.118:5566: request ... failed with errno 52428818
Error: failed to get docker data from 192.168.31.118:5566: timed out waiting for websocket response
```

**解决方案**:
1. **手动拉取**: 在 fnOS Web UI 的 Docker 页面手动拉取镜像
2. **使用小镜像**: 先测试小镜像 (如 alpine) 确认 Docker 正常工作
3. **本地部署**: 如果 Docker 不可用，考虑在本地使用 Playwright + Stealth

## 替代方案

由于 Solverr 部署困难，建议使用已验证的方案：

### 1. Playwright + Stealth (DDoS-Guard)
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
            locale='ru-RU'
        )
        page = await context.new_page()
        s = Stealth()
        await s.apply_stealth_async(page)
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(10)
        return await page.inner_text('body')
```

### 2. RSS Feed (Cloudflare)
```python
from curl_cffi import requests
r = requests.get('https://share.acgnx.se/rss.xml', impersonate='chrome', timeout=15)
# Status: 200, 50 items
```

## Session 管理

**Session 过期时间**: 约24小时

**检查 Session 状态**:
```python
import json, time
with open('/opt/data/home/.config/trim-cli/session.json', 'r') as f:
    session = json.load(f)
updated = int(session.get('updatedAt', 0))
hours = (time.time() - updated) / 3600
print(f'Expired' if hours > 24 else 'Valid')
```

**重新登录**:
```bash
./skills/trim-cli/scripts/trim-cli --host 192.168.31.118 --port 5566 --scheme ws --allow-insecure-ws login -u aiamdin -p "$password"
```

## Docker 镜像列表 (2026-08-09)

当前 fnOS 上的 Docker 镜像:
- hermes-agent:latest
- n8nio/n8n:latest
- ghcr.nju.edu.cn/xinnan-tech/xiaozhi-esp32-server:web_latest
- ghcr.nju.edu.cn/xinnan-tech/xiaozhi-esp32-server:server_latest
- lscr.io/linuxserver/prowlarr:latest
- xream/sub-store:latest
- nginx:latest
- dowloads_qbit:latest
- traefik:latest
- certimate/certimate:latest
- mysql:latest
- openhuman:latest
- ghcr.io/qq85423296/t3fap:latest
- ghcr.io/beck-8/subs-check:latest
- ghcr.io/decohererk/decotv:latest
- node:22-bookworm-slim
- postgres:16
- debian:13.4
- registry.cn-guangzhou.aliyuncs.com/zhcxh/dowloads_qbit:latest
- 6053537/portainer-ce:latest
- ghcr.nju.edu.cn/xinnan-tech/mcp-endpoint-server:latest
- ghcr.io/fish2018/pansou-web:latest
- redis:8.0
- a1ex4/ownfoil:latest
- 1555904/solara-music:latest
- registry.fnnas.com/fnapp/linzeyi_hivision_idphotos:latest
- registry.cn-guangzhou.aliyuncs.com/zhcxh/watchtower:latest
- oldiy/dosgame-web-docker:latest

## 总结

1. **fnOS Docker 操作正常** - 小镜像拉取成功
2. **大镜像拉取超时** - Solverr (~2.3GB) 无法通过 trim-cli 拉取
3. **建议**: 使用 Web UI 手动拉取，或使用已验证的 Playwright + Stealth 方案
