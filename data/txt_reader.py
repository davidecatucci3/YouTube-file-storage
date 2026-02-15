import numpy as np
import mmap
import cv2

def txt_reader(file_path: str, width: int, height: int) -> list[list[list[int]]]:
    frame_gray = np.zeros((height, width), dtype=np.uint8)

    i, j = 0, 0
    k = 0
    block_size = 5
    
    with open(file_path, 'rb') as f:
        #!use numpy for faster matrix operation on it
        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ) as mm:
            while k < len(mm):
                bits = bin(mm[k])[2:].zfill(8)
      
                for bit in bits:   
                    color = 0 if bit == '0' else 255

                    i_end = min(i + block_size, height)
                    j_end = min(j + block_size, width)

                    frame_gray[i: i_end, j:j_end] = color

                    j += block_size

                    if j + block_size > width:
                        j = 0
                        i += block_size
                
                k += 1

                if i >= height:
                    break
    
    # divider: frame_gray[i // (width - 1)][i: i + 20] = [i for i in range(120, 140)] #!avoid to write file for each separate frame
    
    frame_bgr = cv2.cvtColor(frame_gray, cv2.COLOR_GRAY2BGR) # he just take the pixel gray like 93 and copy it 3 times lie 93 -> [93, 93, 93]
    
    return frame_bgr, block_size

