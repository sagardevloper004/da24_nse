import asyncio
import random
import threading
event = threading.Event()

from playwright.async_api import async_playwright
from playwright_stealth import Stealth


async def getstock(page):
    stock_header = await page.query_selector('h1.companyName.compDiv')
    stock_header_text = await stock_header.text_content()

    print("stock")
    print("")
    print("")
    print("stock_header", stock_header_text )
    print("")
    print("stock")
    # get all 1 month historical data of stock
    page.close() # find how to close page
    event.set()   # signal completion


async def waitPage(page):
    await page.wait_for_timeout(5000)
    await page.wait_for_load_state('networkidle')
    await page.wait_for_load_state('load')
    await page.wait_for_load_state('domcontentloaded')


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
            
            # waiting for page to laod 

            await waitPage(page)
            # click on market data and find indices

            markDataLink = await page.query_selector('div.main_nav ul.navbar-nav a#link_2')
            await markDataLink.click()
            await waitPage(page)
            
            indicesLinks = await page.query_selector_all("div#aboutDropdownContent ul a:has-text('Indices')")
            print(len(indicesLinks))
            print(indicesLinks)
            clickAbleIndicesLinks = None
            
            # find and click on indices

            for link in indicesLinks:
                print('-')
                print('link.text_content()', await link.text_content())
                print(await link.get_attribute('href'))
                print('-')
                if await link.text_content() == 'Indices':
                    print('text matched')
                    clickAbleIndicesLinks = link
            await clickAbleIndicesLinks.click()
            await waitPage(page)
            # find nifty 50 a tag and click to open new page
            await page.wait_for_selector("table#liveindexTable  tbody a:has-text('NIFTY 50')")
            
            nifty50Link = await page.query_selector("table#liveindexTable  tbody a:has-text('NIFTY 50')")
             

            # create new page context 

            async with context.expect_page() as new_page_info:
                await nifty50Link.click()

            new_page = await new_page_info.value
            await new_page.wait_for_load_state()

            await waitPage(new_page)


         
            nifty50StockList = await new_page.query_selector_all('table#equityStockTable > tbody > tr > td:nth-child(1) > a')

            if len(nifty50StockList) > 0: 
                for stock in nifty50StockList:
                    event.clear()
                    print('-'*50)
                    print(await stock.text_content())
                    
                    async with context.expect_page() as stock_page_info:
                        await stock.click()
                    stock_page = await stock_page_info.value
                    await stock_page.wait_for_load_state()
                    await waitPage(stock_page)
                    await getstock(stock_page)
                    event.wait() 
                    print("Cycle finished")
                    print('-'*50)
            else:
                print('not found ',nifty50StockList)
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