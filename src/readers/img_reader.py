import numpy as np
import cv2

from PIL import Image

def img_reader(path_file: str, width: int, height: int) -> list[list[list[int]]]:
    img = Image.open(path_file).convert('RGB')

    img_resized = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    frame = cv2.resize(img_resized, (width, height))

    return frame

