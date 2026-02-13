'''
run.py connect all the main files, the encoder, decoder, ...
'''

import time
import os

from main.upload_video import initialize_upload, get_authenticated_service
from decompress.decompresser import decompresser
from main.download_video import download_video
from oauth2client.tools import argparser
from apiclient.errors import HttpError
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
    make everything together
    
    :param path_data: Description
    '''
    imgs_real_sizes, data_files, block_size = encoder(path_data) # put data in the video

    VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")  
    argparser.add_argument("--file", default="video_encoder.mp4", help="Video file to upload") #!required=True removed by me
    argparser.add_argument("--title", help="Video title", default="Test Title")
    argparser.add_argument("--description", help="Video description",
        default="Test Description")
    argparser.add_argument("--category", default="22",
        help="Numeric video category. " +
        "See https://developers.google.com/youtube/v3/docs/videoCategories/list")
    argparser.add_argument("--keywords", help="Video keywords, comma separated",
        default="")
    argparser.add_argument("--privacyStatus", choices=VALID_PRIVACY_STATUSES,
        default=VALID_PRIVACY_STATUSES[0], help="Video privacy status.")
    args = argparser.parse_args()

    if not os.path.exists(args.file):
        exit("Please specify a valid file using the --file= parameter.")

    youtube = get_authenticated_service(args)
    try:
        url, video_id = initialize_upload(youtube, args)
    except HttpError as e:
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))

    wait_for_processing(youtube, video_id) # waits until the YT video is uploaded so i can downloaded
    
    path_video = download_video(url) # download form youtube the video uplaoded

    decoder(data_files, path_video, imgs_real_sizes, block_size) # extract files from the video

    # make the images look like they have been uploaded 
    list_files = os.listdir('out')

    for file in list_files:
        decompresser(file)

run('data')