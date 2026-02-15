import numpy as np
import config
import math
import mmap
import re

def count_letters_file(file_path: str) -> int:
    with open(file_path, "rb") as f:
        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ) as mm:
            return sum(1 for _ in re.finditer(b'[a-zA-Z]', mm))

def txt_reader(file_path: str) -> np.ndarray:
    '''
    Take in input a text file and encode it in a matrix image representation to be putted in the video
    
    :param file_path: file path of the text file
    :param width: width size of video frame
    :param height: height size of video frame
    :return: matrix representation of size (width, height, 3)
    '''

    k = 0
    block_size = config.block_size
    letters_per_frame = (config.width * config.height) // (block_size*block_size*8)
    tot_letters = count_letters_file(file_path)
    frame_needed = math.ceil(tot_letters / letters_per_frame)
    frame_res = np.zeros((frame_needed, config.height, config.width, 3), dtype=np.uint8)

    # START
    with open(file_path, 'rb') as f:
        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ) as mm:
            for z in range(frame_needed):
                local_k = 0
                i, j = 0, 0

                while local_k < letters_per_frame:
                    if k >= len(mm):
                        break

                    bits = bin(mm[k])[2:].zfill(8)
        
                    for bit in bits:   
                        color = 0 if bit == '0' else 255

                        i_end = min(i + block_size, config.height)
                        j_end = min(j + block_size, config.width)

                        frame_res[z, :, :, 0][i: i_end, j:j_end] = color

                        j += block_size

                        if j + block_size > config.width:
                            j = 0
                            i += block_size
                    
                    local_k += 1
                    k += 1

                    if i >= config.height:
                        #print('No space in this matrix')

                        break
    
    return frame_res, frame_needed

# TODO:
# - now i am using just one matrix of the 3 avaialble for colors to store text i could use the other two channels to store other data or just more of the inout data
# - if i need to store more differente data in same frame i need to implement separation pattern
# - extremely slow if large large text like 1000+ pages of books needs to be speed up using numpy 