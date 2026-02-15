'''
The decoder get in input the video downloaded from youtube and exctract all the frames that corresponds to the data stored in the video
'''

import numpy as np
import config
import magic
import cv2

from decompress.img_decompresser import img_decompresser
from decompress.txt_decompresser import txt_decompresser

def img_to_txt(frame: list, output_folder: str, frame_count: int, block_size: int, data_files: list[str]) -> list:
    #!use numpy for faster matrix operation on it
    import os 
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

def decoder(data_files: str, file_path: str, imgs_size: list[tuple[int, int]], all_frame_needed: list[int], frames_per_slide: int) -> None:
    '''
    The decoder get in input the video downloaded from youtube and exctract all the frames that correpsonds to the data stored in the video

    :param data_files: list of all file path of each data in video
    :param file_path: Path for the video
    :param imgs_size: list of tuple where each tuple contains real width and height of image before resizing
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
     
        file_type = magic.from_file(data_files[count_files], mime=True)
        
        if all_frame_needed[count_files] > 1:
            if file_type.startswith('image/'):
                j = 0
                frame_count_local = 0
                inp_img = np.zeros((all_frame_needed[count_files], config.height, config.width, 3))

                while frame_count_local < all_frame_needed[count_files] * frames_per_slide:
                    if frame_count_local % frames_per_slide == 0:
                        inp_img[j] = frame

                        j += 1
                        
                    frame_count_local += 1
                
                    ret, frame = cap.read()
                
                img_decompresser(inp_img, output_folder, count_files, data_files, imgs_size)
            elif file_type.startswith('text/'):
                j = 0
                frame_count_local = 0
                inp_img = np.zeros((all_frame_needed[count_files], config.height, config.width, 3))

                while frame_count_local < all_frame_needed[count_files] * frames_per_slide:
                    if frame_count_local % frames_per_slide == 0:
                        inp_img[j] = frame

                        j += 1
                        
                    frame_count_local += 1
                
                    ret, frame = cap.read()
                
                txt_decompresser(inp_img, output_folder, count_files, data_files, all_frame_needed[count_files])

            count_files += 1
        else:                
            if file_type.startswith('image/'):
                # frame require (frame_needed, width, height, 3) as input
                frame = frame.reshape((1, frame.shape[0], frame.shape[1], 3))

                img_decompresser(frame, output_folder, count_files, data_files, imgs_size)
            elif file_type.startswith('text/'):
                # frame require (frame_needed, width, height, 3) as input
                frame = frame.reshape((1, frame.shape[0], frame.shape[1], 3))
      
                txt_decompresser(frame, output_folder, count_files, data_files, all_frame_needed[count_files])

            count_files += 1

            frame_count_local2 = 0

            while frame_count_local2 <= frames_per_slide - 1:
                ret, frame = cap.read()

                frame_count_local2 += 1
   
        print(f"Saved frame {count_files} - {data_files[count_files - 1]}")
    
    print(f"Done! Extracted {count_files} frames to '{output_folder}/'")

    cap.release()

decoder(['data/extracted_2.jpg', 'data/big_one.txt', 'data/txt_reader.py', 'data/A/extracted_1.jpg', 'data/A/A1/message.txt', 'data/A/A12/notes2.txt', 'data/A/A12/notes1.txt', 'data/B/extracted_3.jpg', 'data/B/encoder.py'], 'video_decoder.mp4', [(612, 408), (1920, 1080), (1920, 1080), (1200, 630), (1920, 1080), (1920, 1080), (1920, 1080), (1024, 576), (1920, 1080)], [25, 2, 1, 73, 1, 1, 1, 57, 1], 8) 