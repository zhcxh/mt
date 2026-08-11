# KMoe Technical Details

## Site Structure

### URLs
- Home: `https://kxx.moe/` (or kzz.moe, koz.moe)
- Manga page: `https://kxx.moe/c/{bookid}.htm`
- Push endpoint: `https://kxx.moe/book_push.php`
- Search: `https://kxx.moe/list.php?q={query}`

### JavaScript Modules
The site uses ES modules imported from:
- `/zzcomm.js?t4` — common utilities (km_set_view, kb_http_get, etc.)
- `/zzfunc.js?t4` — function utilities (tips_close, disp_codeinfo, goto_url, etc.)

### Key Global Variables (defined in `<script>` tags)
```javascript
var uin = "10704779";           // User ID (0 = not logged in)
var ulevel = parseInt("3");     // User level
var is_vip = parseInt("0");     // VIP status
var bookid = "35388";           // Current manga ID
var quota_now = "2484";         // Available quota in MB
var quota_used = "587";         // Used quota in MB
var device_mailto = "xxx@kindle.com";  // Kindle email
```

**Note:** These are `var` declarations, NOT `window.` properties. Access via regex extraction from script content.

## Form Submission Details

### Form: form_action
```html
<form name="form_action" action="/book_push.php" method="post" 
      enctype="multipart/form-data" target="iframe_action">
  <input type="hidden" name="push_bookid" value="35388">
  <input type="hidden" name="push_vol_list" value="">
  <input type="hidden" name="pushto" value="0">
</form>
```

### Required POST Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| push_bookid | hidden | Manga/book ID |
| push_vol_list | hidden | Comma-separated volume IDs |
| pushto | hidden | "0" for Kindle, "2" for KOOBONE |

### Response Format
The server returns HTML with JavaScript to execute in parent frame:
```html
<script>parent.display_codeinfo( "m102", 1 );</script>
<script>parent.display_codeinfo( "c100", 1 );</script>
<script>parent.display_codeinfo( "m104", 1 );</script>
```

## Checkbox & Volume Data

### Checkbox Structure
```html
<input type="checkbox" name="checkbox_vol" value="3601" 
       onclick="javascript:sum_sel_item();">
<input type="hidden" name="size_down_3601" value="33.7">
<input type="hidden" name="size_push_3601" value="33.7">
```

### Volume ID Calculation
- Base: 3001 (for chapters 001-010)
- Pattern: `3001 + (batch_index * 10)`
- Examples:
  - Batch 0 (001-010): 3001
  - Batch 1 (011-020): 3011
  - Batch 60 (601-610): 3601
  - Batch 74 (741-750): 3741

### sum_sel_item() Function
Called when checkbox is clicked. Updates:
- `push_vol_list` hidden field with checked volume IDs
- Button styles (active/inactive)

### do_push(pPushTo) Function
```javascript
function do_push(pPushTo) {
    // Sets pushto value
    // Calculates total push_size from size_push_* elements
    // Checks: push_count > 0 AND push_size <= quota_now AND push_vol_list.length > 0
    // If OK: form.submit()
    // Always returns false
}
```

**Issue:** `window.quota_now` may be inaccessible in some contexts. Use direct fetch instead.

## Quota Rules
- VIP: 40GB/month
- Non-VIP: Limited (check "目前可用額度" on page)
- Special rule: Single chapter push allowed even if size > quota (when push_count==1 and quota_now>0)
- Push size is sum of all selected volumes' `size_push_*` values
