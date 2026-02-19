'''
given the url of the youtube video it download it
'''

import yt_dlp

def download_video(url: str) -> str:
    path_file = "video_decoder.mp4"

    ydl_opts = {
        'format': 'bestvideo[height=1080]+bestaudio/best[height=1080]',
        'merge_output_format': 'mp4',
        'outtmpl': path_file
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Fetching: {url}")

            ydl.download([url])
            
            print("\nDownload complete!")
    except Exception as e:
        print(f"An error occurred: {e}")

    return path_file

# TODO:
# better to understand format download


