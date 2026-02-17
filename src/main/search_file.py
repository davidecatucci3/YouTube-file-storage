'''
Search the url of the video that contains the file that i want and take the file i want
'''

import numpy as np
import yt_dlp
import config
import cv2

from decompress.img_decompresser import img_decompresser
from decompress.txt_decompresser import txt_decompresser
from tinydb import TinyDB, Query

def get_frame(url: str, frame_start: int, frame_end: int):
    ydl_opts = {'format': 'bestvideo[height=1080][ext=mp4]/best[ext=mp4]/best', 'quiet': True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url = info['url']

    cap = cv2.VideoCapture(url)

    if not cap.isOpened():
            print("Error: Could not open video stream.")
            return

    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_start)

    current_frame_num = frame_start

    while current_frame_num <= frame_end:
        success, frame = cap.read()
            
        if not success:
            print(f"Stream ended or failed at frame {current_frame_num}")

            break
                
        yield current_frame_num, frame
            
        current_frame_num += 1

    cap.release()

def search_file(path_file: str) -> str:
    db = TinyDB('my_data.json')

    User = Query()

    res = db.get(User.path_file == path_file)
    url = res['url']
    file_type = res['file type']
    frame_needed = res['frame needed']
    frame_start = res['frame start']
    frame_end = res['frame end']
    w, h = res['frame dim']

    inp_img = np.zeros((frame_needed, config.height, config.width, 3))

    j = 0
    frame_count_local = 0
    
    for _, frame_i in get_frame(url, frame_start, frame_end):
        while frame_count_local < frame_needed * config.frames_per_slide - 1:
            if frame_count_local % config.frames_per_slide == 0:
                inp_img[j] = frame_i

                j += 1
                        
            frame_count_local += 1
    
    if file_type.startswith('image/'):
        img_decompresser(inp_img, 'sea', 0, w, h) 
    elif file_type.startswith('text/'):
        txt_decompresser(inp_img, 'sea', 0, frame_needed)