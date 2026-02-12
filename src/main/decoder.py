'''
The decoder get in input the video downloaded from youtube and exctract all the frames that correpsonds to the data stored in the video
'''

import cv2
import os

def decoder(file_path: str, img_real_size: list[tuple[int, int]]) -> None:
    '''
    The decoder get in input the video downloaded from youtube and exctract all the frames that correpsonds to the data stored in the video
    
    :param file_path: Path for the video
    :param img_real_size: list of tuple where each tuple contains real width and height of image before resizing
    '''

    cap = cv2.VideoCapture(file_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open {file_path}")

        return

    output_folder = 'out'
    frame_count = 0

    print("Starting extraction... this may take a while.")

    while True:
        ret, frame = cap.read()

        if frame_count % 8 == 0:
            if not ret:
                break
            
            frame = cv2.resize(frame, (img_real_size[frame_count // 8][0], img_real_size[frame_count // 8][1])) # 8 is frames_per_slide

            filename = os.path.join(output_folder, f"frame_{frame_count // 8:04d}.jpg")
                
            cv2.imwrite(filename, frame)
                
            if frame_count % 8 == 0:
                print(f"Saved frame {frame_count}")

        frame_count += 1
    
    print(f"Done! Extracted {frame_count} frames to '{output_folder}/'")

    cap.release()
