#!/usr/bin/env python3
"""
Outlook Token Email Client — 统一入口，免密免登录。

用法:
  python outlook_email.py list [--folder FOLDER] [--limit N]
  python outlook_email.py read <序号|message-id>
  python outlook_email.py search <query> [--folder FOLDER]
  python outlook_email.py code [--search KEYWORD] [--limit N]
  python outlook_email.py folders
  python outlook_email.py test
  python outlook_email.py refresh
  python outlook_email.py attachments <序号|message-id>
  python outlook_email.py download <序号|message-id>

环境变量 (.env 文件):
  outlook_email          邮箱地址
  outlook_client_id      Azure AD Application (client) ID
  outlook_refresh_token  OAuth2 Refresh Token
"""

import os
import sys
import re
import json
import base64
from pathlib import Path
from datetime import datetime, timezone

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

FOLDER_MAP = {
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


def find_env_file():
    candidates = [
        Path("/opt/data/.env"),
        Path(__file__).parent / ".env",
        Path.cwd() / ".env",
        Path.home() / ".env",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def load_env(env_path=None):
    p = Path(env_path) if env_path else find_env_file()
    if not p or not p.exists():
        print("[WARN] No .env file found", file=sys.stderr)
        return {}
    config = {}
    with open(p) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key.startswith("outlook_"):
                config[key] = val
    print(f"[ENV] Loaded from {p}", file=sys.stderr)
    return config


def save_env(config, env_path=None):
    p = Path(env_path) if env_path else find_env_file()
    if not p:
        p = Path("/opt/data/.env")
    lines = []
    updated = set()
    if p.exists():
        with open(p) as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith("outlook_") and "=" in stripped:
                    k = stripped.split("=", 1)[0].strip()
                    if k in config:
                        lines.append(f'{k}="{config[k]}"')
                        updated.add(k)
                    else:
                        lines.append(stripped)
                else:
                    lines.append(stripped)
    for k, v in config.items():
        if k not in updated:
            lines.append(f'{k}="{v}"')
    with open(p, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[ENV] Saved to {p}", file=sys.stderr)


# ─── Client ──────────────────────────────────────────────────────────────────

class OutlookClient:
    def __init__(self, config=None):
        self.config = config or load_env()
        self.client_id = self.config.get("outlook_client_id", "")
        self.refresh_token = self.config.get("outlook_refresh_token", "")
        self.access_token = None
        self._msal_app = None
        self._cached_messages = []  # 缓存列表结果供 read(N) 使用

    @property
    def msal_app(self):
        if self._msal_app is None:
            self._msal_app = msal.PublicClientApplication(self.client_id, authority=AUTHORITY)
        return self._msal_app

    def _refresh_token(self):
        if not self.refresh_token:
            print("[ERROR] No refresh_token in .env", file=sys.stderr)
            return False
        print("[TOKEN] Refreshing...", file=sys.stderr)
        result = self.msal_app.acquire_token_by_refresh_token(self.refresh_token, scopes=SCOPES)
        if "access_token" in result:
            self.access_token = result["access_token"]
            if "refresh_token" in result:
                self.refresh_token = result["refresh_token"]
                self.config["outlook_refresh_token"] = self.refresh_token
                save_env(self.config)
            print("[TOKEN] ✅ OK", file=sys.stderr)
            return True
        err = result.get("error", "?")
        desc = result.get("error_description", "")
        print(f"[TOKEN] ❌ {err}: {desc}", file=sys.stderr)
        return False

    def _headers(self):
        if not self.access_token:
            if not self._refresh_token():
                raise RuntimeError("Cannot obtain access token")
        return {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}

    def _get(self, endpoint, params=None):
        url = f"{GRAPH_BASE}{endpoint}"
        resp = requests.get(url, headers=self._headers(), params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _resolve_folder(self, name):
        name_lower = name.lower()
        if name_lower in FOLDER_MAP:
            return FOLDER_MAP[name_lower]
        # 尝试查找
        try:
            data = self._get("/me/mailFolders", {"$top": 100})
            for f in data.get("value", []):
                if f["displayName"].lower() == name_lower:
                    return f["id"]
        except Exception:
            pass
        print(f"[WARN] Folder '{name}' not found, using inbox", file=sys.stderr)
        return "inbox"

    def _strip_html(self, html):
        text = re.sub(r"<br\s*/?>", "\n", html)
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"&nbsp;", " ", text)
        text = re.sub(r"&amp;", "&", text)
        text = re.sub(r"&lt;", "<", text)
        text = re.sub(r"&gt;", ">", text)
        return text.strip()

    # ─── Commands ─────────────────────────────────────────────────────────

    def cmd_test(self):
        try:
            data = self._get("/me/mailFolders", {"$top": 1})
            print("✅ Connected!" if data.get("value") else "❌ No folders")
        except Exception as e:
            print(f"❌ {e}", file=sys.stderr)

    def cmd_folders(self):
        data = self._get("/me/mailFolders", {"$top": 100})
        for f in data.get("value", []):
            unread = f.get("unreadItemCount", 0)
            print(f"  {f['displayName']:30s}  unread={unread}")

    def cmd_list(self, folder="inbox", limit=20):
        folder_id = self._resolve_folder(folder)
        endpoint = f"/me/mailFolders/{folder_id}/messages"
        params = {
            "$top": limit,
            "$orderby": "receivedDateTime desc",
            "$select": "id,subject,from,receivedDateTime,isRead,hasAttachments,bodyPreview",
        }
        data = self._get(endpoint, params)
        messages = data.get("value", [])
        self._cached_messages = messages

        for i, msg in enumerate(messages, 1):
            sender = msg.get("from", {}).get("emailAddress", {})
            name = sender.get("name", "?")
            addr = sender.get("address", "?")
            subj = msg.get("subject", "(no subject)")
            dt = msg.get("receivedDateTime", "")[:16]
            read = "✅" if msg.get("isRead") else "🔴"
            att = "📎" if msg.get("hasAttachments") else "  "
            preview = (msg.get("bodyPreview", "") or "")[:50]
            print(f"{read} [{i:2d}] {dt}  {att} {name} <{addr}>")
            print(f"     📌 {subj}")
            if preview:
                print(f"     💬 {preview}...")
            print()
        return messages

    def cmd_read(self, target):
        # 尝试用序号
        if target.isdigit():
            idx = int(target) - 1
            if 0 <= idx < len(self._cached_messages):
                msg_id = self._cached_messages[idx]["id"]
            else:
                # 重新获取
                data = self._get("/me/mailFolders/inbox/messages", {
                    "$top": 50, "$orderby": "receivedDateTime desc", "$select": "id"
                })
                msgs = data.get("value", [])
                if 0 <= idx < len(msgs):
                    msg_id = msgs[idx]["id"]
                else:
                    print(f"❌ 序号 {target} 超出范围", file=sys.stderr)
                    return
        else:
            msg_id = target

        endpoint = f"/me/messages/{msg_id}"
        params = {"$select": "id,subject,from,toRecipients,receivedDateTime,isRead,hasAttachments,body"}
        msg = self._get(endpoint, params)

        sender = msg.get("from", {}).get("emailAddress", {})
        to_list = [r.get("emailAddress", {}).get("address", "?") for r in msg.get("toRecipients", [])]
        subject = msg.get("subject", "(no subject)")
        dt = msg.get("receivedDateTime", "")
        body_html = msg.get("body", {}).get("content", "")
        body_type = msg.get("body", {}).get("contentType", "Text")

        print("=" * 60)
        print(f"From:    {sender.get('name', '?')} <{sender.get('address', '?')}>")
        print(f"To:      {', '.join(to_list)}")
        print(f"Date:    {dt}")
        print(f"Subject: {subject}")
        print("=" * 60)

        if body_type.lower() == "html":
            print(self._strip_html(body_html))
        else:
            print(body_html)
        print("=" * 60)

    def cmd_search(self, query, folder="inbox", limit=20):
        folder_id = self._resolve_folder(folder)
        endpoint = f"/me/mailFolders/{folder_id}/messages"
        params = {
            "$top": limit,
            "$orderby": "receivedDateTime desc",
            "$select": "id,subject,from,receivedDateTime,isRead,bodyPreview",
        }
        data = self._get(endpoint, params)
        messages = data.get("value", [])

        # 客户端过滤
        results = []
        for msg in messages:
            subj = msg.get("subject", "")
            preview = msg.get("bodyPreview", "") or ""
            if query.lower() in subj.lower() or query.lower() in preview.lower():
                results.append(msg)

        if not results:
            print(f"🔍 No results for '{query}'")
            return []

        print(f"🔍 Found {len(results)} results for '{query}':\n")
        for i, msg in enumerate(results, 1):
            sender = msg.get("from", {}).get("emailAddress", {})
            subj = msg.get("subject", "(no subject)")
            dt = msg.get("receivedDateTime", "")[:16]
            read = "✅" if msg.get("isRead") else "🔴"
            print(f"{read} [{i}] {dt}  {sender.get('name', '?')}")
            print(f"   📌 {subj}")
            print()
        return results

    def cmd_code(self, search_kw=None, limit=10):
        """获取最新验证码。"""
        folder_id = self._resolve_folder("inbox")
        endpoint = f"/me/mailFolders/{folder_id}/messages"
        params = {
            "$top": limit,
            "$orderby": "receivedDateTime desc",
            "$select": "id,subject,from,receivedDateTime,body",
        }
        data = self._get(endpoint, params)
        messages = data.get("value", [])

        for msg in messages:
            if search_kw:
                sender = msg.get("from", {}).get("emailAddress", {}).get("address", "")
                subj = msg.get("subject", "")
                if search_kw.lower() not in sender.lower() and search_kw.lower() not in subj.lower():
                    continue

            body_html = msg.get("body", {}).get("content", "")
            text = self._strip_html(body_html)

            # 提取6位验证码
            codes = re.findall(r"\b(\d{6})\b", text)
            # 过滤占位符
            real_codes = [c for c in codes if c != "555555"]
            if real_codes:
                sender = msg.get("from", {}).get("emailAddress", {})
                dt = msg.get("receivedDateTime", "")[:16]
                subj = msg.get("subject", "")
                print(f"📧 {dt}  {sender.get('address', '?')}")
                print(f"   📌 {subj}")
                print(f"🔑 验证码: {real_codes[0]}")
                return real_codes[0]

        print("❌ 未找到验证码", file=sys.stderr)
        return None

    def cmd_attachments(self, target):
        msg_id = self._resolve_msg_id(target)
        data = self._get(f"/me/messages/{msg_id}/attachments")
        atts = data.get("value", [])
        if not atts:
            print("📎 No attachments")
            return
        print(f"📎 {len(atts)} attachment(s):")
        for att in atts:
            print(f"  📄 {att.get('name', '?')} ({att.get('size', 0)} bytes)")

    def cmd_download(self, target):
        msg_id = self._resolve_msg_id(target)
        data = self._get(f"/me/messages/{msg_id}/attachments")
        for att in data.get("value", []):
            content = att.get("contentBytes", "")
            if content:
                out = Path(att.get("name", "attachment"))
                out.write_bytes(base64.b64decode(content))
                print(f"✅ Saved: {out}")

    def cmd_refresh(self):
        if self._refresh_token():
            save_env(self.config)
            print("✅ Token refreshed")
        else:
            print("❌ Refresh failed", file=sys.stderr)

    def _resolve_msg_id(self, target):
        if target.isdigit():
            idx = int(target) - 1
            data = self._get("/me/mailFolders/inbox/messages", {
                "$top": 50, "$orderby": "receivedDateTime desc", "$select": "id"
            })
            msgs = data.get("value", [])
            if 0 <= idx < len(msgs):
                return msgs[idx]["id"]
            print(f"❌ 序号 {target} 超出范围", file=sys.stderr)
            sys.exit(1)
        return target


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Outlook Token Email Client")
    parser.add_argument("command", choices=["list", "read", "search", "code", "folders", "test", "refresh", "attachments", "download"])
    parser.add_argument("target", nargs="?", help="Message ID/序号 or search query")
    parser.add_argument("-f", "--folder", default="inbox")
    parser.add_argument("-n", "--limit", type=int, default=20)
    parser.add_argument("-s", "--search", dest="search_kw", help="Keyword for code search")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    config = load_env()
    client = OutlookClient(config)

    if args.command == "test":
        client.cmd_test()
    elif args.command == "folders":
        client.cmd_folders()
    elif args.command == "list":
        msgs = client.cmd_list(args.folder, args.limit)
        if args.json:
            print(json.dumps(msgs, indent=2, default=str))
    elif args.command == "read":
        if not args.target:
            print("❌ Need message ID or 序号", file=sys.stderr)
            sys.exit(1)
        client.cmd_read(args.target)
    elif args.command == "search":
        if not args.target:
            print("❌ Need search query", file=sys.stderr)
            sys.exit(1)
        client.cmd_search(args.target, args.folder, args.limit)
    elif args.command == "code":
        client.cmd_code(args.search_kw, args.limit)
    elif args.command == "refresh":
        client.cmd_refresh()
    elif args.command == "attachments":
        if not args.target:
            print("❌ Need message ID or 序号", file=sys.stderr)
            sys.exit(1)
        client.cmd_attachments(args.target)
    elif args.command == "download":
        if not args.target:
            print("❌ Need message ID or 序号", file=sys.stderr)
            sys.exit(1)
        client.cmd_download(args.target)


if __name__ == "__main__":
    main()
