import numpy as np
import mmap
import cv2

def txt_reader(file_path: str, width: int, height: int) -> list[list[list[int]]]:
    frame_gray = np.zeros((height, width), dtype=np.uint8)

    i = 0
    k = 0

    with open(file_path, 'rb') as f:
        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ) as mm:
            while k < len(mm):
                frame_gray[i // (width - 1), i] = mm[k]

                k += 1
                i += 1

                if i >= height:
                    i = 0

    frame_bgr = cv2.cvtColor(frame_gray, cv2.COLOR_GRAY2BGR) # he just take the pixel gray like 93 and copy it 3 times lie 93 -> [93, 93, 93]

    return frame_bgr