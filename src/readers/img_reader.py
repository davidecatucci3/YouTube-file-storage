import numpy as np
import config
import math
import cv2
import os 

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from tinydb import TinyDB, Query

def img_reader(path_file: str, curr_frame: int) -> np.ndarray:
    '''
    Take in input an image and return the frame array encoded
    
    :param path_file: path of the image file
    :return: frame of size widthxheightx3
    '''

    db = TinyDB('my_data.json')
    User = Query()

    img = cv2.imread(path_file) 

    frame = np.array(img)

    img_height, img_width, _ = img.shape

    block_size = config.block_size
    frame_needed = math.ceil(((img_height * img_width) / ((config.width * config.height) / (block_size*block_size*8))))

    frame_res = np.zeros((frame_needed, config.height, config.width, 3), dtype=np.uint8)

    frame_start = curr_frame
    frame_end = frame_start + (frame_needed * config.frames_per_slide)

    db.insert({'path_file': path_file, 'url': '', 'file type': 'image/', 'frame dim': (img_width, img_height), 'frame needed': frame_needed, 'frame start': frame_start, 'frame end': frame_end, 'key': '', 'nonce': '', 'nonce count': 0, 'num pix char': 0})

    # START
    key = os.urandom(32) 
    nonce = os.urandom(16)

    db.update({'key': key.hex()}, User.path_file == path_file)
    db.update({'nonce': nonce.hex()}, User.path_file == path_file)

    target_doc = db.get(User.path_file == path_file)
    current_id = target_doc.doc_id
    previous_doc = db.get(doc_id=current_id - 1)

    if previous_doc:
        end_nonce_count_prev = previous_doc.get('nonce count', 0)

        start_nonce_count = end_nonce_count_prev + 1
            
        db.update({'start nonce count': end_nonce_count_prev + 1}, doc_ids=[current_id])

        nonce_count = end_nonce_count_prev + 1
    else:
        start_nonce_count = 0

        db.update({'start nonce count': 0}, doc_ids=[current_id])

        nonce_count = 0

    base_nonce_int = int.from_bytes(nonce, 'big')

    fk = 0

    for z in range(frame_needed):
        start_k_for_frame = fk
        k_final = fk

        for r in range(3):
            k = start_k_for_frame
            i, j = 0, 0
            nonce_count = start_nonce_count

            flattened_frame = frame[:, :, r].flatten()

            while k < len(flattened_frame):
                bits_str = bin(flattened_frame[k])[2:].zfill(8)

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

                    if j + block_size > config.height:
                        j = 0            
                        i += block_size

                blocks = np.array(flattened_blocks).reshape((8, block_size, block_size))

                if i + block_size > config.height:
                    break
                
                for idx, (y, x) in enumerate(positions):
                    frame_res[z, :, :, 0][y : y + block_size, x : x + block_size] = blocks[idx]
    
                k += 1 
                nonce_count += 1 
            
            k_final = k

        fk = k_final

    db.update({'end nonce count': nonce_count}, doc_ids=[current_id])
    db.update({'num pix char': fk}, User.path_file == path_file)

    return (img_width, img_height), frame_res, frame_needed

# TODO:
# - extremely slow needs to be speed up using numpy 


