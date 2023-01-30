from __future__ import annotations

from dataclasses import dataclass


@dataclass(init=False, frozen=True)
class Config:
    DISPLAY_SIZE: tuple[int, int] = (800, 480)  # todo: check display size
    DISPLAY_HEIHGT: int = 480  # todo: check display size
    DISPLAY_WIDTH: int = 800  # todo: check display size
