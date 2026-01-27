import asyncio
import random
import re
from asyncio import Queue

import playwright
from playwright.async_api import Browser, Page

from core.database import DatabaseManager
from models.scrap_target import ScrapTarget


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

        items = await page.locator(target.list_path).all()
        for item in items:
            title = await item.locator(target.title_path).inner_text()
            id_str = await item.locator(target.id_path).get_attribute(target.id_attr)

            id_match = re.search(target.id_regex, id_str)
            if not id_match:
                raise playwright.async_api.Error("ID 정규표현식 실패")
            target_id = id_match.group(1)
            print(
                f"{target.site_name}({target.seq}) 수집 {title.strip()}, {target.detail_url_format.format(target_id)}"
            )
