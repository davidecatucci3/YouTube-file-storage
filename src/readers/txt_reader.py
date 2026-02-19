import numpy as np
import config
import math

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
    tot_letters = count_letters_file(path_file)
    letters_per_frame = (video_width * video_height) // (block_size*block_size*8)
    frame_needed = math.ceil(tot_letters / letters_per_frame)

    frames = np.zeros((frame_needed, video_height, video_width, 3), dtype=np.uint8)

    char_stream = get_character_generator(path_file)

    # START
    for f in range(frame_needed):
        k = 0
        i, j = 0, 0

        while k < letters_per_frame:
            try:
                char = next(char_stream)
            except StopIteration:
                break
            
            char_code = ord(char) % 256
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

# TODO:
# - now i am using just one matrix of the 3 avaialble for colors to store text i could use the other two channels to store other data or just more of the input data (if i solve this i can do one decompress.py)
# - if i need to store more differente data in same frame i need to implement separation pattern (this is frame needed is one and there are others with frame_needed=1)
# - extremely slow if large large text like 1000+ pages of books needs to be speed up using numpy 
# - encoding (for all language and chars 8 bits is not sufficent)

