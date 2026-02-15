import numpy as np
import config
import math
import cv2

def img_reader(path_file: str) -> np.ndarray:
    '''
    Take in input an image and return the frame array encoded
    
    :param path_file: path of the image file
    :return: frame of size widthxheightx3
    '''
    
    img = cv2.imread(path_file) 

    frame = np.array(img)

    img_height, img_width, _ = img.shape

    block_size = config.block_size
    frame_needed = math.ceil(((img_height * img_width) / ((config.width * config.height) / (block_size*block_size*8))))

    frame_res = np.zeros((frame_needed, config.height, config.width, 3), dtype=np.uint8)

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

                    i_end = min(i + block_size, config.height)
                    j_end = min(j + block_size, config.width)

                    frame_res[z, :, :, r][i: i_end, j:j_end] = color

                    j += block_size

                    if j + block_size > config.width:
                        j = 0
                        i += block_size
                    
                k += 1

                if i >= config.height:
                    #print('No space in this matrix')
                    
                    break
            
            k_final = k

        fk = k_final

    return (img_width, img_height), frame_res, frame_needed

# TODO:
# - extremely slow needs to be speed up using numpy 