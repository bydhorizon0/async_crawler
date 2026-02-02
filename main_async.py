import asyncio
from asyncio import Queue
from typing import Final

from playwright.async_api import async_playwright

from core.database import DatabaseManager, ScrapTarget
from scraper.engine import worker

WORKERS: Final[int] = 4


async def main():
    db_mgr = DatabaseManager()
    await db_mgr.initialize()
    targets = await db_mgr.select_scrap_targets("PAGE")
    queue: Queue[ScrapTarget] = asyncio.Queue()

    for t in targets:  # 수집 리스트
        queue.put_nowait(t)

    # PAGE 수집
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        async with asyncio.TaskGroup() as tg:
            workers = [
                tg.create_task(worker(queue, browser, db_mgr), name=f"Worker-{i}")
                for i in range(WORKERS)
            ]

            await queue.join()

        await browser.close()

    # API 요청 수집


if __name__ == "__main__":
    asyncio.run(main())

"""
- Queue 를 사용해 동시성 제어, Semaphore 를 사용해도 되지만 Queue 가 더 효율적
- 예외 추가
- 로그 추가
"""
