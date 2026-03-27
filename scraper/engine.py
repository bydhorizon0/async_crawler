import asyncio
import re

import playwright
from playwright.async_api import Page

from core.database import DatabaseManager
from models.scrap_target import ScrapTarget

semaphore = asyncio.Semaphore(3)


async def worker(
    queue: asyncio.Queue[ScrapTarget | None],
    page_queue: asyncio.Queue[Page],
    db_mgr: DatabaseManager,
) -> None:
    while True:
        target = await queue.get()

        if target is None:
            queue.task_done()
            break

        page = await page_queue.get()

        # 예외가 발생해도 TaskGroup으로 예외가 전파되지 않고 수집을 계속 진행
        try:
            await scrape(page, target)
        except (playwright.async_api.Error, Exception) as e:
            print(f"[수집 실패] {target.site_name}({target.seq}): {e}")

            error_msg = str(e)
            # await db_mgr.insert_scrap_error(target.seq, error_msg)
        finally:
            await page.goto("about:blank")
            await page.context.clear_cookies()
            await page_queue.put(page)  # Page를 queue에 다시 반납
            # queue.task_done()이 호출되지 않으면 queue.join()은 작업이 남은 줄 알고 계속 대기하게 된다.
            # 실패 상황에서도 반드시 호출되어야 프로그램이 정상 종료된다.
            queue.task_done()


async def scrape(page: Page, target: ScrapTarget) -> None:
    for i in range(1, 4):
        if target.pagination_path:
            async with semaphore:
                await page.goto(target.site_url, wait_until="domcontentloaded")

            locator = page.locator(target.pagination_path)

            if await locator.count() <= 1:
                break

            await locator.nth(i).click()
            # await page.wait_for_selector()
        else:
            await page.goto(
                target.site_url.format(i), timeout=30_000, wait_until="domcontentloaded"
            )

        locator = page.locator(target.list_path)
        await locator.first.wait_for(state="visible", timeout=30_000)

        count = await locator.count()

        if count == 0:
            return

        for list_idx in range(count):
            item = locator.nth(list_idx)

            title_locator = item.locator(target.title_path)
            id_locator = item.locator(target.id_path)

            title = (await title_locator.text_content()) or ""
            id_str = await id_locator.get_attribute(target.id_attr)

            if id_str is None:
                raise playwright.async_api.Error("ID attributes is None")

            format_args: tuple[str, ...] = ()

            if target.id_regex:
                id_match = re.search(target.id_regex, id_str)

                if not id_match:
                    raise playwright.async_api.Error("ID 정규표현식 실패")
                # format(*target_ids)로 1개 이상도 유연하게 처리
                target_ids = id_match.groups()

                # 만약 정규식에 괄호가 없어서 groups()가 비어있다면, 매칭된 전체 문자열을 사용하도록 방어 로직 추가
                format_args = target_ids if target_ids else (id_match.group(),)
            else:
                format_args = (id_str,)

            try:
                detail_url = target.detail_url_format.format(*format_args)
                print(
                    f"{target.site_name}({target.seq}) 수집 {title.strip()}, {detail_url}"
                )
            except IndexError:
                print(f"[{target.site_name}] URL 포맷팅 실패: 인자 개수 불일치")
