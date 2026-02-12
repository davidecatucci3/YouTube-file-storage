import numpy as np

def txt_reader(file: str) -> list[list[list[int]]]:
    frame = np.ones((720, 1280, 3), dtype=np.uint8)

    return frame