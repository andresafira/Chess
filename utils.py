from constants import *
from typing import Union, Tuple


def isvalid(position: tuple[int, int]) -> bool:
    for i in position:
        if i < 0 or i > 7:
            return False
    return True


def get_position(coordinate: tuple[int, int]) -> Union[Tuple[int, int], None]:
    if coordinate is None:
        return None
    return int((coordinate[0] - OFFSET_X) / BLOCK_W), int((coordinate[1] - OFFSET_PIXEL_Y) / BLOCK_H)
