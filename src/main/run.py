'''
run.py connect all the main files, the encoder, decoder, ... is the file that needs to be used to run everything
'''

import time
import os

from main.upload_video import initialize_upload, get_authenticated_service
from main.download_video import download_video
from oauth2client.tools import argparser
from apiclient.errors import HttpError
from tinydb import TinyDB, Query
from main.encoder import encoder
from main.decoder import decoder

def wait_for_processing(youtube, video_id):
    print(f"Waiting for video {video_id} to finish processing...")
    
    while True:
        request = youtube.videos().list(
            part="processingDetails,status",
            id=video_id
        )
        response = request.execute()

        if not response['items']:
            print("Video not found yet...")
        else:
            status = response['items'][0]['status']['uploadStatus']

            if status == "processed":
                print("Video is ready!")

                return True
            elif status == "failed":
                exit("Video processing failed.")
            else:
                print(f"Current status: {status}. Checking again in 5 seconds...")
        
        time.sleep(5) 

def run(path_data: str) -> None:
    '''
    make everything work together
    
    :param path_data: path of the folder where all the data are
    '''
    
    imgs_size, data_files, all_frame_needed = encoder(path_data) # put data in the video
    print(imgs_size, data_files, all_frame_needed)
    # upload video on youtube
    VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")  
    argparser.add_argument("--file", default="video_encoder.mp4", help="Video file to upload")
    argparser.add_argument("--title", help="Video title", default="Test Title")
    argparser.add_argument("--description", help="Video description", default="Test Description")
    argparser.add_argument("--category", default="22", help="Numeric video category. " + "See https://developers.google.com/youtube/v3/docs/videoCategories/list")       
    argparser.add_argument("--keywords", help="Video keywords, comma separated", default="")
    argparser.add_argument("--privacyStatus", choices=VALID_PRIVACY_STATUSES, default=VALID_PRIVACY_STATUSES[0], help="Video privacy status.")
    args = argparser.parse_args()

    if not os.path.exists(args.file):
        exit("Please specify a valid file using the --file= parameter.")

    youtube = get_authenticated_service(args)
    try:
        url, video_id = initialize_upload(youtube, args)
    except HttpError as e:
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))

    db = TinyDB('my_data.json')
    User = Query()

    for file in data_files:
        db.update({'url': url}, User.path_file == file)

    wait_for_processing(youtube, video_id) # waits until the youtube video is uploaded so it can download it
    
    path_video = download_video(url) # download from youtube the video uplaoded before

    decoder(data_files, path_video, imgs_size, all_frame_needed) # extract data from the video and decompress it

run('data')