from dataclasses import dataclass
from typing import NamedTuple


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
        return ScrapResultTuple(self.detail_url, self.title, self.category, self.target_seq)
