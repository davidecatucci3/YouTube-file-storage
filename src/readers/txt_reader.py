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

    yield frame_needed

    bits_per_frame = chars_per_frame * 8
    cols_of_blocks = (video_width + block_size - 1) // block_size
    rows_of_blocks = (video_height + block_size - 1) // block_size
    blocks_per_frame_grid = rows_of_blocks * cols_of_blocks

    # 1. open the stream
    char_stream = get_character_generator(path_file)
    
    while True:
        # 2. Fetch ONLY the characters needed for a single frame
        chunk_chars = list(islice(char_stream, chars_per_frame))
        
        if not chunk_chars:
            break # Reached end of file
            
        # 3. Convert characters to an array of 8-bit integers
        char_codes = np.array([ord(c) % 256 for c in chunk_chars], dtype=np.uint8)

        # 4. Vectorized bit extraction
        bits = np.unpackbits(char_codes)

        # 5. Map bits to colors (0 -> 0, 1 -> 255)
        colors = bits * np.uint8(255)

        # 6. Pad if this is the very last frame and it's partially empty
        if len(colors) < bits_per_frame:
            colors = np.pad(colors, (0, bits_per_frame - len(colors)), constant_values=0)

        # 7. Map flat bits into a 2D grid of blocks for this specific frame
        block_grid = np.zeros(blocks_per_frame_grid, dtype=np.uint8)
        copy_len = min(bits_per_frame, blocks_per_frame_grid)
        block_grid[:copy_len] = colors[:copy_len]
        
        # Reshape into a 2D image format: (height_in_blocks, width_in_blocks)
        block_grid = block_grid.reshape(rows_of_blocks, cols_of_blocks)

        # 8. Scale blocks to actual pixels using np.repeat
        pixel_grid = np.repeat(np.repeat(block_grid, block_size, axis=0), block_size, axis=1)
        
        # 9. Crop back to exact video dimensions
        pixel_grid = pixel_grid[:video_height, :video_width]
        
        # 10. Create the 3-channel frame and assign the grid to channel 0 (Red or Blue depending on RGB/BGR)
        frame = np.zeros((video_height, video_width, 3), dtype=np.uint8)
        frame[:, :, 0] = pixel_grid
        
        # Yield the single frame and let Python garbage-collect the intermediate arrays
        yield frame

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

    return frames, frame_needed 
    '''       

# TODO:
# now i am using just one matrix of the 3 avaialble for colors to store text i could use the other two channels to store other data or just more of the input data (if i solve this i can do one decompress.py)
# encoding (for all language and chars 8 bits is not sufficent)