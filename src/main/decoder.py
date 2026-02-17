'''
The decoder get in input the video downloaded from youtube and exctract all the frames that corresponds to the data stored in the video
'''

import numpy as np
import config
import magic
import cv2

from decompress.img_decompresser import img_decompresser
from decompress.txt_decompresser import txt_decompresser

def decoder(data_files: str, file_path: str, imgs_size: list[tuple[int, int]], all_frame_needed: list[int]) -> None:
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

    frames_per_slide = config.frames_per_slide
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
            
                while frame_count_local < all_frame_needed[count_files] * frames_per_slide - 1:
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

                while frame_count_local < all_frame_needed[count_files] * frames_per_slide - 1:
                    if frame_count_local % frames_per_slide == 0:
                        inp_img[j] = frame

                        j += 1
                        
                    frame_count_local += 1
                
                    ret, frame = cap.read()
                
                txt_decompresser(inp_img, output_folder, count_files, all_frame_needed[count_files], data_files)

            count_files += 1
        else:                
            if file_type.startswith('image/'):
                # frame require (frame_needed, width, height, 3) as input
                frame = frame.reshape((1, frame.shape[0], frame.shape[1], 3))

                img_decompresser(frame, output_folder, count_files, data_files, imgs_size)
            elif file_type.startswith('text/'):
                # frame require (frame_needed, width, height, 3) as input
                frame = frame.reshape((1, frame.shape[0], frame.shape[1], 3))
      
                txt_decompresser(frame, output_folder, count_files, all_frame_needed[count_files], data_files)

            count_files += 1

            frame_count_local2 = 0

            while frame_count_local2 < frames_per_slide - 1:
                ret, frame = cap.read()

                frame_count_local2 += 1
   
        print(f"Saved {data_files[count_files - 1]}")
    
    print(f"Done! Extracted {count_files} frames to '{output_folder}/'")

    cap.release()