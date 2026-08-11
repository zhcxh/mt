#!/usr/bin/env python3
"""
从 Outlook 邮箱自动获取最新验证码（AWS/PMI/其他服务）。
用法: python outlook_verify_code.py [sender_filter] [code_length]
示例: python outlook_verify_code.py aws 6
      python outlook_verify_code.py pmi 6
      python outlook_verify_code.py          # 最新邮件中的6位码
"""
import os, sys, re, requests, msal

def get_token():
    env = {}
    with open('/opt/data/.env') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    app = msal.PublicClientApplication(
        env['outlook_client_id'],
        authority='https://login.microsoftonline.com/common'
    )
    result = app.acquire_token_by_refresh_token(
        env['outlook_refresh_token'],
        scopes=['https://graph.microsoft.com/Mail.Read']
    )
    return {'Authorization': f"Bearer {result['access_token']}"}

def find_code(sender_filter=None, code_len=6):
    headers = get_token()
    params = {
        '$top': 10,
        '$orderby': 'receivedDateTime desc',
        '$select': 'id,subject,from,receivedDateTime,bodyPreview,body'
    }
    resp = requests.get(
        'https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages',
        headers=headers, params=params
    )
    resp.raise_for_status()
    messages = resp.json().get('value', [])

    for msg in messages:
        sender = msg.get('from', {}).get('emailAddress', {}).get('address', '')
        if sender_filter and sender_filter.lower() not in sender.lower():
            continue
        html = msg['body']['content']
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text)
        codes = re.findall(rf'(\d{{{code_len}}})', text)
        if codes:
            print(f"📧 From: {sender}")
            print(f"📅 Date: {msg['receivedDateTime']}")
            print(f"🔑 Code: {codes[0]}")
            return codes[0]
    print("❌ No verification code found")
    return None

if __name__ == '__main__':
    sender = sys.argv[1] if len(sys.argv) > 1 else None
    length = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    find_code(sender, length)
