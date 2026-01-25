from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple, Sequence

import aiosqlite

"""
TypedDict는 오버헤드가 없고, 단순히 데이터를 전달하는데 유용하다. 
dataclass는 데이터를 단순히 전달하는 것을 넘어, 객체로서 관리하고 싶을 때 적합하다.
"""


class ScrapRow(NamedTuple):
    detail_url: str
    title: str
    category: str | None
    target_seq: int


@dataclass(frozen=True)
class ScrapResult:
    detail_url: str
    title: str
    target_seq: int
    category: str | None = None

    # 반환 타입을 tuple[detail_url, title, category, target_seq] 이렇게 하고 싶은
    def to_tuple(self) -> ScrapRow:
        """aiosqlite executemany에 바로 사용할 수 있또록 튜플 반환"""
        return ScrapRow(self.detail_url, self.title, self.category, self.target_seq)


class DatabaseManager:
    def __init__(self) -> None:
        base_dir = Path(__file__).resolve().parent
        self.schema_path = base_dir / "sqlite.sql"
        self.db_path = base_dir / "scrap.db"

    async def init_db(self):
        sql = self.schema_path.read_text(encoding="utf-8")

        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript(sql)
            await db.commit()

    async def _execute_query(self, query: str, params: Sequence[ScrapRow]) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            # Sqlite에서 외래키 활성화(중요!)
            await db.execute("PRAGMA foreign_keys = ON")
            await db.executemany(query, params)
            await db.commit()

    async def _fetch_rows(self, query: str):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()
        return rows

    async def select_scrap_targets(self):
        query = """
            SELECT * 
            FROM scrap_targets
        """

        return await self._fetch_rows(query)

    async def save_scrap_result(self, results: list[ScrapResult]) -> None:
        query = """
            INSERT INTO scrap_result (detail_url, title, category, target_seq)
            VALUES (?, ?, ?, ?)
        """

        values: list[ScrapRow] = [r.to_tuple() for r in results]

        await self._execute_query(query, values)
