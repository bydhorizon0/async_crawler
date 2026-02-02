from typing import NamedTuple


class ScrapTarget(NamedTuple):
    seq: int
    type: str
    pagination_path: str
    site_url: str
    site_name: str
    detail_url_format: str
    list_path: str
    id_path: str
    id_attr: str | None
    id_regex: str | None
    title_path: str
