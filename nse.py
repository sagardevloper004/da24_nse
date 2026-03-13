import asyncio
import random

from playwright.async_api import async_playwright
from playwright_stealth import Stealth
async def getnse():
    async with Stealth().use_async(async_playwright()) as p:
        browser =await p.chromium.launch(headless=False)    
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.nseindia.com/"
            }
        )
        
            
        page = await context.new_page()
        webdriver_status = await page.evaluate("navigator.webdriver")
        print("from new_page: ", webdriver_status)

        try:    
            await page.goto("https://www.nseindia.com/")
            await asyncio.sleep(random.uniform(2, 4)) # Human-like pause

            await page.wait_for_timeout(1000)
            await page.wait_for_load_state("networkidle")
            await page.wait_for_load_state('load')
            await page.wait_for_load_state('domcontentloaded')
            markDataLink = await page.query_selector('div.main_nav ul.navbar-nav a#link_2')
            await markDataLink.click()
            await page.wait_for_timeout(2000)
            await page.wait_for_load_state('networkidle')
            indicesLinks = await page.query_selector_all("div#aboutDropdownContent ul a:has-text('Indices')")
            print(len(indicesLinks))
            print(indicesLinks)
            clickAbleIndicesLinks = None
            for link in indicesLinks:
                print('-')
                print('link.text_content()', link.text_content())
                print(link.get_attribute('href'))
                print('-')
                if await link.text_content() == 'Indices':
                    print('text matched')
                    clickAbleIndicesLinks = link
            await clickAbleIndicesLinks.click()
            await page.wait_for_timeout(5000)
            await page.wait_for_load_state('networkidle')
            await page.wait_for_load_state('load')
            await page.wait_for_load_state('domcontentloaded')
            await page.wait_for_selector("table#liveindexTable  tbody a:has-text('NIFTY 50')")
            nifty50Link = await page.query_selector("table#liveindexTable  tbody a:has-text('NIFTY 50')")
            await nifty50Link.click()    
            await page.wait_for_timeout(100000)
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)
        except Exception as e:
            print('error')
            print('')
            print('e', e)
            print('')
            print('error')

        finally:
            await browser.close()


if __name__ == '__main__':
    asyncio.run(getnse())