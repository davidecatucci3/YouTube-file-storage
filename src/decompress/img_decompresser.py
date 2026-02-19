import numpy as np
import config
import cv2
import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from tinydb import TinyDB, Query

def img_decompresser(frame: list, output_folder: str, frame_count: int, frame_needed: int, data_files=None, imgs_size=None, w=None, h=None) -> list:
    if data_files != None:
        name = data_files[frame_count].split('/')[-1]
        filename = os.path.join(output_folder, name)
    else:
        filename = os.path.join(output_folder, 'file.jpg')

    os.makedirs('out', exist_ok=True)

    block_size = config.block_size
    input_h, input_w = 1080, 1920

    if imgs_size != None:
        target_w, target_h = imgs_size[frame_count]
    else:
        target_w, target_h = w, h

    db = TinyDB('my_data.json')
    User = Query()

    res = db.get(User.path_file == data_files[frame_count])

    key = bytes.fromhex(res['key'])
    nonce = bytes.fromhex(res['nonce'])
    start_nonce_count = res['start nonce count']
    num_pix_char = res['num pix char']

    pix_read = 0
    base_nonce_int = int.from_bytes(nonce, 'big')

    for z in range(frame_needed):
        for c in range(3):
            for i in range(1, len(frame[z]), config.block_size):
                frame_i = [frame[z][i][j][c] for j in range(1, len(frame[z][i]), config.block_size)] 
            
                for j in range(0, len(frame_i), 8):
                    if chars_read >= num_pix_char:
                        break
            
                    pixels = frame_i[j:j + 8]

                    current_nonce_int = (base_nonce_int + start_nonce_count) % (2**128)
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

                    start_nonce_count += 1
                    chars_read += 1

    cv2.imwrite(filename, img_final)
