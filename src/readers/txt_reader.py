import numpy as np
import config
import math
import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from tinydb import TinyDB, Query

def get_character_generator(file_path, chunk_size=8192):
    '''
    Generator that reads a file piece-by-piece (chunk_size chars),
    decoding correctly without loading the whole file into RAM.
    '''

    with open(file_path, 'r', encoding='utf-8') as f:
        while True:
            chunk = f.read(chunk_size)

            if not chunk:
                break

            for char in chunk:
                yield char

def count_letters_file(file_path: str) -> int:
    count = 0

    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            for chunk in iter(lambda: f.read(8192), ''):
                count += len(chunk)
    except FileNotFoundError:
        return 0
    
    return count

def txt_reader(file_path: str, curr_frame: int) -> np.ndarray:
    '''
    Take in input a text file and encode it in a matrix image representation to be putted in the video
    
    :param file_path: file path of the text file
    :param width: width size of video frame
    :param height: height size of video frame
    :return: matrix representation of size (width, height, 3)
    '''

    db = TinyDB('my_data.json')
    User = Query()

    block_size = config.block_size
    letters_per_frame = (config.width * config.height) // (block_size*block_size*8)
    tot_letters = count_letters_file(file_path)
    frame_needed = math.ceil(tot_letters / letters_per_frame)
    frame_res = np.zeros((frame_needed, config.height, config.width, 3), dtype=np.uint8)
    char_stream = get_character_generator(file_path)

    frame_start = curr_frame
    frame_end = frame_start + (frame_needed * config.frames_per_slide)
    db.insert({'path_file': file_path, 'url': '', 'file type': 'text/', 'frame dim': (0, 0), 'frame needed': frame_needed, 'frame start': frame_start, 'frame end': frame_end, 'key': '', 'nonce': '', 'start nonce count': 0, 'end nonce count': 0, 'num pix char': 0})
            
    
    # START
    key = os.urandom(32) 
    nonce = os.urandom(16)

    db.update({'key': key.hex()}, User.path_file == file_path)
    db.update({'nonce': nonce.hex()}, User.path_file == file_path)

    target_doc = db.get(User.path_file == file_path)
    current_id = target_doc.doc_id
    previous_doc = db.get(doc_id=current_id - 1)

    if previous_doc:
        end_nonce_count_prev = previous_doc.get('nonce count', 0)
            
        db.update({'start nonce count': end_nonce_count_prev + 1}, doc_ids=[current_id])

        nonce_count = end_nonce_count_prev + 1
    else:
        db.update({'start nonce count': 0}, doc_ids=[current_id])

        nonce_count = 0

    base_nonce_int = int.from_bytes(nonce, 'big')

    for z in range(frame_needed):
        local_k = 0
        i, j = 0, 0

        while local_k < letters_per_frame:
            try:
                char = next(char_stream)
            except StopIteration:
                break
            
            char_code = ord(char) % 256
            bits_str = bin(char_code)[2:].zfill(8)

            pixel_arr = [0 if b == '0' else 255 for b in bits_str]
            pixel_arr_bytes = bytes(pixel_arr)

            current_nonce_int = (base_nonce_int + nonce_count) % (2**128)
            current_nonce_bytes = current_nonce_int.to_bytes(16, 'big')

            cipher = Cipher(algorithms.AES(key), modes.CTR(current_nonce_bytes))
            encryptor = cipher.encryptor()

            pixel_arr_bytes_enc = encryptor.update(pixel_arr_bytes) + encryptor.finalize()

            pixel_arr_enc = list(pixel_arr_bytes_enc)

            flattened_blocks = []
            positions = []

            for color in pixel_arr_enc:
                flattened_blocks.extend([color] * block_size ** 2)
                
                positions.append((i, j))

                j += block_size

                if j + block_size > config.width:
                    j = 0            
                    i += block_size

            blocks = np.array(flattened_blocks).reshape((8, block_size, block_size))

            for idx, (y, x) in enumerate(positions):
                frame_res[z, :, :, 0][y : y + block_size, x : x + block_size] = blocks[idx]
   
            local_k += 1 
            nonce_count += 1 

    db.update({'end nonce count': nonce_count}, doc_ids=[current_id])
    db.update({'num pix char': local_k}, User.path_file == file_path)

    return frame_res, frame_needed

# TODO:
# - now i am using just one matrix of the 3 avaialble for colors to store text i could use the other two channels to store other data or just more of the inout data
# - if i need to store more differente data in same frame i need to implement separation pattern
# - extremely slow if large large text like 1000+ pages of books needs to be speed up using numpy 
# - encoding (for all language and chars 8 bits is not sufficent)


'''x, _ = txt_reader('a.txt')
txt = ''
nonce_count = 0
chars_read = 0
total_chars_to_read = 117
base_nonce_int = int.from_bytes(nonce, 'big')

for i in range(1, len(x[0]), config.block_size):
            frame_i = [x[0][i][j][0] for j in range(1, len(x[0][i]), config.block_size)] 

            for j in range(0, len(frame_i), 8):
                if chars_read >= total_chars_to_read:
                    break

                pixels = frame_i[j:j + 8]

                current_nonce_int = (base_nonce_int + nonce_count) % (2**128)
                current_nonce_bytes = current_nonce_int.to_bytes(16, 'big')

                cipher = Cipher(algorithms.AES(key), modes.CTR(current_nonce_bytes))
                decryptor = cipher.decryptor()
                
                decrypted_bytes = decryptor.update(bytes(pixels)) + decryptor.finalize()

                pixels_dec = list(decrypted_bytes)

                bits = ''
                
                for p in pixels_dec:
                    if p > 127:
                        bits += '1'
                    else:
                        bits += '0'

                char_code = int(bits, 2)
            
                txt += chr(char_code)

                nonce_count += 1
                chars_read += 1
        
print(txt)'''