'''
The encoder takes as inout a folder with filrs of every type inside (.PDF, .txt, .JPG, .py, ...) and put them in a video of 256GB to
publish on YouTubr (publish for us means store it)
'''

from readers.img_reader import img_reader
from readers.txt_reader import txt_reader