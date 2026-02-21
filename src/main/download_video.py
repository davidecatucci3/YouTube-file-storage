'''
given the url of the youtube video it download it
'''

import yt_dlp
import time

def download_video(url: str, check_interval_seconds: int = 60, max_attempts: int = 60) -> str:
    path_file = "video_decoder.mp4"

    check_opts = {
        'quiet': True,
        'no_warnings': True
    }
    
    download_opts = {
        'format': 'bestvideo[height=1080]+bestaudio/best[height=1080]',
        'merge_output_format': 'mp4',
        'outtmpl': path_file
    }

    print(f"Checking {url} for 1080p availability...")

    attempt = 1
    hd_found = False

    while attempt <= max_attempts:
        try:
            with yt_dlp.YoutubeDL(check_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                
                # look through all available formats for a 1080p stream
                hd_found = any(
                    f.get('height') is not None and f.get('height') >= 1080 
                    for f in formats
                )

                if hd_found:
                    print("\n1080p stream detected! Starting download...")
                    break
                else:
                    print(f"[Attempt {attempt}/{max_attempts}] 1080p not ready yet. Waiting {check_interval_seconds}s...")

                    time.sleep(check_interval_seconds)

                    attempt += 1
                    
        except Exception as e:
            print(f"An error occurred while checking: {e}")
            print(f"Retrying in {check_interval_seconds}s...")

            time.sleep(check_interval_seconds)

            attempt += 1

    if hd_found:
        try:
            with yt_dlp.YoutubeDL(download_opts) as ydl:
                ydl.download([url])
                print("\nDownload complete!")
        except Exception as e:
            print(f"An error occurred during download: {e}")
    else:
        print("\nTimed out waiting for 1080p to process.")

    return path_file

# TODO:
# better to understand format download


