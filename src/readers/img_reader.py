import numpy as np
import math
import cv2

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

    rheight, rwidth, _ = img.shape

    block_size = 5
    frame_needed = math.ceil(((rheight * rwidth) / ((width * height) / (block_size*block_size*8))))

    frame_res = np.zeros((frame_needed, height, width, 3), dtype=np.uint8)

    # START
    fk = 0

    for z in range(frame_needed):
        start_k_for_frame = fk
        k_final = fk

        for r in range(3):
            k = start_k_for_frame
            i, j = 0, 0

            flattened_frame = frame[:, :, r].flatten()

            while k < len(flattened_frame):
                bits = bin(flattened_frame[k])[2:].zfill(8)
        
                for bit in bits:   
                    color = 0 if bit == '0' else 255

                    i_end = min(i + block_size, height)
                    j_end = min(j + block_size, width)

                    frame_res[z, :, :, r][i: i_end, j:j_end] = color

                    j += block_size

                    if j + block_size > width:
                        j = 0
                        i += block_size
                    
                k += 1

                if i >= height:
                    break
            
            k_final = k

        fk = k_final

    return (rwidth, rheight), frame_res, frame_needed

