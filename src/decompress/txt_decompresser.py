import numpy as np
import config
import os

def txt_decompresser(frames: list, output_folder: str, frame_count: int,  frame_needed: int, data_files=None) -> list:
    if data_files != None:
        name = data_files[frame_count].split('/')[-1]
        filename = os.path.join(output_folder, name)
    else:
        filename = os.path.join(output_folder, 'file.txt')
    
    # 1. convert frames list to a numpy array (only take the frames we need), shape becomes: (frame_needed, height, width, channels)
    frames_arr = np.array(frames[:frame_needed])

    # 2. vectorized spatial sampling (Replaces the nested i and j loops), we slice starting at index 1, stepping by block_size, taking only channel 0
    sampled_pixels = frames_arr[:, 1::config.block_size, 1::config.block_size, 0]

    # flatten the 3D grid of sampled blocks into a 1D stream of pixel values
    flat_pixels = sampled_pixels.flatten()

    # 3. vectorized thresholding (Replaces the > 127 if/else logic), this instantly creates an array of 0s and 1s
    bits = (flat_pixels > 127).astype(np.uint8)
    
    # ensure our bit stream is perfectly divisible by 8 to avoid packbits errors
    remainder = len(bits) % 8
    if remainder != 0:
        bits = bits[:-remainder]
        
    # 4. vectorized bit-to-byte conversion (Replaces string binary to int logic), np.packbits groups every 8 bits and turns them into an 8-bit integer
    byte_array = np.packbits(bits)
    
    # 5. filter out NULL characters (char_code == 0)
    valid_bytes = byte_array[byte_array != 0]
    
    # 6. fast string conversion, tobytes() creates a raw byte string, and decoding via latin1 matches chr(0-255) behavior perfectly
    txt = valid_bytes.tobytes().decode('utf-8')
    
    # write the entire chunk to disk at once
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(txt)

    '''
    # FOR EXPLANATION USING PURE PYTHON OF CODE ABOVE

    txt = ''
 
    for f in range(frame_needed):
        for i in range(1, len(frames[f]), config.block_size): # len(frames[f]) return lenght of first dimension so row lenght
            color_first_row = [frames[f][i][j][0] for j in range(1, len(frames[f][i]), config.block_size)] # take all the color (bit -> color in reader) in the first row of block_size
        
            for j in range(0, len(color_first_row), 8): # each loop j is a pixel / char (formed by 8 bits)
                colors_char = color_first_row[j:j + 8]
                char_bits = ''
            
                for color in colors_char:
                    if color > 127:
                        char_bits += '1'
                    else:
                        char_bits += '0'

                char_code = int(char_bits, 2)
                
                # stop if we hit NULL (End of data)
                if char_code == 0: # 0 in ascii UNICODE correspond to Null (invisible)
                    continue
            
                txt += chr(char_code)
              
    with open(filename, 'w') as f:
        f.write(txt)
    '''
