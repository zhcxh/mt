#!/usr/bin/env python3
"""KMoe push chapters to Kindle - reusable template

Usage:
  python3 kmoe_push_template.py --book-id 35388 --chapters 601-750
  
Or modify the parameters below directly.
"""
import asyncio
import argparse
from playwright.async_api import async_playwright

# === CONFIGURATION ===
MOE_USERNAME = "wodexinxi@yeah.net"  # Read from .env in production
MOE_PASSWORD = "Aa654321"
BASE_URL = "https://kxx.moe"

async def login(page):
    """Login to KMoe"""
    print("Logging in...")
    await page.goto(f"{BASE_URL}/", wait_until="networkidle")
    await page.wait_for_timeout(2000)
    
    login_link = page.locator("a:has-text('登錄')")
    if await login_link.count() > 0:
        await login_link.click()
        await page.wait_for_timeout(1000)
        await page.fill('input[placeholder="請輸入郵箱帳號"]', MOE_USERNAME)
        await page.fill('input[placeholder="請輸入帳號密碼"]', MOE_PASSWORD)
        await page.click('button:has-text("登　　錄")')
        await page.wait_for_timeout(3000)
        
        # Verify login
        lv_link = page.locator("a:has-text('Lv')")
        if await lv_link.count() > 0:
            print("✓ Login successful")
            return True
    print("✗ Login failed")
    return False

def chapters_to_vol_ids(start_chapter, end_chapter):
    """Convert chapter range to volume IDs"""
    # Chapters are grouped in batches of 10
    # Volume ID = 3001 + (batch_index * 10)
    start_batch = (start_chapter - 1) // 10
    end_batch = (end_chapter - 1) // 10
    
    vol_ids = []
    for batch in range(start_batch, end_batch + 1):
        vol_id = 3001 + (batch * 10)
        vol_ids.append(str(vol_id))
    
    return vol_ids

async def push_to_kindle(page, book_id, vol_ids):
    """Push selected volumes to Kindle via fetch API"""
    vol_list = ','.join(vol_ids)
    print(f"Pushing {len(vol_ids)} volumes: {vol_list[:50]}...")
    
    result = await page.evaluate("""
        async (params) => {
            const formData = new FormData();
            formData.append('push_bookid', params.bookid);
            formData.append('push_vol_list', params.volList);
            formData.append('pushto', '0');
            
            try {
                const response = await fetch('/book_push.php', {
                    method: 'POST',
                    body: formData,
                    credentials: 'same-origin'
                });
                const text = await response.text();
                return {
                    status: response.status,
                    body: text.substring(0, 500)
                };
            } catch (e) {
                return { error: e.message };
            }
        }
    """, {"bookid": book_id, "volList": vol_list})
    
    return result

async def main():
    parser = argparse.ArgumentParser(description='KMoe Push to Kindle')
    parser.add_argument('--book-id', required=True, help='Manga book ID')
    parser.add_argument('--chapters', required=True, help='Chapter range (e.g., 601-750)')
    parser.add_argument('--site', default='kxx', help='Site domain (kxx/kzz/koz)')
    args = parser.parse_args()
    
    # Parse chapter range
    start, end = map(int, args.chapters.split('-'))
    vol_ids = chapters_to_vol_ids(start, end)
    
    print(f"Book ID: {args.book_id}")
    print(f"Chapters: {start}-{end}")
    print(f"Volumes: {len(vol_ids)}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()
        
        # Login
        if not await login(page):
            await browser.close()
            return
        
        # Navigate to manga page
        print(f"\nNavigating to manga page...")
        await page.goto(f"{BASE_URL}/c/{args.book_id}.htm", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        # Push to Kindle
        print("\nPushing to Kindle...")
        result = await push_to_kindle(page, args.book_id, vol_ids)
        
        if result.get('status') == 200:
            print("✓ Push request sent successfully")
            print(f"Response: {result.get('body', '')[:200]}")
        else:
            print(f"✗ Push failed: {result}")
        
        # Take screenshot
        await page.screenshot(path="/opt/data/kmoe_push_result.png")
        print("\nScreenshot saved to /opt/data/kmoe_push_result.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
