import numpy as np
import config
import math
import cv2

def img_reader(path_file: str) -> np.ndarray:
    '''
    Take in input an image and return the frame array encoded
    
    :param path_file: path of the image file
    :return: frame of size video_widthxvideo_heightx3
    '''

    img = cv2.imread(path_file) 

    img_arr = np.array(img)
    img_height, img_width, _ = img_arr.shape

    video_width = config.video_width
    video_height = config.video_height
    block_size = config.block_size
    pixel_img = img_height * img_width # number of pixels in image imported
    pixel_img_per_frame = (video_width * video_height) / (block_size*block_size*8) # number of pixels that i can fit in video frame using block_size number
    frame_needed = math.ceil(pixel_img / pixel_img_per_frame)

    frames = np.zeros((frame_needed, video_height, video_width, 3), dtype=np.uint8)

    fk = 0

    for f in range(frame_needed):
        start_k_for_frame = fk
        k_final = fk

        for c in range(3):
            k = start_k_for_frame
            i, j = 0, 0

            flattened_img_arr = img_arr[:, :, c].flatten()

            while k < len(flattened_img_arr): # when i am in the last frame this condition is needed because i >= video_height will never be reached because last frame will never be overoccupied
                pixel_bits = bin(flattened_img_arr[k])[2:].zfill(8) # bits representation of a pixel integer
        
                for bit in pixel_bits:   
                    color = 0 if bit == '0' else 255

                    i_end = min(i + block_size, video_height)
                    j_end = min(j + block_size, video_width)

                    frames[f, i:i_end, j:j_end, c] = color

                    j += block_size

                    if j + block_size > video_width:
                        j = 0
                        i += block_size

                if i >= video_height: # no space in this frame anymore                     
                    break
                
                k += 1
            
            k_final = k

        fk = k_final

    return (img_width, img_height), frames, frame_needed

# TODO:
# - extremely slow needs to be speed up using numpy 
# -  if j + block_size > video_width: j = 0, i += block_size : if video_width % block_size is not equal 0 there will be wasted space at the end (if block_size = 7 there is this problem)