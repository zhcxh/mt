#!/usr/bin/env python3
"""
Simple device code flow — 等用户手动在浏览器完成授权。
推荐使用此脚本而非 outlook_reauth_browser.py（后者因 Microsoft 页面重定向经常失败）。

用法:
    python outlook_reauth_simple.py

运行后显示验证码和 URL，用户在浏览器中打开 URL → 输入验证码 → 登录 → 授权。
脚本自动轮询等待授权完成，新 token 自动写入 .env。
"""
import sys, time, msal

CLIENT_ID = "9e5f94bc-e8a4-4e73-b8be-63364c29d753"
SCOPES = ["https://graph.microsoft.com/Mail.Read"]
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

# Poll until user completes or timeout
start = time.time()
while time.time() - start < expires:
    result = app.acquire_token_by_device_flow(flow)
    if "access_token" in result:
        rt = result.get("refresh_token","")
        email = result.get("id_token_claims",{}).get("preferred_username","")
        print(f"\nSUCCESS|{email}|{rt}")
        
        # Save to .env
        lines = []
        try:
            with open(ENV_PATH) as f:
                for line in f:
                    s = line.strip()
                    if s.startswith("outlook_refresh_token"): lines.append(f'outlook_refresh_token="{rt}"')
                    elif s.startswith("outlook_client_id"): lines.append(f'outlook_client_id="{CLIENT_ID}"')
                    elif s.startswith("outlook_email"): lines.append(f'outlook_email="{email}"')
                    else: lines.append(s)
        except: pass
        keys = "\n".join(lines)
        if "outlook_refresh_token" not in keys: lines.append(f'outlook_refresh_token="{rt}"')
        if "outlook_client_id" not in keys: lines.append(f'outlook_client_id="{CLIENT_ID}"')
        if "outlook_email" not in keys: lines.append(f'outlook_email="{email}"')
        with open(ENV_PATH,"w") as f: f.write("\n".join(lines)+"\n")
        print(f"SAVED: {ENV_PATH}")
        sys.exit(0)
    
    err = result.get("error","")
    if err == "authorization_pending":
        elapsed = int(time.time() - start)
        remaining = expires - elapsed
        print(f"PENDING|{remaining}s left")
        time.sleep(8)
    else:
        print(f"ERROR|{err}|{result.get('error_description','')}")
        sys.exit(1)

print("TIMEOUT")
sys.exit(1)
