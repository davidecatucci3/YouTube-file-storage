import numpy as np
import cv2
from PIL import Image
def img_reader(path_file: str, width: int, height: int) -> np.ndarray:
    '''
    Take in input an image and return the resized frame array
    
    :param path_file: path of the image file
    :param width: width frame video
    :param height: height frame video
    :return: frame of size widthxheightx3
    '''

    img = cv2.imread(path_file) 

    frame = np.array(img)

    frame = cv2.resize(frame, (width, height))

    rheight, rwidth, _ = img.shape

    return (rwidth, rheight), frame

