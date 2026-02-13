'''
The decoder get in input the video downloaded from youtube and exctract all the frames that correpsonds to the data stored in the video
'''

import magic
import cv2
import os

def img_to_txt(frame: list, output_folder: str, frame_count: int, block_size: int) -> list:
    filename = os.path.join(output_folder, f"frame_{frame_count // 8:04d}.txt")

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
            if char_code == 0:
                continue
         
            txt += chr(char_code)
    
    with open(filename, 'a') as f:
        f.write(txt)

def decoder(data_files: str, file_path: str, img_real_size: list[tuple[int, int]], block_size) -> None:
    '''
    The decoder get in input the video downloaded from youtube and exctract all the frames that correpsonds to the data stored in the video

    :param data_files: list of all file path of each data in video
    :param file_path: Path for the video
    :param img_real_size: list of tuple where each tuple contains real width and height of image before resizing
    '''

    i = 0
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

            file_type = magic.from_file(data_files[frame_count // 8], mime=True)
           
            if file_type.startswith('image/'):
                filename = os.path.join(output_folder, f"frame_{frame_count:04d}.jpg")
                
                cv2.imwrite(filename, frame)
            elif file_type == 'text/plain':
                img_to_txt(frame, output_folder, frame_count, block_size)
                
            print(f"Saved frame {frame_count}")

        frame_count += 1
    
    print(f"Done! Extracted {frame_count} frames to '{output_folder}/'")

    cap.release()

#decoder(['data/extracted_2.jpg', 'data/A/extracted_1.jpg', 'data/A/A1/message.txt', 'data/A/A12/notes2.txt', 'data/A/A12/notes1.txt', 'data/B/extracted_3.jpg'], 'video_decoder.mp4', [(1920, 1080)] * 6)