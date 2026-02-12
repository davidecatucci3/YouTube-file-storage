'''
The encoder takes as input a folder with filrs of every type inside (.PDF, .txt, .JPG, .py, ...) and put them in a video of 256GB to
publish on YouTubr (publish for us means store it)
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
    Encode all the data and put them in vidoes ready to be loaded
    
    :param path_data: path of the directory where all the data to put in the storage are
    :return imgs_real_size: contains a list of tuple width real widrth and height of images that have been resized
    '''

    data_files = get_files(path_data, [])

    # EntireData
    width, height = 1920, 1080
    fps = 30 # more fps means duration video less and memory video less (slightly), remember MAX 12H and 256GB 
    output_filename = 'video_encoder.mp4'
    frames_per_slide = 8 
    imgs_real_size = []
  
    duration = 3 / fps # more fps is high and more the duration is low and memory occupancy low but if fps is too high it's a problem will be ok to create but
    MAX_DURATION = 12 * 3600 # 12H in sec
  
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
    out = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))  

    for file in data_files:
        file_type = magic.from_file(file, mime=True)

        if file_type.startswith('image/'):
            real_size, frame = img_reader(file, width, height)  

            rwidth, rheight = real_size

            imgs_real_size.append((rwidth, rheight))

            for _ in range(frames_per_slide):
                out.write(frame)
            
        # elif file_type == 'text/plain':
            #frame = txt_reader(file) 

            #out.write(frame)
            #pass
 
    out.release()   

    # ChunkData
    # ...

    return imgs_real_size

