# 反爬虫绕过方案 - 网络调研汇总

## 调研日期: 2026-08-09

---

## 🏆 最佳方案

### 1. Solverr (推荐 ⭐⭐⭐⭐⭐)
- **GitHub**: https://github.com/unseensnick/Solverr
- 整合 FlareSolverr (Chrome引擎) + Byparr (Camoufox隐身引擎)
- **同时支持 Cloudflare + DDoS-Guard**
- 自动故障转移：Chrome引擎失败 → Camoufox点击解决
- Docker部署：`docker run -d -p 8191:8191 ghcr.io/unseensnick/solverr:latest`
- 兼容 FlareSolverr `/v1` API

### 2. Camoufox (推荐 ⭐⭐⭐⭐⭐)
- **GitHub**: https://github.com/daijro/camoufox
- 开源反检测浏览器，基于Firefox
- 在编译级别修改指纹
- 被Solverr、Byparr等项目采用
- ⚠️ **实测注意**: 单独使用无法绕过 Cloudflare/DDoS-Guard，需要配合 playwright-captcha 等工具

### 3. cloudflare-bypass-2026 (推荐 ⭐⭐⭐⭐)
- **GitHub**: https://github.com/1837620622/cloudflare-bypass-2026 (413 stars)
- 5种绕过方案：SeleniumBase UC/CDP、nodriver CDP、curl_cffi TLS
- **关键结论**: curl_cffi 无法通过 Turnstile — 无JS运行时、无DOM、无交互能力

### 4. Turnstile-Solver-NEW (推荐 ⭐⭐⭐⭐)
- **GitHub**: https://github.com/D3-vin/Turnstile-Solver-NEW (296 stars)
- 本地API解算器，支持 Turnstile + IUAM
- 多线程并发，REST API接口

---

## 🔑 关键技术洞察

### 为什么 curl_cffi 无法绕过 Turnstile?
1. **无JS运行时** — 无法执行Turnstile挑战
2. **无DOM/Web API** — 缺少navigator、WebGL、canvas信号
3. **无交互能力** — Managed模式需要真实点击
4. **TLS只是信号之一** — JA3/JA4匹配不够

### 2025-2026 Cloudflare检测分层
1. 网络信誉 (IP reputation)
2. TLS/HTTP指纹
3. JavaScript挑战
4. Turnstile交互
5. 自动化协议特征

### 推荐基线方案
```
有头真实Chrome
  + 住宅/高质量出口IP
  + UC断连重连 或 纯CDP
  + 需要交互时使用操作系统级点击
```

---

## 📊 方案对比

| 方案 | Cloudflare | DDoS-Guard | 部署难度 | 推荐度 |
|------|-----------|------------|---------|--------|
| **Solverr** | ✅ | ✅ | ⭐ 简单(Docker) | ⭐⭐⭐⭐⭐ |
| **Camoufox** | ✅ | ✅ | ⭐⭐ 中等 | ⭐⭐⭐⭐⭐ |
| **cloudflare-bypass-2026** | ✅ | ❓ | ⭐⭐ 中等 | ⭐⭐⭐⭐ |
| **Turnstile-Solver** | ✅ | ❓ | ⭐⭐ 中等 | ⭐⭐⭐⭐ |
| **Playwright+Stealth** | ❌ | ✅ | ⭐ 简单 | ⭐⭐⭐ |

---

## 📚 参考资源

1. **Solverr**: https://github.com/unseensnick/Solverr
2. **Camoufox**: https://github.com/daijro/camoufox
3. **cloudflare-bypass-2026**: https://github.com/1837620622/cloudflare-bypass-2026
4. **Turnstile-Solver**: https://github.com/D3-vin/Turnstile-Solver-NEW
5. **FlareSolverr**: https://github.com/FlareSolverr/FlareSolverr
6. **Byparr**: https://github.com/ThePhaseless/Byparr
