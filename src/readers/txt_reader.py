import numpy as np
import config
import math

from itertools import islice

def get_character_generator(path_file, chunk_size=8192):
    '''
    Generator that reads a file piece-by-piece (chunk_size chars),
    decoding correctly without loading the whole file into RAM.
    '''

    with open(path_file, 'r', encoding='utf-8') as f:
        while True:
            chunk = f.read(chunk_size)

            if not chunk:
                break

            for char in chunk:
                yield char

def count_letters_file(path_file: str) -> int:
    count = 0
    
    with open(path_file, 'r', encoding='utf-8', errors='replace') as f:
        for chunk in iter(lambda: f.read(8192), ''):
            count += len(chunk)

    return count

def txt_reader(path_file: str) -> np.ndarray:
    '''
    Take in input a text file and encode it in a matrix image representation to be putted in the video
    
    :param path_file: file path of the text file
    :return: matrix representation of size (width, height, 3)
    '''

    video_width = config.video_width
    video_height = config.video_height
    block_size = config.block_size
    tot_chars = count_letters_file(path_file)
    chars_per_frame = (video_width * video_height) // (block_size*block_size*8)
    frame_needed = math.ceil(tot_chars / chars_per_frame)
    frames = np.zeros((frame_needed, video_height, video_width, 3), dtype=np.uint8)

    # 1. fetch all required characters from stream at once
    char_stream = get_character_generator(path_file)
    chars = list(islice(char_stream, tot_chars))
    
    # 2. convert characters to an arry of 8-bit integer
    char_codes = np.array([ord(c) % 256 for c in chars], dtype=np.uint8)

    # 3. vectorized bit extractions (this replaces the string binary conversion), np.unpackbits instantly turns an array of uint8 into an array of 0s and 1s
    bits = np.unpackbits(char_codes)

    # 4. map bits to colors (0 -> 0, 1 -> 255)
    colors = bits * np.uint8(255)

    # 5. calculate dimensions
    bits_per_frame = chars_per_frame * 8
    actual_frames = (len(colors) + bits_per_frame - 1) // bits_per_frame
    
    cols_of_blocks = (video_width + block_size - 1) // block_size
    rows_of_blocks = (video_height + block_size - 1) // block_size
    blocks_per_frame_grid = rows_of_blocks * cols_of_blocks
    
    # 6. pad colors so they fit perfectly into whole frames
    pad_len = (actual_frames * bits_per_frame) - len(colors)

    if pad_len > 0:
        colors = np.pad(colors, (0, pad_len), constant_values=0)

    # group colors by frame
    frame_colors = colors.reshape(actual_frames, bits_per_frame)

    # 7. map the flat bits into a 2D grid of blocks for each frame, create an empty grid in case bits_per_frame < blocks_per_frame_grid
    block_grids = np.zeros((actual_frames, blocks_per_frame_grid), dtype=np.uint8)

    # copy the bits into our block grid (cutting off safely if bits exceed screen space)
    copy_len = min(bits_per_frame, blocks_per_frame_grid)
    block_grids[:, :copy_len] = frame_colors[:, :copy_len]
    
    # reshape into a 2D image format: (frames, height_in_blocks, width_in_blocks)
    block_grids = block_grids.reshape(actual_frames, rows_of_blocks, cols_of_blocks)

    # 8. scale blocks to actual pixels using np.repeat (Replaces the i/j coordinate loops), this stretches the grid on the Y-axis, then the X-axis
    pixel_grids = np.repeat(np.repeat(block_grids, block_size, axis=1), block_size, axis=2)
    
    # 9. crop back to exact video dimensions (if block_size didn't perfectly divide height/width)
    pixel_grids = pixel_grids[:, :video_height, :video_width]
    
    # 10. assign the generated pixel grids to channel 0 of the original frames array
    frames[:actual_frames, :, :, 0] = pixel_grids

    '''    
    # FOR EXPLANATION USING PURE PYTHON OF CODE ABOVE
    
    for f in range(frame_needed):
        k = 0
        i, j = 0, 0

        while k < chars_per_frame:
            try:
                char = next(char_stream)
            except StopIteration:
                break
            
            char_code = ord(char) % 256 # recognize only 8 bits so 256 chars (not all of them that are 1024)
            char_bits = bin(char_code)[2:].zfill(8)
        
            for bit in char_bits:   
                color = 0 if bit == '0' else 255

                i_end = min(i + block_size, video_height)
                j_end = min(j + block_size, video_width)

                frames[f, i:i_end, j:j_end, 0] = color

                j += block_size    

                if j + block_size > video_width:
                    j = 0
                    i += block_size      

            k += 1    
    '''  
            
    return frames, frame_needed

# TODO:
# now i am using just one matrix of the 3 avaialble for colors to store text i could use the other two channels to store other data or just more of the input data (if i solve this i can do one decompress.py)
# if i need to store more differente data in same frame i need to implement separation pattern (this is frame needed is one and there are others with frame_needed=1)
# encoding (for all language and chars 8 bits is not sufficent)s