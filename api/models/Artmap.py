import datetime

from redis_om import JsonModel


class ArtMap(JsonModel, index=True):
    original_image: str
    rows: int
    cols: int
    use_dither: bool
    created_at: datetime.datetime
    uploaded_by: str
    num_grid: list[list[int]]
    color_counts: dict[int, int]