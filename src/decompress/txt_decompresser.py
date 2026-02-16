import config
import os

def txt_decompresser(frame: list, output_folder: str, frame_count: int,  frame_needed: int, data_files=None) -> list:
    if data_files != None:
        name = data_files[frame_count].split('/')[-1]
        filename = os.path.join(output_folder, name)
    else:
        filename = os.path.join(output_folder, 'file.txt')
    
    txt = ''
 
    for z in range(frame_needed):
        for i in range(1, len(frame[z]), config.block_size):
            frame_i = [frame[z][i][j][0] for j in range(1, len(frame[z][i]), config.block_size)] 
        
            for j in range(0, len(frame_i), 8):
                pixels = frame_i[j:j + 8]
                bits = ''
            
                for p in pixels:
                    if p > 127:
                        bits += '1'
                    else:
                        bits += '0'

                char_code = int(bits, 2)
                
                # stop if we hit NULL (End of data)
                if char_code == 0: # 0 in ascii UNICODE correspond to Null (invisible)
                    continue
            
                txt += chr(char_code)
              
    with open(filename, 'w') as f:
        f.write(txt)

# TODO:
# IF ONLY 10% OR LESS LETTERS OF A WORDS ARE WRONG I CAN USE AI OR WORD RECONSTRUCTION SO IT DOEDS NOT NEED TO BE PERFECT THE DECOMPRESSION JUST LESS LETTERS PER WORDS SO I CAN RECONSTRUCIT IN FEW TIME (or ...)
# speedup
