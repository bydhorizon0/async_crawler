from pathlib import Path
from typing import Sequence

import aiosqlite

from models.scrap_result import ScrapResultTuple, ScrapResult
from models.scrap_target import ScrapTarget

"""
TypedDict는 오버헤드가 없고, 단순히 데이터를 전달하는데 유용하다. 
dataclass는 데이터를 단순히 전달하는 것을 넘어, 객체로서 관리하고 싶을 때 적합하다.
NamedTuple
"""


class DatabaseManager:
    def __init__(self) -> None:
        base_dir = Path(__file__).resolve().parent.parent
        self.schema_path = base_dir / "sqlite.sql"
        self.db_path = base_dir / "scrap.db"

    async def initialize(self) -> None:
        """초기화 담당"""
        if not self.db_path.exists():
            print(f"[{self.db_path.name}] 파일이 없어 초기화를 시작합니다...")
            await self._init_db()
        else:
            print(f"[{self.db_path.name}] 기존 데이터베이스를 사용합니다.")

    async def _init_db(self):
        sql = self.schema_path.read_text(encoding="utf-8")

        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript(sql)
            await db.commit()

    async def _execute_query(self, query: str, params: Sequence[ScrapResultTuple]) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            # Sqlite에서 외래키 활성화(중요!)
            await db.execute("PRAGMA foreign_keys = ON")
            await db.executemany(query, params)
            await db.commit()

    async def _fetch_rows(self, query: str):
        async with aiosqlite.connect(self.db_path) as db:
            # 결과를 컬럼명 기반으로 접근할 수 있게 해줌 (Row 객체)
            db.row_factory = aiosqlite.Row
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()

                # NamedTuple은 *row 언패킹이 가장 빠르고 깔끔하다. (중요! Select 순서와 NamedTuple의 순서가 일치해야 함!!!!)
                return [ScrapTarget(*row) for row in rows]

    async def select_scrap_targets(self) -> list[ScrapTarget]:
        """
        가져오는 데이터의 개수가 적을 땐 한꺼번에 가져와도 되지만,
        데이터의 양이 많아지고, 데이터를 가져오자마자 워커를 돌리고 싶을 때는 비동기 제너레이터(async for)를 사용하자
        :return:
        """
        query = """
            SELECT seq, type, site_url, site_name, detail_url_format, list_path, id_path, id_attr, id_regex, title_path
            FROM scrap_targets
        """

        return await self._fetch_rows(query)

    async def save_scrap_result(self, results: list[ScrapResult]) -> None:
        query = """
            INSERT INTO scrap_result (detail_url, title, category, target_seq)
            VALUES (?, ?, ?, ?)
        """

        values: list[ScrapResultTuple] = [r.to_tuple() for r in results]

        await self._execute_query(query, values)
