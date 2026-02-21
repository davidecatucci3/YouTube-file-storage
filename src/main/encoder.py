'''
The encoder takes as input a folder with data of every type inside (.PDF, .txt, .JPG, .py, ...) and put them in a video of 256GB to be
publish on YouTube (pusblished so it can be stored)
'''

import config
import magic
import cv2
import os

from readers.img_reader import img_reader
from readers.txt_reader import txt_reader
from tinydb import TinyDB

def get_files(path: str, data_files: list) -> list[str]:
    '''
    Recursively search all the data (not directory just data files of every type) in the data directory

    :param path_data: the first function contains path_data but is recursive so the other calls will be others path os sub directory of path_data
    :return data_files: all the files in the data directory
    '''    
    
    subpaths = os.listdir(path)
    subpath_onlydir = []

    for subpath in subpaths:
        absolute_path = path + '/' + subpath
        
        if subpath != '.DS_Store':
            if os.path.isfile(absolute_path):
                data_files.append(absolute_path)
            else:
                subpath_onlydir.append(subpath)

    if len(subpath_onlydir) == 0:
        return data_files 

    for subpath in subpath_onlydir:
        get_files(path + '/' + subpath, data_files)
  
    return data_files

def encoder(path_data: str) -> list[tuple[int, int]]:
    '''
    Encode all the data and put them in a youtube video to be loaded
    
    :param path_data: path of the directory where all the data to put in the storage are
    :return imgs_size: contains a list of tuple with the width and height of the stored images usefule in the decoder
    '''

    data_files = get_files(path_data, [])

    db = TinyDB('my_data.json')

    # EntireData (store everything in less video possible)
    video_width, video_height = config.video_width, config.video_height # video frame dimension
    fps = 30
    filename = 'video_encoder.mp4'
    frames_per_slide = config.frames_per_slide # an image cannot have 1 frame so have a duration of millisecond otherwise the video algoeithm won't work so we need to store more of the same frame, more frames_per_slide is higher and more the video is long and size is high but less error in decompression i will have
    frames_per_slide_img = config.frames_per_slide_img
    fourcc = cv2.VideoWriter_fourcc(*'avc1')  
    out = cv2.VideoWriter(filename, fourcc, fps, (video_width, video_height))  
    
    all_frame_needed = [] # number if frames neeed to store the ith data file (if 1 needs just 1 frame)
    curr_frame = 0 # number of frame i am at
    curr_duration = 0.0
    curr_size = 0.0 # in GB, the actual data will be defined ater out.release() when everything will be written inside the file, so finla size will be sllightly higher
    MAX_DURATION = 12 * 3600 # 12H in sec
    MAX_SIZE = 256 # in GB

    for path_file in data_files:
        file_type = magic.from_file(path_file, mime=True)

        if file_type.startswith('image/'):
            size, frames, frame_needed = img_reader(path_file)  
            
            img_width, img_height = size

            frame_start = curr_frame
            frame_end = frame_start + (frame_needed * frames_per_slide_img)

            curr_duration += (frame_needed * frames_per_slide) / fps

            db.insert({'path_file': path_file, 'url': '', 'file type': file_type, 'frame dim': (img_width, img_height), 'frame needed': frame_needed, 'frame start': frame_start, 'frame end': frame_end})

            for r in range(frame_needed):
                for _ in range(frames_per_slide_img):
                    out.write(frames[r])

                    curr_frame += 1
        elif file_type.startswith('text/'):
            frames, frame_needed = txt_reader(path_file) 

            frame_start = curr_frame
            frame_end = frame_start + (frame_needed * frames_per_slide)

            curr_duration += (frame_needed * frames_per_slide) / fps
            
            db.insert({'path_file': path_file, 'url': '', 'file type': file_type, 'frame dim': (0, 0), 'frame needed': frame_needed, 'frame start': frame_start, 'frame end': frame_end})
            
            for r in range(frame_needed):
                for _ in range(frames_per_slide):
                    out.write(frames[r])

                    curr_frame += 1
    
        all_frame_needed.append(frame_needed)

        if os.path.exists(filename):
            curr_size_bytes = os.path.getsize(filename)

            curr_size = curr_size_bytes / (1024 * 1024 * 1024)
        
        print(f'frame range: {frame_start:3d}-{frame_end:3d} | duration: {curr_duration:.3f}s/{MAX_DURATION}s | size: {curr_size:.3f} GB/{MAX_SIZE} GB')
 
    out.release()   

    if os.path.exists(filename):
        size_bytes = os.path.getsize(filename)

        size = size_bytes / (1024 * 1024 * 1024)
    
    print(f'final size: {size:.3f} GB')

    return data_files, all_frame_needed

# TODO:
# bug when mix text and images (text sligh more errors in letters)