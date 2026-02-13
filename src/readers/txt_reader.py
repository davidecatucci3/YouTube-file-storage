import numpy as np
import mmap

def txt_reader(file_path: str, width: int, height: int) -> list[list[list[int]]]:
    frame = np.zeros((width, height), dtype=np.uint8)

    i = 0
    k = 0

    with open(file_path, 'rb') as f:
        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ) as mm:
            while k < len(mm):
                frame[i // width, i] = mm[k]

                k += 1
                i += 1

    return frame
