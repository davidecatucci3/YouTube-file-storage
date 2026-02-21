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

    # 1. convert only the required frames to a NumPy array
    frames_arr = np.array(frames[:frame_needed])
    
    # 2. vectorized spatial sampling
    # Slices starting at index 1 and stepping by block_size to sample one pixel per block
    # Shape becomes: (Frames, Rows, Cols, Channels)
    sampled_pixels = frames_arr[:, 1::block_size, 1::block_size, :]
    
    # 3. reorder axes to match the original loop execution order: (Frames, Channels, Rows, Cols)
    # The original loop executes: for f -> for c -> for i -> for j
    sampled_channels = sampled_pixels.transpose(0, 3, 1, 2)
    
    # 4. flatten the spatial grid (Rows, Cols) so we have a flat stream of data per channel
    F, C, H_blocks, W_blocks = sampled_channels.shape
    blocks_per_frame = H_blocks * W_blocks
    flat_data = sampled_channels.reshape(F, C, blocks_per_frame)
    
    # 5. threshold colors to bits (Instantly replaces the 'if color > 127' loop)
    bits = (flat_data > 127).astype(np.uint8)
    
    # 6. truncate cleanly to multiples of 8 bits 
    # (Matches the original range(0, len, 8) so we don't pack incomplete bytes)
    valid_bits_len = (blocks_per_frame // 8) * 8
    bits = bits[:, :, :valid_bits_len]

    # 7. convert bits back to pixels using C-level bit packing
    pixels = np.packbits(bits, axis=-1) # Shape becomes: (Frames, 3 Channels, Pixels_per_channel)
    
    # 8. realign the RGB channels for each pixel
    # Transpose from (Frames, Channels, Pixels) to (Frames, Pixels, Channels)
    pixels_rgb = pixels.transpose(0, 2, 1)
    
    # 9. flatten frames into one continuous 1D stream of RGB pixels
    stream_rgb = pixels_rgb.reshape(-1, 3)
    
    # 10. truncate to the exact required image size and reshape to 2D image format
    total_pixels = img_height * img_width
    img_arr = stream_rgb[:total_pixels].reshape(img_height, img_width, 3)
    
    # Write to disk
    cv2.imwrite(filename, img_arr)
    
    '''
    # FOR EXPLANATION USING PURE PYTHON OF CODE ABOVE

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

                    # there is not if pixel == 0 :continue because can be exchanged with the color black and jump important data

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
    '''