'''
given the url of the video it download it
'''

import yt_dlp

def download_video(url: str) -> None:
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': '%(title)s.%(ext)s',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Fetching: {url}")

            ydl.download([url])
            
            print("\nDownload complete!")
    except Exception as e:
        print(f"An error occurred: {e}")


