import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple, Sequence

import aiosqlite

"""
TypedDict는 오버헤드가 없고, 단순히 데이터를 전달하는데 유용하다. 
dataclass는 데이터를 단순히 전달하는 것을 넘어, 객체로서 관리하고 싶을 때 적합하다.
"""


class ScrapTarget(NamedTuple):
    seq: int
    type: str
    site_url: str
    site_name: str
    detail_url_format: str
    list_path: str
    id_path: str
    id_attr: str | None
    id_regex: str | None
    title_path: str


class ScrapResultTuple(NamedTuple):
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
    def to_tuple(self) -> ScrapResultTuple:
        """aiosqlite executemany에 바로 사용할 수 있또록 튜플 반환"""
        return ScrapResultTuple(
            self.detail_url, self.title, self.category, self.target_seq
        )


class DatabaseManager:
    def __init__(self) -> None:
        base_dir = Path(__file__).resolve().parent
        self.schema_path = base_dir / "sqlite.sql"
        self.db_path = base_dir / "scrap.db"

        if not self.db_path.exists():
            print(f"[{self.db_path.name}] 파일이 없어 초기화를 시작합니다...")
            asyncio.run(self._init_db())
        else:
            print(f"[{self.db_path.name}] 기존 데이터베이스를 사용합니다.")

    async def _init_db(self):
        sql = self.schema_path.read_text(encoding="utf-8")

        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript(sql)
            await db.commit()

    async def _execute_query(
        self, query: str, params: Sequence[ScrapResultTuple]
    ) -> None:
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

                # aiosqlite.Row 객체는 키 기반 접근이 가능하므로
                # ScrapTarget(**row) 형태로 바로 변환 가능합니다.
                return [ScrapTarget(**dict(row)) for row in rows]

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
