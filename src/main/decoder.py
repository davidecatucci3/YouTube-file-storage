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

decoder(['data/document_48.txt', 'data/document_7.txt', 'data/photo_25.jpg', 'data/document_12.txt', 'data/photo_37.jpg', 'data/document_28.txt', 'data/photo_22.jpg', 'data/photo_13.jpg', 'data/document_18.txt', 'data/photo_38.jpg', 'data/document_27.txt', 'data/document_32.txt', 'data/photo_14.jpg', 'data/document_47.txt', 'data/document_50.txt', 'data/photo_49.jpg', 'data/Beta/document_24.txt', 'data/Beta/document_9.txt', 'data/Beta/Beta/Epsilon/document_29.txt', 'data/Beta/Beta/Alpha/document_6.txt', 'data/Beta/Beta/Alpha/photo_19.jpg', 'data/Beta/Gamma/Alpha/photo_33.jpg', 'data/Beta/Epsilon/Alpha/photo_34.jpg', 'data/Beta/Alpha/Zeta/photo_26.jpg', 'data/Delta/Beta/Epsilon/photo_4.jpg', 'data/Delta/Beta/Alpha/photo_46.jpg', 'data/Delta/Zeta/document_16.txt', 'data/Delta/Epsilon/Beta/photo_10.jpg', 'data/Gamma/photo_2.jpg', 'data/Gamma/document_36.txt', 'data/Gamma/Beta/photo_40.jpg', 'data/Gamma/Gamma/document_8.txt', 'data/Gamma/Zeta/Gamma/photo_45.jpg', 'data/Gamma/Zeta/Zeta/document_44.txt', 'data/Gamma/Epsilon/document_17.txt', 'data/Gamma/Epsilon/Alpha/photo_5.jpg', 'data/Gamma/Alpha/Zeta/document_20.txt', 'data/Zeta/document_3.txt', 'data/Zeta/document_23.txt', 'data/Zeta/document_42.txt', 'data/Zeta/Zeta/photo_11.jpg', 'data/Zeta/Epsilon/Gamma/photo_41.jpg', 'data/Epsilon/photo_39.jpg', 'data/Epsilon/Beta/photo_1.jpg', 'data/Epsilon/Alpha/Beta/photo_15.jpg', 'data/Alpha/Beta/Delta/document_21.txt', 'data/Alpha/Gamma/Beta/document_31.txt', 'data/Alpha/Zeta/Zeta/photo_35.jpg', 'data/Alpha/Alpha/Delta/photo_43.jpg', 'data/Alpha/Alpha/Zeta/document_30.txt'], 'video_decoder.mp4', [11, 4, 44, 2, 12, 3, 64, 68, 11, 115, 1, 9, 82, 8, 4, 34, 8, 10, 6, 7, 28, 34, 52, 52, 23, 40, 3, 18, 118, 2, 60, 4, 20, 4, 3, 20, 6, 1, 3, 3, 92, 41, 15, 35, 15, 4, 10, 47, 16, 8])