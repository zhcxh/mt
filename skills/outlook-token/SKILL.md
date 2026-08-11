---
name: outlook-token
description: "Outlook OAuth2 免密收件：用 refresh_token 自动刷新 access_token，通过 Microsoft Graph API 收发邮件，无需浏览器登录。"
version: 1.1.0
author: hermes-agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Email, Outlook, OAuth2, Token, Microsoft Graph]
prerequisites:
  commands: [python3]
  python_packages: [msal, requests]
---

# Outlook Token Email Client

使用 OAuth2 refresh_token 自动获取 access_token，通过 Microsoft Graph API 操作 Outlook 邮箱。**完全无需浏览器、无需密码登录**。

## 前置条件

1. **Azure AD App Registration**（client_id + refresh_token）
2. Python venv 已安装 `msal` 和 `requests`

### 安装依赖

**推荐用 `pmi_env`** — 已配置好 Playwright + Chrome，可同时用于浏览器相关操作。

```bash
cd /opt/data && source pmi_env/bin/activate
pip install --target pmi_env/lib/python3.13/site-packages msal requests
```

**Pitfall：** msal 有时 pip install 不写入正确的 site-packages，必须用 `--target` 强制安装到 venv 目录。

**Pitfall：** `outlook_env` 仅包含 msal + requests，无 Playwright。如果需要浏览器操作（如 device code flow），必须用 pmi_env。

## 配置文件 (.env)

在 `/opt/data/.env` 中添加以下变量：

```env
outlook_email="your@email.com"
outlook_password="unused"
outlook_client_id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
outlook_refresh_token="0.AXYA..."
```

### 获取 refresh_token

1. 在 Azure Portal → App registrations → 注册应用
2. 配置 redirect URI（可用 http://localhost）
3. 授权权限：`Mail.Read`, `Mail.ReadWrite`, `Mail.Send`, `offline_access`
4. 用 device code flow 或 auth code flow 获取初始 refresh_token
5. refresh_token 有效期约 90 天，脚本会自动刷新

### Venv 注意事项

- **推荐用 `pmi_env`** — 已配置好 Playwright + Chrome，可同时用于浏览器相关操作
- `outlook_env` 仅包含 msal + requests，无 Playwright
- 如果在 outlook_env 中需要 Playwright，需额外 `pip install playwright`
- msal 有时 pip install 不写入正确的 site-packages，可用 `pip install --target pmi_env/lib/python3.13/site-packages msal` 强制安装

## 用法

**推荐脚本：** `/opt/data/skills/email/outlook-token/scripts/outlook_email.py`

统一入口脚本，支持所有操作：

```bash
source /opt/data/pmi_env/bin/activate
SCRIPT="/opt/data/skills/email/outlook-token/scripts/outlook_email.py"
```

### 快速命令

```bash
# 测试连接
python $SCRIPT test

# 列出收件箱（默认20封）
python $SCRIPT list
python $SCRIPT list -n 50                     # 50封
python $SCRIPT list -f sent                   # 已发送
python $SCRIPT list -f junk                   # 垃圾邮件

# 读取邮件（支持序号或ID）
python $SCRIPT read 1                         # 读最新一封
python $SCRIPT read 3                         # 读第3封
python $SCRIPT read <full-message-id>         # 用真实ID

# 搜索邮件
python $SCRIPT search "AWS"
python $SCRIPT search "verification" -n 10

# 获取验证码（自动提取6位数字）
python $SCRIPT code                           # 最新验证码
python $SCRIPT code -s "AWS"                  # 搜索AWS邮件中的验证码
python $SCRIPT code -n 5                      # 从最近5封中提取

# 刷新Token
python $SCRIPT refresh

# 列出文件夹
python $SCRIPT folders
```

### 获取验证码（最常用）

在注册/登录流程中自动获取邮箱验证码：

```bash
# 获取最新验证码
python $SCRIPT code

# 搜索特定发件人的验证码
python $SCRIPT code -s "no-reply@verify.signin.aws"

# 指定搜索数量
python $SCRIPT code -n 10
```

**⚠️ Pitfall: 验证码有效期10分钟，获取后请立即使用**

### 读取邮件

```bash
# 用序号读取（推荐）
python $SCRIPT read 1
python $SCRIPT read 2

# 用真实ID读取
python $SCRIPT read "AAMkAD..."

# 输出JSON格式
python $SCRIPT read 1 --json
```

### 搜索邮件

```bash
python $SCRIPT search "AWS"
python $SCRIPT search "verification" -f inbox
python $SCRIPT search "code" -n 50
```

### 附件操作

```bash
python $SCRIPT attachments 1                  # 列出第1封邮件的附件
python $SCRIPT download 1                     # 下载附件
```

## Token 自动刷新

脚本每次调用时会自动用 refresh_token 获取新的 access_token。
如果 refresh_token 过期，会报错并提示需要重新授权。

**refresh_token 刷新策略：**
- 每次调用 `get_access_token()` 时自动刷新
- 新的 refresh_token 会自动写回 .env 文件
- 无需手动干预

## API 权限要求

本技能使用 Thunderbird 的公共 OAuth2 应用，无需自行配置权限。

**正确的 Scope：**
```python
SCOPES = ["https://graph.microsoft.com/Mail.Read"]  # ✅ 唯一可用的
```

> ⚠️ 不要使用 `.default` scope，会导致 `/me` 端点 403。

## 已知限制

本技能使用 Thunderbird 的公共 OAuth2 client_id，有以下限制：
- ❌ `/me` 端点返回 403
- ❌ IMAP XOAUTH2 认证失败
- ✅ `/me/mailFolders` 和 `/me/messages` 正常（Mail.Read scope）

详细限制列表见 `references/thunderbird-client-limits.md`。

## 常见问题

### Token 过期怎么办？

**症状：** `refresh_access_token()` 返回 `invalid_grant` (AADSTS70000)

**解决：** 运行 device code flow 脚本重新授权：

```bash
source /opt/data/pmi_env/bin/activate
python /opt/data/skills/email/outlook-token/scripts/outlook_reauth_simple.py
```

脚本会：
1. 显示验证码和 URL → 在浏览器打开 `https://login.microsoft.com/device`
2. 输入验证码 → 登录 → 授权
3. 自动将新 refresh_token 写入 `/opt/data/.env`

**Pitfall：** refresh_token 有效期约 90 天。每次 `outlook_token.py` 调用会自动刷新，但如果长期未用（>90天）会过期，必须重新走 device code flow。

**Pitfall：** device code flow 需要用户在浏览器中手动操作（输入验证码+登录），agent 无法自动化这一步。Microsoft 的 device auth 页面会多次重定向（`deviceauth?sso_reload=true`），Playwright 自动化会因找不到元素而失败。

**Pitfall：** Playwright 浏览器自动化需要 X server。如果报 `Missing X server or $DISPLAY`，需先启动 Xvfb：`Xvfb :99 -screen 0 1920x1080x24 &`，然后设置 `DISPLAY=:99`。

**Pitfall：** 用 `reauth_simple.py`（简单轮询方式）比 `outlook_reauth_browser.py`（浏览器自动化方式）更可靠。浏览器自动化在 Microsoft 登录流程中经常因页面重定向而失败。

**Pitfall：** device code 有效期约 15 分钟，发起后应立即告知用户操作，不要等待。

### 邮箱地址不一致？
确保 .env 中的 `outlook_email` 与 Azure AD 中注册的一致。

### 权限不足？
确保 App Registration 中已添加 `Mail.Read` 等权限并获得管理员同意。

## 脚本结构

```
skills/email/outlook-token/
├── SKILL.md                    # 本文件
├── references/
│   ├── thunderbird-client-limits.md  # Thunderbird client 限制详情
│   └── auto-verification-codes.md    # 自动获取验证码模式
└── scripts/
    ├── outlook_email.py        # ⭐ 推荐：统一入口（list/read/search/code/test/refresh）
    ├── outlook_token.py        # 旧版核心脚本
    ├── outlook_reauth_simple.py # Device Code Flow（推荐，简单轮询）
    ├── outlook_reauth.py       # Device Code Flow（旧版）
    └── outlook_reauth_browser.py  # 浏览器自动化版（不推荐，易失败）
```

**推荐使用 `outlook_email.py`**，它是统一入口脚本，支持：
- `list` — 列出邮件（支持序号）
- `read` — 读取邮件（支持序号或ID）
- `search` — 搜索邮件（客户端过滤，避免400错误）
- `code` — 自动提取验证码
- `test` — 测试连接
- `refresh` — 刷新Token
- `attachments` / `download` — 附件操作

## 自动获取验证码（注册流程集成）

在 Web 注册/登录流程中，可以用 Outlook API 自动获取邮箱验证码，无需手动查看邮箱。详见 `references/auto-verification-codes.md`。

## 依赖

- Python 3.8+
- `msal` — Microsoft Authentication Library
- `requests` — HTTP 客户端
