---
name: kmoe-manga
description: |
  KMoe (kxx.moe, kzz.moe, koz.moe) manga/ebook platform automation — login, browse, search manga, push chapters to Kindle.
  Triggers: kmoe, kxx, kzz, koz, manga push, kindle push, comic download, 漫画推送, kindle漫画
category: automation
---

# KMoe Manga Platform Automation

KMoe platforms (kxx.moe, kzz.moe, koz.moe) offer manga in Kindle/epub format with a "push to Kindle" feature.

## Core Workflow

1. **Login** at home page (`/`) — credentials from `/opt/data/.env` (`moe_username`, `moe_password`)
2. **Navigate** to manga page (e.g., `https://kxx.moe/c/0202ff.htm`)
3. **Select chapters** via checkboxes
4. **Push to Kindle** via form submission to `/book_push.php`

## Critical Technical Findings

### Login & Session
- Login at `https://kxx.moe/` first, then navigate to manga page
- Session can be lost between page loads — re-login if "請先登錄" dialog appears
- Login button: `button:has-text("登　　錄")`
- Email field: `input[placeholder="請輸入郵箱帳號"]`
- Password field: `input[placeholder="請輸入帳號密碼"]`

### Form Structure
```
Form: form_action
Action: /book_push.php
Method: POST
Target: iframe_action (submitting to iframe, not main page)

Hidden fields:
- push_bookid: manga ID (e.g., "35388")
- push_vol_list: comma-separated volume IDs (e.g., "3601,3611,...")
- pushto: "0" for Kindle
```

### Checkbox Mechanics
- Checkboxes: `input[type="checkbox"][name="checkbox_vol"]`
- Each checkbox has `onclick="javascript:sum_sel_item();"`
- Checkbox `value` attribute contains volume ID (e.g., "3601" for chapters 601-610)
- `size_push_<volId>` hidden inputs contain size in MB (e.g., "33.7")
- `size_down_<volId>` hidden inputs contain download size

### Chapter to Volume Mapping
- Chapters are grouped in batches of 10 (e.g., 601-610 = one volume)
- Volume ID pattern: `3001 + (batch_index * 10)`
- First batch (001-010) = vol_id 3001
- Batch 60 (601-610) = vol_id 3601
- Batch 74 (741-750) = vol_id 3741

### Push Mechanism (Direct POST)
The `do_push()` function has issues with `window.quota_now` being inaccessible. Use direct fetch:

```javascript
const formData = new FormData();
formData.append('push_bookid', bookid);
formData.append('push_vol_list', '3601,3611,3621,...');
formData.append('pushto', '0');

const response = await fetch('/book_push.php', {
    method: 'POST',
    body: formData,
    credentials: 'same-origin'
});
// Response contains: parent.display_codeinfo("m102", 1) etc.
```

### Success Indicators
- HTTP 200 response
- Response body contains `display_codeinfo` calls:
  - `"m102"` = push started/processing
  - `"c100"` = completed
  - `"m104"` = status update
- Quota decreases after successful push (check "目前可用額度")

## Pitfalls

1. **`window.quota_now` returns None** — Variable is defined in `<script>` tag with `var`, not on `window`. Extract from script content via regex: `var\s+quota_now\s*=\s*["']?(\d+)["']?`

2. **Form submits to iframe** — `target="iframe_action"` means page doesn't change. Use `fetch()` API for direct POST.

3. **Checkbox `checked` property not enough** — Must trigger `onclick` handler via `.click()` to update `push_vol_list`. Setting `.checked = true` alone won't populate the hidden field.

4. **Size calculation fails if `size_push_*` elements missing** — They exist but may not be visible in DOM queries. Use `document.getElementsByName('size_push_' + volId)[0]`.

5. **Session loss** — Login state can be lost. Always verify login status before push (check for `a:has-text('Lv')` element).

## Quota System
- VIP: 40GB/month
- Non-VIP: Limited quota (check "目前可用額度")
- Push consumes quota based on total size of pushed chapters
- Single chapter push allowed even if size > quota (special rule in `do_push`)
