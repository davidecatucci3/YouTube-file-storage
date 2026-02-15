import config
import os

def txt_decompresser(frame: list, output_folder: str, frame_count: int, data_files: list[str]) -> list:
    #!use numpy for faster matrix operation on it
    filename = os.path.join(output_folder, f"frame_{frame_count:04d}.{data_files[frame_count].split('.')[-1]}")
    
    txt = ''
  
    for i in range(1, len(frame), config.block_size):
        frame_i = [frame[i][j][0] for j in range(1, len(frame[i]), config.block_size)] 
      
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
# speedup