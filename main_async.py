import asyncio
from asyncio import Queue
from typing import Final

from playwright.async_api import async_playwright, Page

from core.database import DatabaseManager, ScrapTarget
from scraper.engine import worker

WORKERS: Final[int] = 4
CONTEXT_POOL_SIZE: Final[int] = 3
PAGES_PER_CONTEXT: Final[int] = 2


async def main():
    db_mgr = DatabaseManager()
    await db_mgr.initialize()

    targets = await db_mgr.select_scrap_targets("PAGE")

    queue: Queue[ScrapTarget | None] = asyncio.Queue()
    page_queue: Queue[Page] = asyncio.Queue()

    # 수집 목록 큐
    for t in targets:
        queue.put_nowait(t)

    for _ in range(WORKERS):
        queue.put_nowait(None)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # Context Pool
        contexts = [await browser.new_context() for _ in range(CONTEXT_POOL_SIZE)]
        # Page Pool
        pages: list[Page] = []

        for context in contexts:
            for _ in range(PAGES_PER_CONTEXT):
                page = await context.new_page()
                pages.append(page)
                await page_queue.put(page)

        async with asyncio.TaskGroup() as tg:
            for i in range(WORKERS):
                tg.create_task(worker(queue, page_queue, db_mgr), name=f"Worker-{i}")

            await queue.join()

        for page in pages:
            await page.close()

        for context in contexts:
            await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
