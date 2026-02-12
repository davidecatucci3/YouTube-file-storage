'''
The encoder takes as input a folder with filrs of every type inside (.PDF, .txt, .JPG, .py, ...) and put them in a video of 256GB to
publish on YouTubr (publish for us means store it)
'''

import numpy as np
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

        if os.path.isfile(absolute_path):
            data_files.append(absolute_path)
        else:
            subpath_onlydir.append(subpath)

    if len(subpath_onlydir) == 0:
        return 

    for subpath in subpath_onlydir:
        get_files(path + '/' + subpath, data_files)

    return data_files

def encoder(path_data: str) -> None:
    '''
    Encode all the data and put them in vidoes ready to be loaded
    
    :param path_data: path of the directory where all the data to put in the storage are
    '''

    data_files = get_files(path_data, [])

    # EntireData
    # create video
    width, height = 1280, 720   # 1920x1080
    fps = 24      
    seconds = 6            
    frames_per_slide = (fps * seconds) // len(data_files)       
    output_filename = 'video1.mp4'

    fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
    out = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))  

    for file in data_files:
        file_type = magic.from_file(file, mime=True)

        if file_type.startswith('image/'):
            frame = img_reader(file, width, height)  

            for _ in range(frames_per_slide):
                out.write(frame)
        elif file_type == 'text/plain':
            #frame = txt_reader(file) 

            #out.write(frame)
            pass

    out.release()

    # ChunkData
    # ...

encoder("data")

