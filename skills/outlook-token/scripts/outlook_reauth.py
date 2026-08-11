#!/usr/bin/env python3
"""
Device Code Flow — 重新授权获取新的 refresh_token。

运行后会显示一个 URL 和一个 code，用户在浏览器中：
1. 打开 URL
2. 输入 code
3. 登录并授权

脚本会自动轮询直到用户完成授权（最长15分钟），然后将新 token 写入 .env。
用法: python outlook_reauth.py
"""
import sys
import time
import msal

CLIENT_ID = "9e5f94bc-e8a4-4e73-b8be-63364c29d753"
SCOPES = ["https://graph.microsoft.com/.default"]
AUTHORITY = "https://login.microsoftonline.com/common"
ENV_PATH = "/opt/data/.env"

app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
flow = app.initiate_device_flow(scopes=SCOPES)

if "user_code" not in flow:
    print(f"❌ {flow.get('error_description','unknown')}")
    sys.exit(1)

code = flow["user_code"]
uri = flow["verification_uri"]
expires = flow.get("expires_in", 900)

print(f"CODE: {code}")
print(f"URL:  {uri}")
print(f"EXPIRES_IN: {expires}s")
print("WAITING...")

start = time.time()
while time.time() - start < expires:
    result = app.acquire_token_by_device_flow(flow)
    if "access_token" in result:
        rt = result.get("refresh_token", "")
        email = result.get("id_token_claims", {}).get("preferred_username", "")
        print(f"\nSUCCESS|{email}|{rt}")

        lines = []
        try:
            with open(ENV_PATH) as f:
                for line in f:
                    s = line.strip()
                    if s.startswith("outlook_refresh_token"):
                        lines.append(f'outlook_refresh_token="{rt}"')
                    elif s.startswith("outlook_client_id"):
                        lines.append(f'outlook_client_id="{CLIENT_ID}"')
                    elif s.startswith("outlook_email"):
                        lines.append(f'outlook_email="{email}"')
                    else:
                        lines.append(s)
        except FileNotFoundError:
            pass
        keys = "\n".join(lines)
        if "outlook_refresh_token" not in keys:
            lines.append(f'outlook_refresh_token="{rt}"')
        if "outlook_client_id" not in keys:
            lines.append(f'outlook_client_id="{CLIENT_ID}"')
        if "outlook_email" not in keys:
            lines.append(f'outlook_email="{email}"')
        with open(ENV_PATH, "w") as f:
            f.write("\n".join(lines) + "\n")
        print(f"SAVED: {ENV_PATH}")
        sys.exit(0)

    err = result.get("error", "")
    if err == "authorization_pending":
        elapsed = int(time.time() - start)
        remaining = expires - elapsed
        print(f"PENDING|{remaining}s left")
        time.sleep(8)
    else:
        print(f"ERROR|{err}|{result.get('error_description', '')}")
        sys.exit(1)

print("TIMEOUT")
sys.exit(1)
