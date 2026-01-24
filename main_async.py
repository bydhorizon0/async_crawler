import asyncio
import random
from asyncio import Queue

from playwright.async_api import async_playwright, Browser, Page


async def main():
    queue = asyncio.Queue()

    for t in []:  # 수집 리스트
        queue.put_nowait(t)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        async with asyncio.TaskGroup() as tg:
            for _ in range(10):
                tg.create_task(worker(queue, browser))

        await browser.close()

    # await queue.join()


async def worker(queue: Queue, browser: Browser):
    page = await browser.new_page()

    try:
        while True:
            try:
                target = queue.get_nowait()
            except asyncio.QueueEmpty:
                break

            # 예외가 발생해도 TaskGroup으로 예외가 전파되지 않고 수집을 계속 진행
            try:
                await scrape(page, target)
                await asyncio.sleep(random.uniform(2.2, 5.7))
            except Exception as e:
                print(e)
    finally:
        await page.close()  # page 누수 방지를 위해 반드시 종료


async def scrape(page: Page, target):
    await page.goto(target.url, timeout=30_000, wait_until="domcontentloaded")
    print(await page.title())


if __name__ == "__main__":
    asyncio.run(main())

"""
Queue 를 사용해 동시성 제어
Semaphore 를 사용해도 되지만 Queue 가 더 효율적
로그 추가
"""
