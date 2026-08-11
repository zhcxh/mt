# Thunderbird OAuth2 Client 限制

## Client ID
`9e5f94bc-e8a4-4e73-b8be-63364c29d753` (Thunderbird)

## 已验证的限制

| 功能 | 状态 | 说明 |
|------|------|------|
| Token 刷新 | ✅ | `acquire_token_by_refresh_token()` 正常 |
| Graph API `/me` | ❌ 403 | 不支持用户基本信息查询 |
| Graph API `/me/mailFolders` | ✅ | Mail.Read scope 可用 |
| Graph API `/me/messages` | ✅ | Mail.Read scope 可用 |
| IMAP XOAUTH2 | ❌ BAD | `AUTHENTICATE XOAUTH2` 命令失败 |
| Outlook REST API | ❌ 401 | Token 无法用于 REST API |

## 正确的 Scope

```python
# ✅ 正确 - 可以读邮件
SCOPES = ["https://graph.microsoft.com/Mail.Read"]

# ❌ 错误 - /me 端点 403
SCOPES = ["https://graph.microsoft.com/.default"]

# ❌ 错误 - IMAP scope 不支持
SCOPES = ["https://outlook.office365.com/IMAP.AccessAsUser.All"]
```

## Token 刷新流程

```python
import msal

app = msal.PublicClientApplication(CLIENT_ID, authority="https://login.microsoftonline.com/common")

# 1. 用 refresh_token 获取新 access_token
result = app.acquire_token_by_refresh_token(refresh_token, scopes=["https://graph.microsoft.com/Mail.Read"])

# 2. 如果成功，result 包含:
#    - access_token: 用于 API 调用
#    - refresh_token: 新的 refresh_token（如果旧的快过期）

# 3. 保存新 refresh_token 到 .env
```

## Device Code Flow 重新授权

当 refresh_token 过期（`invalid_grant` 错误）时：

```python
app = msal.PublicClientApplication(CLIENT_ID, authority="https://login.microsoftonline.com/common")
flow = app.initiate_device_flow(scopes=["https://graph.microsoft.com/Mail.Read"])

print(f"打开: {flow['verification_uri']}")
print(f"验证码: {flow['user_code']}")

# 等待用户在浏览器中完成授权
result = app.acquire_token_by_device_flow(flow)
# result['refresh_token'] → 保存到 .env
```

## 参考链接
- [Microsoft Graph Mail API](https://learn.microsoft.com/en-us/graph/api/resources/message)
- [OAuth 2.0 device code flow](https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-device-code-flow)
