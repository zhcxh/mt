#!/usr/bin/env python3
"""自动追剧脚本：检查新集数并下载 BT 种子。配合 cron 使用。
用法：修改下方配置，然后通过 cron 定期执行。
"""
import subprocess
import re
import os
import json

# ===== 配置（修改这里） =====
QB_HOST = "192.168.31.218:8989"
QB_USER = "myadmin"
QB_PASS = "Aa@.654321"
QB_SAVE = "/downloads/整理前"
KEYWORD = "夫妻的博弈"        # 中文名
ENGLISH_NAME = "Mrs.Revenge"  # 英文名（用于搜索和验证）
TOTAL_EPISODES = 25
CHECKED_FILE = "/opt/data/scripts/checked_episodes.json"
CRON_JOB_ID = ""  # 全部完成后自动删除此 cron 任务（留空则不删）

def run_cmd(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    return r.stdout.strip()

def load_checked():
    if os.path.exists(CHECKED_FILE):
        with open(CHECKED_FILE) as f:
            return json.load(f)
    return {"episodes": [], "completed": False}

def save_checked(data):
    with open(CHECKED_FILE, "w") as f:
        json.dump(data, f)

def login_qb():
    run_cmd('curl -s -c /tmp/qb_cookies.txt --data "username={}&password={}" "http://{}/api/v2/auth/login"'.format(QB_USER, QB_PASS, QB_HOST))

def add_torrent(filepath, savepath=QB_SAVE):
    result = run_cmd('curl -s -b /tmp/qb_cookies.txt -F "fileselect=@{}" -F "savepath={}" "http://{}/api/v2/torrents/add"'.format(filepath, savepath, QB_HOST))
    return "success_count" in result or "added_torrent_ids" in result

def verify_torrent(filepath, keyword, english_name=""):
    try:
        with open(filepath, "rb") as f:
            data = f.read()
        if b"4:name" in data:
            idx = data.index(b"4:name")
            nls = data.index(b":", idx + 6)
            nl = int(data[idx + 6:nls])
            name = data[nls + 1 : nls + 1 + nl].decode("utf-8", errors="replace")
            return keyword in name or english_name in name
    except:
        pass
    return False

def search_episode(ep):
    from urllib.parse import quote
    patterns = ["{} 第{}集".format(KEYWORD, ep)]
    if ENGLISH_NAME:
        patterns.append("{}.S01E{:02d}".format(ENGLISH_NAME, ep))
    for pattern in patterns:
        encoded = quote(pattern)
        url = "https://www.1lou.pro/search-{}-1.htm".format(encoded)
        threads = run_cmd("curl -sL '{}' | grep -oP 'thread-[0-9]+\\.htm' | head -5".format(url))
        threads = [t for t in threads.split("\n") if t]
        for tid in threads[:3]:
            html = run_cmd("curl -sL 'https://www.1lou.pro/{}'".format(tid))
            if KEYWORD in html or ENGLISH_NAME in html:
                if "BT下载" in html and "夸克" not in html:
                    attach_match = re.search(r'attach-download-(\d+)', html)
                    title_match = re.search(r'<title>([^<]+)', html)
                    if attach_match and title_match:
                        title = title_match.group(1)
                        if str(ep) in title or "E{:02d}".format(ep) in title:
                            return {"ep": ep, "thread": tid, "attach": attach_match.group(1), "title": title[:80]}
    return None

def delete_cron_job():
    if CRON_JOB_ID:
        run_cmd('hermes cron remove {} --yes 2>&1 || true'.format(CRON_JOB_ID))

def main():
    checked = load_checked()
    if checked["completed"]:
        print("已标记完成，跳过检查")
        return
    found_new = False
    for ep in range(1, TOTAL_EPISODES + 1):
        if ep in checked["episodes"]:
            continue
        result = search_episode(ep)
        if result:
            torrent_url = "https://www.1lou.pro/attach-download-{}.htm".format(result["attach"])
            filename = "{}_第{}集_4K.torrent".format(KEYWORD, ep)
            filepath = "/opt/data/{}".format(filename)
            run_cmd('curl -sL -o "{}" "{}"'.format(filepath, torrent_url))
            if verify_torrent(filepath, KEYWORD, ENGLISH_NAME):
                login_qb()
                if add_torrent(filepath):
                    print("✅ 第{}集: 已下载并推送".format(ep))
                    checked["episodes"].append(ep)
                    found_new = True
                else:
                    print("⚠️ 第{}集: 推送失败".format(ep))
            else:
                print("❌ 第{}集: 种子内容错误，已删除".format(ep))
                os.remove(filepath)
    all_eps = set(range(1, TOTAL_EPISODES + 1))
    if all_eps.issubset(set(checked["episodes"])):
        checked["completed"] = True
        print("\n🎉 全部{}集下载完成！".format(TOTAL_EPISODES))
        delete_cron_job()
        print("✅ 定时任务已删除")
    save_checked(checked)
    if not found_new and not checked["completed"]:
        print("暂无新集数（已下载 {}/{} 集）".format(len(checked["episodes"]), TOTAL_EPISODES))

if __name__ == "__main__":
    main()
