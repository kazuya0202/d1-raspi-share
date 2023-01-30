from dataclasses import dataclass


@dataclass(init=False, frozen=True)
class DisplayFlags:
    DISP_SLEEP: str = "BB"
    DISP_LEVEL3: str = "A3"
    DISP_LEVEL4: str = "A4"
    DISP_LEVEL5: str = "A5"
