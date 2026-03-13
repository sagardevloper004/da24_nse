import asyncio
import random
from playwright.async_api import async_playwright

async def get_nse_data():
    async with async_playwright() as p:
        # 1. Use 'channel="chrome"' if installed to look more authentic
        browser = await p.chromium.launch(headless=False)
        
        # 2. Add extra headers to look like a real user
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.nseindia.com/"
            }
        )
        
        page = await context.new_page()

        try:
            # Step 1: Hit the home page first to get initial session cookies
            print("Landing on Home Page...")
            await page.goto("https://www.nseindia.com/", wait_until="networkidle")
            await asyncio.sleep(random.uniform(2, 4)) # Human-like pause

            # Step 2: Navigate directly to Nifty 50 page instead of clicking 5 menus
            print("Navigating to Nifty 50 Market Data...")
            target_url = "https://www.nseindia.com/market-data/live-equity-market?symbol=NIFTY%2050"
            await page.goto(target_url, wait_until="load")
            
            # Step 3: Wait for the table to actually appear
            await page.wait_for_selector("table#equityStockTable", timeout=15000)

            # Step 4: Logic to click each 'a' tag in the table
            # We get the list of symbols first
            rows = await page.query_selector_all("table#equityStockTable tbody tr")
            symbols = []
            
            for row in rows:
                anchor = await row.query_selector("td a")
                if anchor:
                    symbol_text = await anchor.inner_text()
                    symbols.append(symbol_text.strip())

            print(f"Discovered {len(symbols)} stocks. Starting deep scrape...")

            # Step 5: Iterate and click
            for symbol in symbols[:5]: # Testing with first 5 to avoid ban
                print(f"Scraping data for: {symbol}")
                # Click the stock link
                await page.click(f"table#equityStockTable a:has-text('{symbol}')")
                
                # Wait for detail page to load (e.g., look for the price element)
                await page.wait_for_selector("#quoteLTP", timeout=10000)
                ltp = await page.inner_text("#quoteLTP")
                print(f"Symbol: {symbol} | LTP: {ltp}")
                
                # Go back to the list
                await page.go_back(wait_until="networkidle")
                await asyncio.sleep(random.uniform(1, 3))
                await page.wait_for_timeout(100000)
        except Exception as e:
            print(f"Connection Error: {e}")
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(get_nse_data())