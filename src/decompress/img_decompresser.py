import numpy as np
import config
import cv2
import os

import numpy as np
import config
import cv2
import os

def img_decompresser(frames: list, output_folder: str, frame_needed: int, frame_count: int, img_width: int, img_height: int, data_files=None) -> list:
    if data_files != None:
        name = data_files[frame_count].split('/')[-1]
        filename = os.path.join(output_folder, name)
    else:
        filename = os.path.join(output_folder, 'file.jpg')

    block_size = config.block_size
    count_local_w = 0
    count_local_h = 0
    img_arr = np.zeros((img_height, img_width, 3), dtype=np.uint8)

    for f in range(frame_needed):
        advanced_w = count_local_w
        advanced_h = count_local_h

        for c in range(3):       
            count_h = count_local_h
            count_w = count_local_w

            for i in range(1, len(frames[f]), block_size): # len(frames[f]) return lenght of first dimension so row lenght
                color_first_row = [frames[f][i][j][c] for j in range(1, len(frames[f][i]), block_size)] # take all the color (bit -> color in reader) in the first row of block_size
            
                for j in range(0, len(color_first_row), 8): # each loop j is a pixel / char (formed by 8 bits)
                    colors_pixel = color_first_row[j:j + 8]
                    pixel_bits = ''
                
                    for color in colors_pixel:
                        if color > 127:
                            pixel_bits += '1'
                        else:
                            pixel_bits += '0'

                    pixel = int(pixel_bits, 2)
                    
                    img_arr[count_h, count_w, c] = pixel

                    count_w += 1

                    if count_w >= img_width:
                        count_w = 0
                        count_h += 1
                    
                    if count_h >= img_height:
                        break

                if count_h >= img_height:
                    break

            advanced_w = count_w
            advanced_h = count_h
        
        count_local_w = advanced_w
        count_local_h = advanced_h

    cv2.imwrite(filename, img_arr)

# TODO:
# make it faster 