# Auto-Fetching Verification Codes from Outlook

During web registration/login flows, AWS and other services send 6-digit verification codes via email. This reference documents how to automatically retrieve these codes using the Outlook Token API.

## Pattern: Fetch Latest Verification Code

```python
import msal, requests, re

CLIENT_ID = "9e5f94bc-e8a4-4e73-b8be-63364c29d753"

app = msal.PublicClientApplication(CLIENT_ID, authority="https://login.microsoftonline.com/common")
with open("/opt/data/.env") as f:
    for line in f:
        if line.startswith("outlook_refresh_token"):
            rt = line.split("=", 1)[1].strip().strip('"')

result = app.acquire_token_by_refresh_token(rt, scopes=["https://graph.microsoft.com/Mail.Read"])
token = result["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get latest 3 emails from inbox
r = requests.get(
    "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages?"
    "$top=3&$orderby=receivedDateTime%20desc&$select=subject,body",
    headers=headers, timeout=10
)

for msg in r.json().get("value", []):
    body = msg.get("body", {}).get("content", "")
    codes = re.findall(r'\b(\d{6})\b', body)
    if codes:
        # Filter out placeholder codes (555555 is AWS placeholder)
        real_codes = [c for c in codes if c != "555555"]
        if real_codes:
            print(f"Latest code: {real_codes[0]}")
            break
```

## AWS-Specific Notes

- AWS verification emails come from `no-reply@signup.aws` or `no-reply@verify.signin.aws`
- Subject lines: "Verify your email address", "Verify your identity", "Sign up for AWS - Email Verification"
- The 6-digit code is in the email body, often after "Verification code" text
- Code `555555` is a placeholder in AWS emails — always filter it out
- Codes expire in 10 minutes
- Multiple codes may exist if user triggered multiple sign-up attempts — always use the LATEST

## Integration with Playwright Registration Scripts

```python
async def get_latest_code():
    """Get latest verification code from Outlook (async wrapper)."""
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _fetch_code_sync)

# In registration script:
code = await get_latest_code()
if code:
    await page.fill("input[name='code']", code)
    await page.click("button:has-text('Verify')")
```

## Pitfalls

- **bodyPreview truncation**: The `bodyPreview` field may be truncated and not contain the code. Use `body.content` instead (full HTML body).
- **Race condition**: Email may not arrive immediately. Add `await asyncio.sleep(10)` before first fetch, then retry.
- **Token refresh overhead**: Each code fetch refreshes the access token. Cache the token if fetching multiple times in quick succession.
- **Multiple inboxes**: If the account has rules that move emails, search across folders, not just INBOX.
