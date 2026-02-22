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

    yield (img_width, img_height), frame_needed

    # 1. Flatten spatial dimensions but keep the 3 color channels separate
    channels = img.transpose(2, 0, 1).reshape(3, -1)
    
    # 2. Vectorized bit extraction. unpackbits outputs shape (3, total_pixels * 8) instantly
    bits = np.unpackbits(channels, axis=1)
    
    # Map 0s and 1s to 0 and 255
    colors = bits * np.uint8(255)
    total_bits = colors.shape[1]
    
    # 3. Calculate exact block dimensions
    cols_of_blocks = (video_width + block_size - 1) // block_size
    rows_of_blocks = (video_height + block_size - 1) // block_size
    blocks_per_frame = rows_of_blocks * cols_of_blocks
    
    frame_needed = math.ceil(total_bits / blocks_per_frame)
    
    # 4. Generate and yield frames one by one
    for frame_idx in range(frame_needed):
        start_idx = frame_idx * blocks_per_frame
        end_idx = start_idx + blocks_per_frame
        
        # Slice the colors array for just this specific frame
        frame_colors = colors[:, start_idx:end_idx]
        
        # Pad if this is the last frame and it doesn't perfectly fill the grid
        if frame_colors.shape[1] < blocks_per_frame:
            pad_len = blocks_per_frame - frame_colors.shape[1]
            frame_colors = np.pad(frame_colors, ((0, 0), (0, pad_len)), constant_values=0)
            
        # 5. Reshape bits into a 3D grid of blocks: (3 channels, rows, cols)
        block_grid = frame_colors.reshape(3, rows_of_blocks, cols_of_blocks)
        
        # Transpose to shape: (rows, cols, 3 channels) so it acts like standard image data
        block_grid = block_grid.transpose(1, 2, 0)
        
        # 6. Scale 1x1 blocks up to pixel blocks using np.repeat
        pixel_grid = np.repeat(np.repeat(block_grid, block_size, axis=0), block_size, axis=1)
        
        # 7. Crop precisely to video bounds
        frame = pixel_grid[:video_height, :video_width, :]
        
        yield frame

    '''
    # FOR EXPLANATION USING PURE PYTHON OF CODE ABOVE

    fk = 0

    # if j + block_size > video_width: j = 0, i += block_size : if video_width % block_size is not equal 0 there will be wasted space at the end (if block_size = 7 there is this problem)
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

                k += 1
                        
                if i >= video_height: # no space in this frame anymore                     
                    break
            
            k_final = k

        fk = k_final
    
    return (img_width, img_height), frames, frame_needed
    '''
