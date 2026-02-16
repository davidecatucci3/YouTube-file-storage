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
    output_folder = 'out2'
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

            while frame_count_local2 < frames_per_slide - 1:
                ret, frame = cap.read()

                frame_count_local2 += 1
   
        print(f"Saved {data_files[count_files - 1]}")
    
    print(f"Done! Extracted {count_files} frames to '{output_folder}/'")

    cap.release()

#decoder(['data/extracted_2.jpg', 'data/big_one.txt', 'data/txt_reader.py', 'data/A/extracted_1.jpg', 'data/A/A1/t.txt', 'data/A/A1/message.txt', 'data/A/A12/notes.txt', 'data/A/A12/notes3.txt', 'data/A/A12/notes1.txt', 'data/C/rtt.txt', 'data/C/im1.jpg', 'data/B/extracted_3.jpg', 'data/B/encoder.py', 'data/B/extracted_111.jpg'], 'video_decoder.mp4', [(612, 408), (1920, 1080), (1920, 1080), (1200, 630), (1920, 1080), (1920, 1080), (1920, 1080), (1920, 1080), (1920, 1080), (1920, 1080), (612, 408), (1024, 576), (1920, 1080), (1200, 630)], [25, 2, 1, 73, 1, 1, 1, 1, 1, 1, 25, 57, 1, 73])
#decoder(['data/photo_19.jpg', 'data/photo_22.jpg', 'data/document_18.txt', 'data/Beta/photo_24.jpg', 'data/Beta/Delta/Alpha/photo_13.jpg', 'data/Beta/Epsilon/Gamma/photo_10.jpg', 'data/Beta/Alpha/Delta/document_8.txt', 'data/Delta/document_25.txt', 'data/Delta/Delta/document_20.txt', 'data/Delta/Epsilon/Delta/document_17.txt', 'data/Delta/Alpha/photo_1.jpg', 'data/Gamma/photo_21.jpg', 'data/Gamma/Delta/photo_12.jpg', 'data/Gamma/Delta/Beta/document_7.txt', 'data/Gamma/Zeta/Gamma/photo_9.jpg', 'data/Gamma/Epsilon/Delta/photo_3.jpg', 'data/Zeta/Gamma/Epsilon/photo_16.jpg', 'data/Zeta/Epsilon/Gamma/photo_2.jpg', 'data/Epsilon/photo_23.jpg', 'data/Epsilon/Gamma/document_11.txt', 'data/Epsilon/Epsilon/Gamma/photo_4.jpg', 'data/Epsilon/Epsilon/Alpha/document_14.txt', 'data/Alpha/Beta/Alpha/photo_5.jpg', 'data/Alpha/Gamma/document_15.txt', 'data/Alpha/Alpha/Zeta/document_6.txt'], 'video_decoder.mp4', [(276, 599), (1962, 538), (1920, 1080), (943, 282), (1399, 953), (277, 1219), (1920, 1080), (1920, 1080), (1920, 1080), (1920, 1080), (210, 935), (1771, 282), (599, 870), (1920, 1080), (1078, 782), (1497, 907), (1331, 289), (1008, 945), (662, 1403), (1920, 1080), (1687, 933), (1920, 1080), (824, 690), (1920, 1080), (1920, 1080)], [16, 102, 10, 26, 129, 33, 1, 3, 3, 9, 19, 49, 51, 16, 82, 131, 38, 92, 90, 2, 152, 11, 55, 10, 7])
#decoder(['data/photo_4.jpg', 'data/document_8.txt', 'data/Beta/Alpha/photo_9.jpg', 'data/Beta/Alpha/photo_6.jpg', 'data/Beta/Alpha/Zeta/photo_7.jpg', 'data/Gamma/Alpha/Epsilon/document_1.txt', 'data/Zeta/Delta/Beta/photo_5.jpg', 'data/Zeta/Gamma/Epsilon/photo_10.jpg', 'data/Epsilon/Alpha/Gamma/photo_3.jpg', 'data/Alpha/document_2.txt'], 'video_decoder.mp4', [(218, 581), (1920, 1080), (394, 482), (474, 673), (226, 595), (1920, 1080), (469, 536), (601, 370), (397, 539), (1920, 1080)], [24, 10, 36, 61, 26, 13, 48, 43, 41, 7])
#decoder(['data/photo_4.jpg', 'data/document_8.txt', 'data/Beta/Alpha/photo_9.jpg', 'data/Beta/Alpha/photo_6.jpg', 'data/Beta/Alpha/Zeta/photo_7.jpg', 'data/Gamma/Alpha/Epsilon/document_1.txt', 'data/Zeta/Delta/Beta/photo_5.jpg', 'data/Zeta/Gamma/Epsilon/photo_10.jpg', 'data/Epsilon/Alpha/Gamma/photo_3.jpg', 'data/Alpha/document_2.txt', 'data/Alpha/a.py'], 'video_decoder.mp4', [(218, 581), (1920, 1080), (394, 482), (474, 673), (226, 595), (1920, 1080), (469, 536), (601, 370), (397, 539), (1920, 1080), (1920, 1080)], [8, 4, 12, 20, 9, 5, 16, 14, 14, 2, 1])