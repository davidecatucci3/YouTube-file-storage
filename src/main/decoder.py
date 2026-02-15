'''
The decoder get in input the video downloaded from youtube and exctract all the frames that corresponds to the data stored in the video
'''

import numpy as np
import magic
import cv2
import os

#? PUT IN DECOMPRESSER
def img_to_txt(frame: list, output_folder: str, frame_count: int, block_size: int, data_files: list[str]) -> list:
    #!use numpy for faster matrix operation on it
    filename = os.path.join(output_folder, f"frame_{frame_count:04d}.{data_files[frame_count].split('.')[-1]}")
    
    txt = ''
  
    for i in range(1, len(frame), block_size):
        frame_i = [frame[i][j][0] for j in range(1, len(frame[i]), block_size)] 
      
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

#? PUT IN DECOMPRESSER
def img_to_imgback(frame: list, output_folder: str, frame_count: int, block_size: int, all_frame_needed: list[int], data_files: list[str], imgs_size) -> list:
    filename = os.path.join(output_folder, f"frame_{frame_count:04d}.{data_files[frame_count].split('.')[-1]}")

    os.makedirs('out', exist_ok=True)

    block_size = 5
    input_h, input_w = 1080, 1920
    target_w, target_h = imgs_size[frame_count]

    # A. Sampling (Center of blocks)
    offset = block_size // 2
    sampled_grid = frame[:, offset:input_h:block_size, offset:input_w:block_size, :]

    # B. Thresholding
    bits_recovered = (sampled_grid > 127).astype(np.uint8)

    # C. Flatten to bit stream
    # Shape: (Total_Bits_Vertical, 3)
    # Because of our encoder Transpose, this is now correctly ordered:
    # Row 0: [Pixel0_Bit0_B, Pixel0_Bit0_G, Pixel0_Bit0_R]
    flat_bits = bits_recovered.reshape(-1, 3)

    # D. Truncate Padding
    total_pixels = target_w * target_h
    # We need exactly 8 rows per pixel (8 bits)
    required_rows = total_pixels * 8
    flat_bits = flat_bits[:required_rows]

    # E. Reshape for Packing
    # We group every 8 rows together. 
    # Shape becomes: (Pixels, 8_Bits, 3_Channels)
    flat_bits_grouped = flat_bits.reshape(total_pixels, 8, 3)

    # F. Pack Bits
    # We pack along axis 1 (the 8 bits).
    # Result: (Pixels, 1, 3)
    img_packed = np.packbits(flat_bits_grouped, axis=1)

    # G. Final Reshape
    img_final = img_packed.reshape(target_h, target_w, 3)

    cv2.imwrite(filename, img_final)

def decoder(data_files: str, file_path: str, imgs_size: list[tuple[int, int]], block_size: int, all_frame_needed: list[int], frames_per_slide: int, video_width: int, video_height) -> None:
    '''
    The decoder get in input the video downloaded from youtube and exctract all the frames that correpsonds to the data stored in the video

    :param data_files: list of all file path of each data in video
    :param file_path: Path for the video
    :param imgs_size: list of tuple where each tuple contains real width and height of image before resizing
    :param block_size: called also PIXEL_SIZE used for avoid youtube compression
    :paran all_frame_needed: number of frame needed for ith data file to be complitely stored in the video
    :param frames_per_slide: how many frames need a single frame (strange!)
    '''

    cap = cv2.VideoCapture(file_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open {file_path}")

        return

    output_folder = 'out'
    count_files = 0

    print("Starting extraction... this may take a while.")

    while True:
        ret, frame = cap.read()

        if not ret:
            break
        
        if all_frame_needed[count_files] > 1:
            j = 0
            frame_count_local = 0
            inp_img = np.zeros((all_frame_needed[count_files], video_height, video_width, 3))

            while frame_count_local < all_frame_needed[count_files] * frames_per_slide:
                if frame_count_local % frames_per_slide == 0:
                    inp_img[j] = frame

                    j += 1
                    
                frame_count_local += 1
            
                ret, frame = cap.read()
            
            img_to_imgback(inp_img, output_folder, count_files, block_size, all_frame_needed, data_files, imgs_size)

            count_files += 1
        else:
            file_type = magic.from_file(data_files[count_files], mime=True)
                
            if file_type.startswith('image/'):
                # frame require (frame_needed, width, height, 3) as input
                frame = cv2.resize((1, frame.shape[0], frame.shape[1], 3))

                img_to_imgback(frame, output_folder, count_files, block_size, all_frame_needed, data_files, imgs_size)
            elif file_type.startswith('text/'):
                img_to_txt(frame, output_folder, count_files, block_size, data_files)

            count_files += 1

            frame_count_local2 = 0

            while frame_count_local2 <= frames_per_slide - 1:
                ret, frame = cap.read()

                frame_count_local2 += 1
   
        print(f"Saved frame {count_files} - {data_files[count_files - 1]}")
    
    print(f"Done! Extracted {count_files} frames to '{output_folder}/'")

    cap.release()
