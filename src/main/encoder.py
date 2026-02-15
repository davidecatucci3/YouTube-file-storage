'''
The encoder takes as input a folder with data of every type inside (.PDF, .txt, .JPG, .py, ...) and put them in a video of 256GB to 
publish on YouTube (pusblished so it can be stored)
'''

import magic
import cv2
import os

from readers.img_reader import img_reader
from readers.txt_reader import txt_reader

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
        return 

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

    # EntireData (store everything in less video possible)
    width, height = 1920, 1080 # video frame dimension
    fps = 30 
    output_filename = 'video_encoder.mp4'
    frames_per_slide = 8 #! better to remove but how 

    imgs_size = []
    all_frame_needed = [] # number if frames neeed to store the ith data file (if 1 needs just 1 frame)

    curr_duration = 0.0
    MAX_DURATION = 12 * 3600 # 12H in sec

    fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
    out = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))  

    for file_path in data_files:
        file_type = magic.from_file(file_path, mime=True)

        if file_type.startswith('image/'):
            size, frame, frame_needed = img_reader(file_path, width, height)  
            
            img_width, img_height = size

            all_frame_needed.append(frame_needed)
            imgs_size.append((img_width, img_height))

            curr_duration += (frame_needed * frames_per_slide) / fps
  
            if frame_needed == 1:
                for _ in range(frames_per_slide):
                    out.write(frame)
            else:
                for r in range(frame_needed):
                    for _ in range(frames_per_slide):
                        out.write(frame[r])
        elif file_type.startswith('text/'):
            frame, block_size = txt_reader(file_path, width, height) 

            imgs_size.append((width, height))
            all_frame_needed.append(1)

            curr_duration += (1 * frames_per_slide) / fps

            for _ in range(frames_per_slide):
                out.write(frame)

        print(f'Current video duration (in seconds): {curr_duration:.3f}/{MAX_DURATION}')
 
    out.release()   

    # ChunkData (store everything in more video possible)
    # ...

    return imgs_size, data_files, block_size, all_frame_needed, frames_per_slide, width, height

