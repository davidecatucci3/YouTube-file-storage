import numpy as np
import config
import mmap
import cv2

def txt_reader(file_path: str) -> np.ndarray:
    '''
    Take in input a text file and encode it in a matrix image representation to be putted in the video
    
    :param file_path: file path of the text file
    :param width: width size of video frame
    :param height: height size of video frame
    :return: matrix representation of size (width, height, 3)
    '''

    frame_gray = np.zeros((config.height, config.width), dtype=np.uint8)

    i, j = 0, 0
    k = 0
    block_size = config.block_size

    with open(file_path, 'rb') as f:
        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ) as mm:
            while k < len(mm):
                bits = bin(mm[k])[2:].zfill(8)
      
                for bit in bits:   
                    color = 0 if bit == '0' else 255

                    i_end = min(i + block_size, config.height)
                    j_end = min(j + block_size, config.width)

                    frame_gray[i: i_end, j:j_end] = color

                    j += block_size

                    if j + block_size > config.width:
                        j = 0
                        i += block_size
                
                k += 1

                if i >= config.height:
                    #print('No space in this matrix')

                    break
    
    frame_bgr = cv2.cvtColor(frame_gray, cv2.COLOR_GRAY2BGR) # he just take the pixel gray like 93 and copy it 3 times lie 93 -> [93, 93, 93]
    
    return frame_bgr


# TODO:
# - now i am using just one matrix of the 4 avaialble for colors to store text i could use the other two channels to store other data or just more of the inout data
# - if i need to store more differente data in same frame i need to implement separation pattern
# - possible speedup