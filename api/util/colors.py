import json
from collections import Counter
from dataclasses import dataclass
from typing import Tuple


@dataclass
class Color:
    id: int
    name: str
    hex: str
    rgb: Tuple[int, int, int]
    material: str
    asset_url: str


def setup_colors():
    colors = {}
    with open("./data/mc_colors.json") as raw_colors:

        parsed = json.load(raw_colors)

        for color in parsed["colors"]:
            hex_val = color["hex"].lstrip('#')
            rgb_tuple = tuple(int(hex_val[i:i + 2], 16) for i in (0, 2, 4))

            colors[color["id"]] = Color(
                id=color["id"],
                name=color["name"],
                hex=color["hex"],
                rgb=rgb_tuple,
                material=color["material"],
                asset_url=color["asset_url"],
            )

    return colors


def get_global_color_tally(number_grid):

    flat_grid = [color_id for row in number_grid for color_id in row]
    tally = Counter(flat_grid)

    return dict(tally)


def get_chunk_color_tally(number_grid, col_idx, row_idx, chunk_size=32):
    x0 = col_idx * chunk_size
    y0 = row_idx * chunk_size
    x1 = x0 + chunk_size
    y1 = y0 + chunk_size

    chunk_tally = Counter()

    for y in range(y0, y1):
        for x in range(x0, x1):
            color_id = number_grid[y][x]
            chunk_tally[color_id] += 1

    return dict(chunk_tally)