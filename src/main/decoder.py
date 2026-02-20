'''
The decoder get in input the video downloaded from youtube and exctract all the frames that corresponds to the data stored in the video
'''

import numpy as np
import config
import magic
import cv2

from decompress.img_decompresser import img_decompresser
from decompress.txt_decompresser import txt_decompresser
from tinydb import TinyDB, Query

def decoder(data_files: str, path_video: str, all_frame_needed: list[int]) -> None:
    '''
    The decoder get in input the video downloaded from youtube and exctract all the frames that correpsonds to the data stored in the video

    :param data_files: list of all file path of each data in video
    :param path_video: Path for the video
    :param imgs_size: list of tuple where each tuple contains real width and height of image before resizing
    :paran all_frame_needed: number of frame needed for ith data file to be complitely stored in the video
    :param frames_per_slide: how many frames need a single frame (strange!)
    '''

    cap = cv2.VideoCapture(path_video)
    
    if not cap.isOpened():
        print(f"Error: Could not open {path_video}")

        return

    video_width = config.video_width
    video_height = config.video_height
    frames_per_slide = config.frames_per_slide
    output_folder = 'out'
    count_files = 0

    db = TinyDB('my_data.json')
    User = Query()

    print("Starting extraction... this may take a while.")

    while True:
        ret, frame = cap.read()

        if not ret:
            break
     
        file_type = magic.from_file(data_files[count_files], mime=True)

        if all_frame_needed[count_files] > 1:
            j = 0
            frame_count_local = 0
            frames = np.zeros((all_frame_needed[count_files], video_height, video_width, 3)) # all frame together of frames form the data file

            while frame_count_local < all_frame_needed[count_files] * frames_per_slide - 1:
                if frame_count_local % frames_per_slide == 0: # get frame i want not the copies 
                    frames[j] = frame 

                    j += 1
                        
                frame_count_local += 1
                
                ret, frame = cap.read()

            if file_type.startswith('image/'):  
                path_file = data_files[count_files]

                res = db.get(User.path_file == path_file)
                img_width, img_height = res['frame dim']

                img_decompresser(frames, output_folder, all_frame_needed[count_files], count_files, img_width, img_height, data_files)
            elif file_type.startswith('text/'):
                txt_decompresser(frames, output_folder, count_files, all_frame_needed[count_files], data_files)

            count_files += 1
        else:         
            # frame require (frame_needed, width, height, 3) as input
            frame = frame.reshape((1, frame.shape[0], frame.shape[1], 3))

            if file_type.startswith('image/'):
                path_file = data_files[count_files]
                
                res = db.get(User.path_file == path_file)
                img_width, img_height = res['frame dim']

                img_decompresser(frame, output_folder, all_frame_needed[count_files], count_files, img_width, img_height, data_files)
            elif file_type.startswith('text/'):      
                txt_decompresser(frame, output_folder, count_files, all_frame_needed[count_files], data_files)

            count_files += 1

            # i dont't want to check the frames_per_slice frames that are just the copy of the one i want to see so i skip them
            frame_count_local2 = 0

            while frame_count_local2 < frames_per_slide - 1:
                ret, frame = cap.read()

                frame_count_local2 += 1
   
        print(f"Saved {data_files[count_files - 1]}")
    
    print(f"Done! Extracted {count_files} frames to '{output_folder}/'")

    cap.release()

