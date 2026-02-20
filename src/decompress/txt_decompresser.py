import config
import os

def txt_decompresser(frames: list, output_folder: str, frame_count: int,  frame_needed: int, data_files=None) -> list:
    if data_files != None:
        name = data_files[frame_count].split('/')[-1]
        filename = os.path.join(output_folder, name)
    else:
        filename = os.path.join(output_folder, 'file.txt')
    
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

# TODO:
# speedup
