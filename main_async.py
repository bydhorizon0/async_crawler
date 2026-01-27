import asyncio
import random
import re
from asyncio import Queue
from typing import Final

import playwright.async_api
from playwright.async_api import async_playwright, Browser, Page

from database import DatabaseManager, ScrapTarget

WORKERS: Final[int] = 3


async def main():
    db_mgr = DatabaseManager()
    targets = await db_mgr.select_scrap_targets()
    queue: Queue[ScrapTarget] = asyncio.Queue()

    for t in targets:  # 수집 리스트
        queue.put_nowait(t)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        async with asyncio.TaskGroup() as tg:
            workers = [
                tg.create_task(worker(queue, browser, db_mgr), name=f"Worker-{i}")
                for i in range(WORKERS)
            ]

            await queue.join()

        await browser.close()


async def worker(queue: Queue, browser: Browser, db_mgr: DatabaseManager):
    page = await browser.new_page()

    try:
        while True:
            try:
                target: ScrapTarget = queue.get_nowait()
            except asyncio.QueueEmpty:
                break

            # 예외가 발생해도 TaskGroup으로 예외가 전파되지 않고 수집을 계속 진행
            try:
                await scrape(page, target)
                await asyncio.sleep(random.uniform(2.2, 5.7))
            except playwright.async_api.TimeoutError as e:
                pass
            except playwright.async_api.WebError as e:
                pass
            except playwright.async_api.Error as e:
                print(e)
            except Exception as e:
                print(e)
            finally:
                queue.task_done()
    finally:
        await page.close()  # page 누수 방지를 위해 반드시 종료


async def scrape(page: Page, target: ScrapTarget):
    for i in range(1, 4):
        await page.goto(target.site_url.format(i), timeout=30_000, wait_until="domcontentloaded")
        print(await page.title())

        items = await page.locator(target.list_path).all()
        for item in items:
            title = await item.locator(target.title_path).inner_text()
            id_str = await item.locator(target.id_path).get_attribute(target.id_attr)

            id_match = re.search(target.id_regex, id_str)
            if not id_match:
                raise playwright.async_api.Error("ID 정규표현식 실패")
            target_id = id_match.group(1)
            print(title.strip(), target.detail_url_format.format(target_id))


if __name__ == "__main__":
    asyncio.run(main())

"""
Queue 를 사용해 동시성 제어
Semaphore 를 사용해도 되지만 Queue 가 더 효율적
로그 추가
"""
