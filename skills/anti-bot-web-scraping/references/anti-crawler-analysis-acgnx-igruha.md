# Anti-Crawler Analysis: share.acgnx.se & repack-igruha.net

## 分析日期: 2026-08-09

---

## 1. share.acgnx.se (AcgnX末日動漫資源庫)

### 基本信息
- **站点类型**: ACG (Anime, Comic, Game) 资源分享站
- **语言**: 中文
- **技术栈**: jQuery, Cloudflare CDN
- **内容**: 动漫BT种子/磁力链接资源

### 反爬虫系统: Cloudflare (Managed Challenge)

#### 挑战机制
```
响应头: cf-mitigated: challenge
页面标题: "Just a moment..."
挑战类型: Cloudflare Turnstile (Managed)
```

#### 挑战页面结构
1. **JS Challenge**: 动态加载 `/cdn-cgi/challenge-platform/h/b/orchestrate/chl_page/v1`
2. **CSP Nonce**: 每次请求生成唯一nonce
3. **Turnstile Widget**: iframe加载 `https://challenges.cloudflare.com`
4. **自动验证**: 无需用户交互，JS自动执行验证

#### 安全头分析
| Header | Value |
|--------|-------|
| Server | cloudflare |
| X-Frame-Options | SAMEORIGIN |
| X-Content-Type-Options | nosniff |
| Referrer-Policy | same-origin |
| Permissions-Policy | 完整限制列表 |
| CSP | 严格限制，仅允许challenges.cloudflare.com |

#### TLS指纹测试结果
| Impersonation | Status | 结果 |
|---------------|--------|------|
| chrome | 403 | ❌ 被拦截 |
| chrome110 | 403 | ❌ 被拦截 |
| chrome120 | 403 | ❌ 被拦截 |
| chrome124 | 403 | ❌ 被拦截 |
| safari15_3 | 403 | ❌ 被拦截 |
| safari17_0 | 403 | ❌ 被拦截 |
| firefox | 403 | ❌ 被拦截 |

**结论**: Cloudflare不依赖TLS指纹，所有impersonation都被拦截。

#### 关键发现: RSS Feed绕过
```
URL: https://share.acgnx.se/rss.xml
Status: 200 ✅
Size: 50,435 bytes
Items: 50条资源
```

**RSS Feed包含**:
- 资源标题 (中英文)
- 资源链接 (show-*.html)
- 发布时间
- 资源描述

**限制**: 
- RSS Feed可访问，但个别资源页面 (show-*.html) 仍被Cloudflare拦截
- 无法通过RSS获取下载链接 (magnet/torrent)

#### 自动化绕过测试
| 工具 | 结果 | 原因 |
|------|------|------|
| curl_cffi (TLS伪装) | ❌ 失败 | JS Challenge需要真实浏览器环境 |
| scrapling Fetcher | ❌ 失败 | 同上 |
| scrapling StealthyFetcher | ❌ 失败 | 缺少patchright模块 |
| SeleniumBase UC模式 | ❌ 失败 | Chrome未正确配置 |
| Playwright + 反检测 | ❌ 失败 | Turnstile自动验证失败 |
| nodriver | ❌ 失败 | 浏览器连接问题 |

---

## 2. repack-igruha.net (Торрент-Игруха)

### 基本信息
- **站点类型**: 俄语游戏资源分享站 (PC游戏Repack)
- **语言**: 俄语
- **内容**: 游戏BT种子/磁力链接资源

### 反爬虫系统: DDoS-Guard

#### 挑战机制
```
服务器: ddos-guard
响应状态: 403
挑战类型: JS Challenge + CAPTCHA (图片验证)
```

#### DDoS-Guard Cookies (7个)
| Cookie | 用途 | 生命周期 |
|--------|------|----------|
| `__ddg8_` | 会话标识 | 20分钟 |
| `__ddg10_` | 时间戳 | 20分钟 |
| `__ddg9_` | IP地址 | 20分钟 |
| `__ddgid_` | 唯一ID | 1年 |
| `__ddgmark_` | 标记 | 1天 |
| `__ddg5_` | 验证状态 | 3小时 |
| `__ddg7_` | 标志位 | 5分钟 |

#### 挑战流程
1. **初始请求**: 返回403 + DDoS-Guard cookies
2. **JS Challenge**: 加载三个脚本:
   - `/.well-known/ddos-guard/js-challenge/view.js` (61KB, 混淆)
   - `/.well-known/ddos-guard/js-challenge/index.js` (191KB, webpack打包)
   - `https://check.ddos-guard.net/check.js` (152B, 信标)
3. **浏览器验证**: "Checking your browser before accessing..."
4. **CAPTCHA验证**: 图片选择验证 (如 "Select all images with crosswalks")
5. **通过后**: 设置cookie，允许访问

#### JS分析结果
**view.js**:
- 混淆的JavaScript代码
- 设置 `__ddg8_`, `__ddg10_`, `__ddg9_` cookies
- 包含浏览器指纹收集

**index.js**:
- Webpack打包的大型脚本
- 包含222个iframe/embed引用
- 集成CAPTCHA验证
- 包含广告拦截检测 (`getAdBlock`)

**check.js**:
- 简单的信标脚本
- 创建Image对象发送请求到:
  - `/.well-known/ddos-guard/id/{id}`
  - `https://check.ddos-guard.net/set/id/{id}`

#### 安全特性
- **全站保护**: 所有路径 (/, /api/, /search, etc.) 都返回403
- **无robots.txt**: robots.txt也被DDoS-Guard拦截
- **无API端点**: 所有API路径都被保护

#### TLS指纹测试结果
| Impersonation | Status | 结果 |
|---------------|--------|------|
| chrome | 403 | ❌ 被拦截 |
| chrome110 | 403 | ❌ 被拦截 |
| chrome120 | 403 | ❌ 被拦截 |
| chrome124 | 403 | ❌ 被拦截 |
| safari15_3 | 403 | ❌ 被拦截 |
| safari17_0 | 403 | ❌ 被拦截 |
| firefox | 403 | ❌ 被拦截 |

**注意**: 早期测试中chrome impersonation曾返回200，但后续请求都被403拦截，说明DDoS-Guard会跟踪IP并加强防护。

#### 自动化绕过测试
| 工具 | 结果 | 原因 |
|------|------|------|
| curl_cffi (TLS伪装) | ❌ 失败 | JS Challenge + CAPTCHA |
| scrapling Fetcher | ❌ 失败 | 同上 |
| Playwright + 反检测 | ❌ 失败 | CAPTCHA需要人工交互 |
| nodriver | ❌ 失败 | 浏览器连接问题 |

---

## 3. 对比分析

| 特性 | share.acgnx.se | repack-igruha.net |
|------|----------------|-------------------|
| **反爬虫系统** | Cloudflare | DDoS-Guard |
| **挑战类型** | JS Challenge (Turnstile) | JS Challenge + CAPTCHA |
| **用户交互** | 无 (自动验证) | 有 (图片选择) |
| **RSS Feed** | ✅ 可访问 | ❌ 被拦截 |
| **API端点** | ❌ 被拦截 | ❌ 被拦截 |
| **Cookies数量** | 0 (Cloudflare管理) | 7 (DDoS-Guard) |
| **保护范围** | 主页及资源页 | 全站所有路径 |
| **绕过难度** | ⭐⭐⭐⭐ (高) | ⭐⭐⭐⭐⭐ (极高) |

---

## 4. 绕过策略评估

### share.acgnx.se
1. **RSS Feed**: ✅ 可用于获取资源列表
2. **资源详情页**: ❌ 需要绕过Cloudflare
3. **下载链接**: ❌ 需要访问资源详情页

**可行方案**:
- 使用RSS Feed获取最新资源
- 资源详情页需要真实浏览器 + Turnstile自动验证
- 可能需要付费Cloudflare bypass服务

### repack-igruha.net
1. **所有页面**: ❌ 被DDoS-Guard拦截
2. **CAPTCHA**: 图片选择验证，需要人工交互

**可行方案**:
- 目前无可靠自动化方案
- DDoS-Guard的CAPTCHA需要真实用户交互
- 可能需要手动验证后保持session

---

## 5. 请求频率建议

### share.acgnx.se
- **RSS Feed**: 可以每5-10分钟请求一次
- **资源页面**: 避免频繁请求，建议间隔30秒以上
- **注意**: 频繁请求可能触发Cloudflare更严格的挑战

### repack-igruha.net
- **建议**: 不要频繁请求
- **原因**: DDoS-Guard会跟踪IP，频繁请求会导致更严格的CAPTCHA
- **策略**: 手动验证一次，保持cookie，然后低频率请求

---

## 6. 技术细节

### Cloudflare Turnstile (share.acgnx.se)
- **挑战类型**: Managed Challenge
- **JS加载**: `/cdn-cgi/challenge-platform/h/b/orchestrate/chl_page/v1`
- **验证方式**: 自动JS执行 + 浏览器环境检测
- **CSP**: 严格限制，仅允许challenges.cloudflare.com

### DDoS-Guard (repack-igruha.net)
- **挑战类型**: JS Challenge + Image CAPTCHA
- **JS文件**: view.js (61KB混淆) + index.js (191KB webpack)
- **Cookie机制**: 7个cookie，包含IP、时间戳、验证状态
- **CAPTCHA类型**: 图片选择 (如选择人行横道)

---

## 7. 结论

1. **share.acgnx.se**: 
   - Cloudflare Managed Challenge 无法通过TLS指纹伪装绕过
   - RSS Feed是唯一可用的数据源
   - 资源详情页需要真实浏览器环境

2. **repack-igruha.net**: 
   - DDoS-Guard 是目前最难绕过的反爬虫系统之一
   - 所有路径都被保护，无API后门
   - CAPTCHA需要人工交互，无法自动化

3. **通用建议**: 
   - 这两个站点都应该谨慎访问，避免触发封锁
   - 使用代理和延迟来分散请求
   - 优先使用RSS Feed等合法数据源

---

## 附录: 测试环境

- **工具**: curl_cffi, scrapling, Playwright, SeleniumBase, nodriver
- **虚拟环境**: /opt/data/anti_bot_env
- **Chrome**: /opt/data/home/.agent-browser/browsers/chrome-150.0.7871.115/chrome
- **测试时间**: 2026-08-09 20:37-20:50 UTC
