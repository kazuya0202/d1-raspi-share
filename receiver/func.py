from __future__ import annotations
from pathlib import Path

from typing import Optional

from PIL import Image


def parse_data(receive_data: str) -> str:
    data = receive_data[11:]
    data_list = data.split(",")

    # xx,--,--,--,--,--,--,-- のxxだけ取得する
    return data_list[0]


def load_image_with_resize(filepath: Path, size: Optional[tuple[int, int]] = None) -> Image.Image:
    img = Image.open(filepath)
    if size is not None:
        img = img.resize(size)
    return img
