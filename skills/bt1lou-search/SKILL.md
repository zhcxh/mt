---
name: bt1lou-search
description: 搜索 BT之家1LOU站 (www.1lou.pro)，自动过滤网盘资源，仅保留 BT 种子/磁力链接，适合日常观影筛选。
trigger: 用户要找电影/电视剧/动漫下载资源 | 需要搜索 BT 种子 | 日常观影找片
os:
  - linux
  - darwin
requires:
  bins: ["node", "npm", "curl"]
  env: ["PATH"]
---

# BT之家1LOU站 搜索技能

在 BT之家1LOU站 搜索影视资源，自动过滤网盘/夸克/阿里云盘等非 BT 资源，仅保留 BT 种子下载。

## 前置依赖

```bash
npm install -g agent-browser --prefix ~/.npm-global 2>/dev/null
export PATH="$HOME/.npm-global/bin:$PATH"
agent-browser install 2>/dev/null
```

## ⚠️ 完整工作流（搜索 → 下载 → 验证 → 推送）

**每次搜索任务都必须完成全部4步，不要中途停下：**

1. **搜索** — URL编码关键词，翻页收集所有结果
2. **下载** — 过滤网盘，批量下载BT种子文件
3. **验证** — 解析bencode确认种子内容正确（⚠️ 错误是常态）
4. **推送** — 推送到qBittorrent并确认开始下载

> ❌ 常见错误：下载完种子就停下，忘记推送到 qBittorrent。用户期望的是完整流程。
> ❌ 常见错误：验证发现错误种子后只删不补，导致部分集数缺失。

## 🔍 完整搜索工作流

### 步骤 1：URL 直接搜索（推荐，比表单更可靠）

使用 `browser_navigate` 直接导航到搜索 URL，跳过表单提交：

```
# 中文关键词需要 URL 编码（用 Python urllib.parse.quote）
browser_navigate(url="https://www.1lou.pro/search-{url_encoded_keyword}-1.htm")
```

- `-1.htm` = 主题贴（默认，先试这个）
- `-0.htm` = 所有贴（含回复，覆盖更广）

**分页：** 搜索结果可能有多页（最多4页）。分页 URL 格式：
```
https://www.1lou.pro/search-{encoded_keyword}-1-{page}.htm
# 例如第2页：
https://www.1lou.pro/search-%E5%A4%AB%E5%A6%BB%E7%9A%84%E5%8D%9A%E5%BC%88-1-2.htm
```
> ⚠️ **电视剧搜索必须翻页！** 第1页只显示最新几集，早期集数在后续页面。用 JS 提取分页链接：`document.querySelectorAll('a[href*="search-"]').forEach(...)` 找到页码链接。

**示例：**
```
# "騎呢大狀" → URL 编码后：
browser_navigate(url="https://www.1lou.pro/search-%E9%AA%91%E5%91%A2%E5%A4%A7%E7%8A%B6-1.htm")
```

### 备选：表单搜索

如果 URL 搜索无结果，可尝试表单搜索（偶尔覆盖范围不同）：

```
browser_navigate(url="https://www.1lou.pro/")
browser_type(ref="@e27", text="<搜索关键词>")
browser_click(ref="@e28")
```

> **注意：** 首页搜索框 ref 每次新会话会变，务必先 `browser_snapshot` 确认。

### 步骤 2：获取搜索结果并过滤

```
browser_snapshot()
```

从结果中手动过滤：

| 过滤规则 | 操作 |
|----------|------|
| ❌ **网盘资源** | 标题含「夸克下载」「阿里云盘」「网盘」的**丢弃** |
| ✅ **BT 种子** | 标题含「BT下载」「BD-MKV」「WEB-MKV」「BluRay」的**保留** |
| ✅ **日常观影** | 优先选择 **1080P** 适中大小，其次 **4K** 高品质 |
| ✅ **推荐格式** | H265(省空间) > H264(兼容好)，10bit > 8bit |

**日常观影推荐大小参考：**
- 1080p H265: **1~4 GB**（省空间，画质够好）
- 1080p H264: **3~8 GB**（兼容性好）
- 4K H265: **8~20 GB**（高品质）
- 4K 60fps H265: **4~6 GB**（丝滑+体积适中，日常首选）
- 4K Remux: 20G+（发烧友）

### 步骤 3：点击结果进入详情页

```
browser_click(ref="<结果的 ref>")
browser_snapshot()
```

### 步骤 4：提取种子下载链接

```javascript
// 在 browser_console 中执行
Array.from(document.querySelectorAll('a'))
  .filter(a => a.textContent.includes('.torrent'))
  .map(a => a.href)
```

返回类似：`https://www.1lou.pro/attach-download-xxxxxx.htm`

### 步骤 5：下载种子文件

```bash
curl -sL -o "/opt/data/<文件名>.torrent" "https://www.1lou.pro/attach-download-xxxxxx.htm"
```

### 步骤 5.5：验证种子文件内容（⚠️ 必须执行，不可跳过）

**实测踩坑：** 从搜索结果提取的种子文件可能包含完全不同的影片内容！原因是 thread 页面的 attach-download ID 可能指向错误附件。

**必须在推送 qBittorrent 之前验证每个种子文件：**

```python
import os
for f in os.listdir("/opt/data/"):
    if f.endswith(".torrent") and "关键词" in f:  # 替换为实际关键词
        with open("/opt/data/" + f, "rb") as fp:
            data = fp.read()
            if b"4:name" in data:
                idx = data.index(b"4:name")
                nls = data.index(b":", idx + 6)
                nl = int(data[idx + 6:nls])
                name = data[nls + 1 : nls + 1 + nl].decode("utf-8", errors="replace")
                print("{} → {}".format(f, name[:60]))
```

- ✅ 种子名称包含预期影片名 → 继续
- ❌ 种子名称是其他影片 → **立即删除**，重新从正确的 thread 页面提取 attach-download ID

### 步骤 6：推送 qBittorrent（⚠️ 下载后必须执行，不要遗忘）

```bash
# 登录
curl -s -c /tmp/qb_cookies.txt \
  --data "username=<用户名>&password=<密码>" \
  "http://<qB主机IP>:8989/api/v2/auth/login"

# 添加种子
curl -s -b /tmp/qb_cookies.txt \
  -F "fileselect=@/path/to/<文件名>.torrent" \
  -F "savepath=/data/downloads" \
  "http://<qB主机IP>:8989/api/v2/torrents/add"

# 查看下载状态（可选）
curl -s -b /tmp/qb_cookies.txt \
  "http://<qB主机IP>:8989/api/v2/torrents/info?filter=all" | python3 -c "
import json,sys
for t in json.load(sys.stdin):
    print(f\"名称: {t['name']}\\n进度: {t['progress']*100:.1f}%\\n状态: {t['state']}\\n大小: {t['total_size']/1024/1024/1024:.2f} GB\\n速度: {t['dlspeed']/1024:.1f} KB/s\")
"
```

## ⚠️ 过滤规则详解

### 发现即丢弃的网盘关键词
```
夸克下载, 阿里云盘, 百度网盘, 网盘, 天翼云, 123云盘, 迅雷云盘
```

### 保留的 BT 类型关键词
```
BT下载, BD-MKV, WEB-MKV, BD-4K, BD-1080P, WEB-4K, WEB-1080P,
BluRay, REMUX, 蓝光, 4K-Remux, BD-Remux
```

### 分区选择（日常观影推荐）
| 分区 | 说明 | 推荐指数 |
|------|------|----------|
| **最新电影** | 近期新片，质量参差 | ⭐⭐⭐⭐ |
| **高清电影** | 蓝光压制，画质好 | ⭐⭐⭐⭐⭐ |
| **电视剧集** | 剧集打包 | ⭐⭐⭐⭐ |
| **高清剧集** | 高质量剧集 | ⭐⭐⭐⭐⭐ |
| **动漫专区** | 动画资源 | ⭐⭐⭐⭐ |
| **纪录综艺** | 纪录片/综艺 | ⭐⭐⭐ |

## ⚡ 批量下载工作流（剧集推荐）

当搜索结果包含多集（电视剧/动漫）时，**不要逐个点击**。用以下批量流程：

### 步骤 0：翻页收集所有结果（⚠️ 电视剧必须翻页！）

搜索结果最多4页。**第1页通常只有最新几集，早期集数在后续页面。**

```
# 检查是否有分页
browser_console(expression="document.querySelectorAll('a[href*=\"search-\"]').length")

# 遍历所有页面收集 BT 链接
for page in range(1, 5):
    url = "https://www.1lou.pro/search-{encoded}-1-{}.htm".format(page)
    # 提取该页的 BT 链接
```

### 步骤 A：JS 一次性提取所有 BT 链接

在搜索结果页面执行 JS，过滤掉网盘资源：

```javascript
const links = Array.from(document.querySelectorAll('li a[href*="thread-"]'));
const btLinks = links.filter(a => {
  const text = a.textContent;
  return text.includes('BT下载') && !text.includes('夸克') && !text.includes('网盘');
}).map(a => ({
  title: a.textContent.trim().substring(0, 80),
  url: a.href
}));
// 去重
const seen = new Set();
const unique = btLinks.filter(l => { if (seen.has(l.url)) return false; seen.add(l.url); return true; });
JSON.stringify(unique, null, 2);
```

返回格式：`[{ title: "...", url: "https://www.1lou.pro/thread-XXXXX.htm" }, ...]`

### 步骤 B：curl 批量提取种子 ID 并下载

用 `execute_code` + `terminal()` 批量处理：

```python
import re
from hermes_tools import terminal

episodes = [
    {"ep": 21, "url": "https://www.1lou.pro/thread-XXXXX.htm", "quality": "4K高码版"},
    {"ep": 20, "url": "https://www.1lou.pro/thread-YYYYY.htm", "quality": "4K高码版"},
    # ... 从步骤 A 的结果中选取高码版
]

for ep in episodes:
    # 从详情页提取 attach-download ID
    result = terminal("curl -sL '{}' | grep -oP 'attach-download-[0-9]+' | head -1".format(ep["url"]))
    attach_id = result.get("output", "").strip()
    if attach_id:
        torrent_url = "https://www.1lou.pro/{}.htm".format(attach_id)
        filename = "文件名_第{}集_{}.torrent".format(ep["ep"], ep["quality"])
        terminal('curl -sL -o "/opt/data/{}" "{}"'.format(filename, torrent_url))
```

**关键优势：** 全程不需要 `browser_click` 逐个进入详情页，速度快 5-10 倍。

### 步骤 C：验证所有种子 + 推送 qBittorrent（⚠️ 必须执行）

```python
# 1. 验证每个种子文件内容
for f in torrent_files:
    # 解析 bencode 提取 name 字段，确认是目标影片
    # 不对的立即删除重下

# 2. 登录 qBittorrent
terminal('curl -s -c /tmp/qb_cookies.txt --data "username=xxx&password=xxx" http://IP:8989/api/v2/auth/login')

# 3. 批量推送
for f in verified_files:
    terminal('curl -s -b /tmp/qb_cookies.txt -F "fileselect=@/opt/data/{}" -F "savepath=/data/downloads" http://IP:8989/api/v2/torrents/add'.format(f))
```

> ⚠️ **不要跳过验证直接推送！** 实测发现错误种子一旦加入 qBittorrent，删除后重新添加会返回 `Conflict`（hash 冲突），处理很麻烦。

## 🔤 字幕搜索工作流

下载完种子后，用户可能需要外挂中文字幕。以下是搜索字幕的标准流程：

### 搜索渠道优先级

| 渠道 | 网址 | 特点 |
|------|------|------|
| **射手网 API** | api.assrt.net | ✅ 最佳方案，API 免费，无需登录即可下载 |
| **SubDL** | subdl.com | 免费无需登录，但中文覆盖较少 |
| **射手网网页** | assrt.net | 需注册登录才能下载（HTTP 402） |
| **SubHD** | subhd.tv | 中文字幕质量高，需登录 |
| **字幕库** | zimuku.la | 中文字幕丰富，需登录 |

### 射手网 API（推荐）

射手网提供免费 API，无需登录即可搜索和下载字幕：

**API 端点：** `api.assrt.net`（不是 `assrt.net/api`）

```bash
# 搜索字幕
curl -sL 'https://api.assrt.net/v1/sub/search?token=TOKEN&q=Colony+2026&cnt=10'

# 获取字幕详情（含下载链接）
curl -sL 'https://api.assrt.net/v1/sub/detail?id=800132&token=TOKEN'

# 下载字幕文件
curl -sL -o subtitle.srt "http://file1.assrt.net/onthefly/800132/-/5/filename.srt?token=TOKEN"
```

**API 返回的字幕文件列表示例：**
- `*.chs.srt` — 简体中文 SRT
- `*.cht.srt` — 繁体中文 SRT
- `*.chs&eng.srt` — 简体+英文双语 SRT
- `*.chs.ass` — 简体中文 ASS（特效字幕）

**配额：** 20次/分钟（个人免费）

### 搜索步骤

1. **用英文名搜索** — 该站对英文名支持更好（如 "Colony 2026" 而非 "群体"）
2. **筛选中文字幕** — 在 SubDL 可用语言过滤器筛选 "Chinese"
3. **匹配版本** — 字幕需匹配视频版本（如 WEB-DL.x265.10bit vs WEB-DL.x264）
4. **下载格式** — 优先选 .srt（兼容性最好）

### 射手网网页版注意事项

- 需要**注册登录**才能下载（HTTP 402 = 未登录）
- 下载链接格式：`https://assrt.net/download/{id}/{filename}.zip`
- 页面是 XML+XSL 渲染，curl 无法直接解析，需用浏览器操作
- **推荐用 API 代替网页版**，更稳定且无需登录

### ⚠️ 字幕搜索常见问题

- 新片字幕较少，可能只有 AI 翻译版（质量一般）
- 字幕需匹配视频版本（分辨率、编码、来源），否则时间轴可能对不上
- 如果找不到中文字幕，可先用英文字幕凑合，或等字幕组更新

## 🔐 反爬保护处理

遇到 Cloudflare 等反爬保护的网站时，使用 Playwright + 反检测参数绕过：

```python
# Playwright 反检测启动参数
args = [
    '--disable-blink-features=AutomationControlled',
    '--ignore-certificate-errors',
]
# 注入 navigator.webdriver override
page.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
""")
```

**已验证有效的环境：**
- Playwright venv: `/opt/data/pmi_env`
- Chrome: `/opt/data/home/.agent-browser/browsers/chrome-150.0.7871.115/chrome`
- Xvfb: `:99`（headed 模式需要）

## 💡 经验总结

### 多集打包发布模式

电视剧/动漫早期集数常以**打包形式发布**（非单集），搜索时注意识别：

| 标题格式 | 含义 |
|----------|------|
| `第01-04集` | 4集打包 |
| `第07-09集` | 3集打包 |
| `第12-13集` | 2集打包 |
| `第14-15集` | 2集打包 |
| `第21集` | 单集 |

> 💡 **策略：** 先搜剧名翻页找全所有种子，优先选高码版（`HQ.WEB-DL`）打包种子，一次覆盖多集。单集发布通常从第10集左右开始。

### Ref ID 会变！
每次 `agent-browser open` 都是新进程，ref 全部重编号。同一页面的 ref 在同一个 terminal() 调用中有效，跨调用失效。

### 多集下载优先用批量流程
逐个 `browser_click` → `browser_snapshot` → 提取链接非常慢。对于电视剧/动漫等多集资源，**务必用「批量下载工作流」**（JS 提取 + curl 批量下载），不要手动逐集点击。单集电影才走逐步流程。

### 网盘资源的特征
网盘资源在搜索结果中标题通常以 `[夸克下载]` 开头，而且不包含 `.torrent` 附件。BT 资源标题通常含 `[BT下载]` 或分辨率+编码信息。

### 优先选 H265
同样 1080p，H265 体积只有 H264 的一半左右，日常观影首选。

### qBittorrent 注意
- 如果 qB 返回 `{"added_torrent_ids":["..."], "success_count":1}` 表示成功
- 返回 `Conflict` 表示种子已存在（hash 重复），不是错误
- 返回空响应 + HTTP 204 也表示成功（登录时常见）
- 如果遇到认证问题，重新登录获取 cookie
- **下载路径偏好：** `/downloads/整理前`（非默认 `/data/downloads/`）

### qBittorrent 修改下载路径（setLocation）

添加种子后可修改保存路径：

```bash
# 修改单个种子的保存路径
curl -s -b /tmp/qb_cookies.txt \
  -d "hashes=<torrent_hash>&location=/downloads/整理前" \
  "http://<qB主机IP>:8989/api/v2/torrents/setLocation"

# 批量修改多个种子
curl -s -b /tmp/qb_cookies.txt \
  -d "hashes=hash1|hash2|hash3&location=/downloads/整理前" \
  "http://<qB主机IP>:8989/api/v2/torrents/setLocation"
```

返回空响应 + HTTP 200 表示成功。可通过 `torrents/info` 获取 hash。

### 自动追剧：定时检查新集数

对于连载剧集，可设置 cron 任务自动检查新集数并下载。完整脚本示例见 `references/cron_episode_checker.py`。

核心逻辑：
1. 维护已下载集数列表（JSON 文件）
2. 每天搜索未下载的集数
3. 下载 → 验证 → 推送
4. 全部集数完成后自动删除 cron 任务

### ⚠️ 种子文件内容错误是常态，不是偶发

**实测发现：** 从搜索结果提取的 thread URL → attach-download ID 链路经常指向错误附件。这不是偶发 bug，而是该站点的已知问题。

**正确流程：下载 → 验证 → 推送**（三步缺一不可）
- 验证方法：解析 bencode 提取 `name` 字段
- 错误处理：删除错误文件 → 重新从 thread 页面提取 attach-download ID → 再验证
- 推送后发现错误：qBittorrent 中删除后重新添加会 `Conflict`（hash 冲突），必须重启 qB 或等 hash 过期

### 豆瓣信息辅助搜索（新片推荐）

对于新片，**先通过豆瓣获取详细信息**再搜索，效率更高：

1. 用豆瓣链接获取：英文名、年份、演员、类型
2. 用英文名/演员名在 BT 站搜索（该站对英文名支持更好）
3. 豆瓣链接格式：`https://movie.douban.com/subject/{id}/`

> 💡 示例：用户给了 `https://movie.douban.com/subject/37096700/` → 获取英文名 "Colony" → 用 "Colony 2026" 或 "全智贤" 搜索成功。

### 搜索无结果时的回退策略
站点搜索可能对中文全名、新片、小众影片返回空结果。**依次尝试以下回退**：

1. **拆词搜索**：去掉后缀，只搜核心词。如"功夫女足"→ 先搜"功夫"，再搜"女足"。

2. **英文名回退**：用 IMDb/豆瓣上的英文片名搜。如少林足球 → `Shaolin Soccer`、`KungFuSoccer`。站点公告明确提到"改用英文名搜"是常用策略。

3. **演员名回退**：搜中文名无结果时，**搜主演演员名**往往能找到。如"群体"搜不到 → 搜"全智贤"直接找到。这是该站的特殊行为，演员名关联比片名更可靠。

4. **中英文名交叉验证**：有些影片中英文名差异大（如"群体"英文名是"Colony"不是"The Group"）。搜索时需同时尝试多个英文名变体。

5. **切换搜索模式**：从"主题贴"（`-1.htm`）切到"所有贴"（`-0.htm`），覆盖帖子回复内容。

6. **繁简切换**：如果繁体无结果，试简体；反之亦然。

7. **⚠️ 何时停止**：如果以上 3-4 种关键词变体（中文全名、英文名、演员名、拆词、繁简）全部返回空结果，说明该片在本站 **没有 BT 种子资源**。直接告知用户并推荐其他渠道（网盘、PT站、其他BT站），不要无限循环尝试。

**URL 编码提示：** 中文关键词在 URL 中需要 percent-encoding。用 Python 快速生成：
```python
from urllib.parse import quote
print(quote("騎呢大狀"))  # → %E9%AA%91%E5%91%A2%E5%A4%A7%E7%8A%B6
```
