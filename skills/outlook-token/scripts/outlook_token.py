#!/usr/bin/env python3
"""
Outlook Token Email Client — 免密免登录，使用 OAuth2 token 收发邮件。

用法:
  python outlook_token.py list [--folder inbox|sent|drafts|junk|deleted] [--limit N]
  python outlook_token.py read <message-id>
  python outlook_token.py search <query> [--folder FOLDER]
  python outlook_token.py folders
  python outlook_token.py save <message-id> [--output DIR]
  python outlook_token.py refresh          # 手动刷新 token 并保存
  python outlook_token.py test             # 测试连接
  python outlook_token.py raw <message-id> # 输出原始 MIME

环境变量 (.env 文件):
  outlook_email          邮箱地址
  outlook_password       密码（备用，本脚本不用）
  outlook_client_id      Azure AD Application (client) ID
  outlook_refresh_token  OAuth2 Refresh Token

Token 刷新流程:
  1. 首先尝试用 refresh_token 换取新 access_token
  2. 如果 refresh_token 过期，自动用 client_secret 重新授权（需用户介入）
  3. 新 token 自动写回 .env 文件
"""

import os
import sys
import json
import base64
import imaplib
import email
import email.header
import email.utils
from email.mime.text import MIMEText
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlencode

try:
    import msal
except ImportError:
    print("[ERROR] msal not installed. Run: pip install msal", file=sys.stderr)
    sys.exit(1)

try:
    import requests
except ImportError:
    print("[ERROR] requests not installed. Run: pip install requests", file=sys.stderr)
    sys.exit(1)

# ─── Config ──────────────────────────────────────────────────────────────────

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
AUTHORITY = "https://login.microsoftonline.com/common"
SCOPES = ["https://graph.microsoft.com/Mail.Read"]
# IMAP/SMTP OAuth2 scopes
IMAP_SCOPES = ["https://outlook.office365.com/.default"]

def find_env_file():
    """Find .env file: same dir as script → cwd → parent dirs."""
    candidates = [
        Path(__file__).parent / ".env",
        Path.cwd() / ".env",
        Path.home() / ".env",
        Path("/opt/data/.env"),
    ]
    for p in candidates:
        if p.exists():
            return p
    return None

def load_env(env_path=None):
    """Load .env file into os.environ. Returns dict of outlook_* vars."""
    if env_path:
        p = Path(env_path)
    else:
        p = find_env_file()
    if not p or not p.exists():
        print(f"[WARN] No .env file found", file=sys.stderr)
        return {}
    
    config = {}
    with open(p) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key.startswith("outlook_"):
                    config[key] = val
                    os.environ[key] = val
    print(f"[ENV] Loaded from {p}", file=sys.stderr)
    return config

def save_env(config, env_path=None):
    """Update outlook_* vars in .env file."""
    if env_path:
        p = Path(env_path)
    else:
        p = find_env_file()
    if not p:
        p = Path("/opt/data/.env")
    
    lines = []
    updated_keys = set()
    if p.exists():
        with open(p) as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith("outlook_") and "=" in stripped:
                    key = stripped.split("=", 1)[0].strip()
                    if key in config:
                        lines.append(f'{key}="{config[key]}"')
                        updated_keys.add(key)
                    else:
                        lines.append(stripped)
                else:
                    lines.append(stripped)
    
    # Append new keys
    for key, val in config.items():
        if key not in updated_keys:
            lines.append(f'{key}="{val}"')
    
    with open(p, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[ENV] Saved to {p}", file=sys.stderr)


# ─── Token Management ────────────────────────────────────────────────────────

class OutlookClient:
    """Microsoft Graph + IMAP OAuth2 client for Outlook."""
    
    def __init__(self, config=None):
        self.config = config or load_env()
        self.email = self.config.get("outlook_email", "")
        self.client_id = self.config.get("outlook_client_id", "")
        self.refresh_token = self.config.get("outlook_refresh_token", "")
        self.access_token = None
        self._msal_app = None
    
    @property
    def msal_app(self):
        if self._msal_app is None:
            self._msal_app = msal.PublicClientApplication(
                self.client_id,
                authority=AUTHORITY,
            )
        return self._msal_app
    
    def refresh_access_token(self):
        """Refresh OAuth2 access token using refresh_token."""
        if not self.refresh_token:
            print("[ERROR] No refresh_token available", file=sys.stderr)
            return False
        
        print("[TOKEN] Refreshing access token...", file=sys.stderr)
        result = self.msal_app.acquire_token_by_refresh_token(
            self.refresh_token,
            scopes=SCOPES,
        )
        
        if "access_token" in result:
            self.access_token = result["access_token"]
            # Update refresh_token if new one provided
            if "refresh_token" in result:
                self.refresh_token = result["refresh_token"]
                self.config["outlook_refresh_token"] = self.refresh_token
                save_env(self.config)
            print("[TOKEN] ✅ Access token refreshed", file=sys.stderr)
            return True
        else:
            err = result.get("error", "unknown")
            desc = result.get("error_description", "")
            print(f"[TOKEN] ❌ Refresh failed: {err} — {desc}", file=sys.stderr)
            return False
    
    def get_access_token(self):
        """Get a valid access token, refreshing if needed."""
        if self.access_token:
            return self.access_token
        if self.refresh_access_token():
            return self.access_token
        return None
    
    def graph_headers(self):
        """Return headers for Microsoft Graph API calls."""
        token = self.get_access_token()
        if not token:
            raise RuntimeError("Cannot obtain access token")
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
    
    def graph_get(self, endpoint, params=None):
        """GET request to Microsoft Graph API."""
        url = f"{GRAPH_BASE}{endpoint}"
        resp = requests.get(url, headers=self.graph_headers(), params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    
    def graph_get_raw(self, endpoint, params=None):
        """GET request returning raw response."""
        url = f"{GRAPH_BASE}{endpoint}"
        resp = requests.get(url, headers=self.graph_headers(), params=params, timeout=30)
        resp.raise_for_status()
        return resp
    
    # ─── IMAP Operations ──────────────────────────────────────────────────
    
    def imap_connect(self):
        """Connect to Outlook IMAP using XOAUTH2."""
        token = self.get_access_token()
        if not token:
            raise RuntimeError("Cannot obtain access token for IMAP")
        
        # Build XOAUTH2 auth string
        auth_string = f"user={self.email}\x01auth=Bearer {token}\x01\x01"
        auth_bytes = base64.b64encode(auth_string.encode("utf-8")).decode("ascii")
        
        imap = imaplib.IMAP4_SSL("outlook.office365.com", 993)
        
        # XOAUTH2 authentication
        imap.authenticate("XOAUTH2", lambda x: auth_bytes.encode("utf-8"))
        print("[IMAP] ✅ Connected via XOAUTH2", file=sys.stderr)
        return imap
    
    # ─── Email Operations ─────────────────────────────────────────────────
    
    def list_folders(self):
        """List all mail folders."""
        data = self.graph_get("/me/mailFolders", params={"$top": 100})
        folders = data.get("value", [])
        for f in folders:
            print(f"  {f['displayName']:30s}  id={f['id'][:20]}... unread={f.get('unreadItemCount', 0)}")
        return folders
    
    def list_messages(self, folder="inbox", limit=20):
        """List messages in a folder."""
        folder_id = self._resolve_folder(folder)
        endpoint = f"/me/mailFolders/{folder_id}/messages"
        params = {
            "$top": limit,
            "$orderby": "receivedDateTime desc",
            "$select": "id,subject,from,receivedDateTime,isRead,importance,hasAttachments,bodyPreview",
        }
        data = self.graph_get(endpoint, params)
        messages = data.get("value", [])
        
        for i, msg in enumerate(messages, 1):
            from_name = msg.get("from", {}).get("emailAddress", {}).get("name", "?")
            from_addr = msg.get("from", {}).get("emailAddress", {}).get("address", "?")
            subject = msg.get("subject", "(no subject)")
            dt = msg.get("receivedDateTime", "")
            read = "✅" if msg.get("isRead") else "🔴"
            preview = (msg.get("bodyPreview", "") or "")[:60]
            print(f"{read} [{i}] {dt[:16]}  {from_name} <{from_addr}>")
            print(f"   📌 {subject}")
            if preview:
                print(f"   💬 {preview}...")
            print()
        
        return messages
    
    def read_message(self, message_id):
        """Read a single message by ID."""
        endpoint = f"/me/messages/{message_id}"
        params = {
            "$select": "id,subject,from,toRecipients,ccRecipients,receivedDateTime,isRead,importance,hasAttachments,body,internetMessageId,conversationId"
        }
        msg = self.graph_get(endpoint, params)
        
        from_name = msg.get("from", {}).get("emailAddress", {}).get("name", "?")
        from_addr = msg.get("from", {}).get("emailAddress", {}).get("address", "?")
        to_list = [r.get("emailAddress", {}).get("address", "?") for r in msg.get("toRecipients", [])]
        cc_list = [r.get("emailAddress", {}).get("address", "") for r in msg.get("ccRecipients", [])]
        subject = msg.get("subject", "(no subject)")
        dt = msg.get("receivedDateTime", "")
        importance = msg.get("importance", "normal")
        body_html = msg.get("body", {}).get("content", "")
        body_type = msg.get("body", {}).get("contentType", "Text")
        
        print(f"{'='*60}")
        print(f"From:    {from_name} <{from_addr}>")
        print(f"To:      {', '.join(to_list)}")
        if cc_list:
            print(f"CC:      {', '.join(cc_list)}")
        print(f"Date:    {dt}")
        print(f"Subject: {subject}")
        if importance != "normal":
            print(f"⚠️  Priority: {importance}")
        print(f"{'='*60}")
        
        if body_type == "HTML":
            # Strip HTML tags for terminal display (basic)
            import re
            text = re.sub(r'<br\s*/?>', '\n', body_html)
            text = re.sub(r'<[^>]+>', '', text)
            text = re.sub(r'&nbsp;', ' ', text)
            text = re.sub(r'&amp;', '&', text)
            text = re.sub(r'&lt;', '<', text)
            text = re.sub(r'&gt;', '>', text)
            text = text.strip()
        else:
            text = body_html
        
        print(text)
        print(f"{'='*60}")
        return msg
    
    def search_messages(self, query, folder=None, limit=20):
        """Search messages using Graph API search."""
        if folder:
            folder_id = self._resolve_folder(folder)
            endpoint = f"/me/mailFolders/{folder_id}/messages"
        else:
            endpoint = "/me/messages"
        
        params = {
            "$top": limit,
            "$filter": f"contains(subject, '{query}') or contains(bodyPreview, '{query}')",
            "$orderby": "receivedDateTime desc",
            "$select": "id,subject,from,receivedDateTime,isRead,bodyPreview",
        }
        data = self.graph_get(endpoint, params)
        messages = data.get("value", [])
        
        if not messages:
            print(f"🔍 No results for '{query}'")
            return []
        
        print(f"🔍 Found {len(messages)} results for '{query}':\n")
        for i, msg in enumerate(messages, 1):
            from_name = msg.get("from", {}).get("emailAddress", {}).get("name", "?")
            subject = msg.get("subject", "(no subject)")
            dt = msg.get("receivedDateTime", "")
            read = "✅" if msg.get("isRead") else "🔴"
            print(f"{read} [{i}] {dt[:16]}  {from_name}")
            print(f"   📌 {subject}")
            print(f"   id: {msg['id']}")
            print()
        
        return messages
    
    def get_attachments(self, message_id):
        """List and download attachments from a message."""
        endpoint = f"/me/messages/{message_id}/attachments"
        data = self.graph_get(endpoint)
        attachments = data.get("value", [])
        
        if not attachments:
            print("📎 No attachments")
            return []
        
        print(f"📎 {len(attachments)} attachment(s):")
        for att in attachments:
            name = att.get("name", "unknown")
            size = att.get("size", 0)
            content_type = att.get("contentType", "?")
            print(f"  📄 {name} ({size} bytes, {content_type})")
        
        return attachments
    
    def download_attachment(self, message_id, attachment_id, output_dir="."):
        """Download a specific attachment."""
        endpoint = f"/me/messages/{message_id}/attachments/{attachment_id}"
        att = self.graph_get(endpoint)
        
        name = att.get("name", "attachment")
        content_bytes = att.get("contentBytes", "")
        
        if content_bytes:
            data = base64.b64decode(content_bytes)
            out_path = Path(output_dir) / name
            out_path.write_bytes(data)
            print(f"✅ Saved: {out_path} ({len(data)} bytes)")
            return str(out_path)
        else:
            print("❌ No content bytes in attachment")
            return None
    
    def get_raw_mime(self, message_id):
        """Get raw MIME content of a message."""
        endpoint = f"/me/messages/{message_id}"
        params = {"$select": "internetMessageHeaders"}
        resp = self.graph_get_raw(endpoint, params)
        return resp.text
    
    def test_connection(self):
        """Test Graph API connection via mail folders."""
        try:
            data = self.graph_get("/me/mailFolders", params={"$top": 1})
            folders = data.get("value", [])
            if folders:
                print(f"✅ Connected! Found {len(folders)}+ folders")
                return True
            else:
                print("❌ Connected but no folders found")
                return False
        except Exception as e:
            print(f"❌ Connection failed: {e}", file=sys.stderr)
            return False
    
    # ─── Helpers ──────────────────────────────────────────────────────────
    
    def _resolve_folder(self, name):
        """Resolve folder name to ID."""
        common = {
            "inbox": "inbox",
            "sent": "sentitems",
            "sentitems": "sentitems",
            "drafts": "drafts",
            "junk": "junkemail",
            "junkemail": "junkemail",
            "deleted": "deleteditems",
            "deleteditems": "deleteditems",
            "archive": "archive",
        }
        name_lower = name.lower()
        if name_lower in common:
            return common[name_lower]
        # Try to find by display name
        folders = self.list_folders()
        for f in folders:
            if f["displayName"].lower() == name_lower:
                return f["id"]
        # Default to inbox
        print(f"[WARN] Folder '{name}' not found, using inbox", file=sys.stderr)
        return "inbox"


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Outlook Token Email Client")
    parser.add_argument("command", choices=["list", "read", "search", "folders", "save", "refresh", "test", "raw"],
                        help="Command to execute")
    parser.add_argument("target", nargs="?", help="Message ID or search query")
    parser.add_argument("--folder", "-f", default="inbox", help="Mail folder")
    parser.add_argument("--limit", "-n", type=int, default=20, help="Number of messages")
    parser.add_argument("--output", "-o", default=".", help="Output directory")
    parser.add_argument("--env", help="Path to .env file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    # Load config
    config = load_env(args.env)
    client = OutlookClient(config)
    
    if args.command == "test":
        client.test_connection()
    
    elif args.command == "refresh":
        if client.refresh_access_token():
            save_env(client.config, args.env)
            print("✅ Token refreshed and saved")
        else:
            print("❌ Token refresh failed", file=sys.stderr)
            sys.exit(1)
    
    elif args.command == "folders":
        client.list_folders()
    
    elif args.command == "list":
        msgs = client.list_messages(args.folder, args.limit)
        if args.json:
            print(json.dumps(msgs, indent=2, default=str))
    
    elif args.command == "read":
        if not args.target:
            print("❌ Need message ID", file=sys.stderr)
            sys.exit(1)
        client.read_message(args.target)
    
    elif args.command == "search":
        if not args.target:
            print("❌ Need search query", file=sys.stderr)
            sys.exit(1)
        msgs = client.search_messages(args.target, args.folder, args.limit)
        if args.json:
            print(json.dumps(msgs, indent=2, default=str))
    
    elif args.command == "save":
        if not args.target:
            print("❌ Need message ID", file=sys.stderr)
            sys.exit(1)
        client.get_attachments(args.target)
    
    elif args.command == "raw":
        if not args.target:
            print("❌ Need message ID", file=sys.stderr)
            sys.exit(1)
        print(client.get_raw_mime(args.target))


if __name__ == "__main__":
    main()
