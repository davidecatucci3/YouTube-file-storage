# YouTube-file-storage

> Store any file — images, videos, audio, documents — for free on YouTube by encoding binary data into video frames.

YouTube imposes no storage limits on uploaded videos. This project exploits that by converting arbitrary files into video streams, uploading them to YouTube, and decoding them back on demand — effectively turning YouTube into a free, unlimited cloud storage backend.

---

## How It Works

1. **Encode** — Binary data from your files is converted into visual frames (pixel patterns) and compiled into an `.mp4` video.
2. **Upload** — The video is uploaded to YouTube via the YouTube Data API v3.
3. **Wait** — The system polls YouTube until the video finishes processing.
4. **Download** — The processed video is downloaded from YouTube.
5. **Decode** — Frames are read and the original binary data is reconstructed, restoring your files exactly.

A local [TinyDB](https://tinydb.readthedocs.io/) database (`my_data.json`) maps each original file path to its corresponding YouTube URL for retrieval.

---

## Project Structure

```
.
├── data/                   # Drop your files here before running
├── main/
│   ├── encoder.py          # Converts files into video frames (.mp4)
│   ├── decoder.py          # Reconstructs files from downloaded video
│   ├── upload_video.py     # Handles YouTube OAuth2 auth & upload
│   └── download_video.py   # Downloads the processed video from YouTube
├── run.py                  # Entry point — ties everything together
├── my_data.json            # TinyDB file→URL mapping database
├── video_encoder.mp4       # Intermediate encoded video (auto-generated)
└── client_secrets.json     # Your YouTube API OAuth2 credentials (see setup)
```

---

## Requirements

- Python 3.8+
- A Google account with YouTube Data API v3 enabled
- `client_secrets.json` from Google Cloud Console

Install dependencies:

```bash
pip install -r requirements.txt
```

Key packages used:

| Package | Purpose |
|---|---|
| `google-api-python-client` | YouTube Data API v3 |
| `oauth2client` | OAuth2 authentication |
| `tinydb` | Local file→URL database |
| `opencv-python` | Frame encoding/decoding |

---

## Setup

### 1. Enable the YouTube Data API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Navigate to **APIs & Services → Library**
4. Search for **YouTube Data API v3** and enable it
5. Go to **APIs & Services → Credentials**
6. Create an **OAuth 2.0 Client ID** (Desktop app)
7. Download the credentials and save them as `client_secrets.json` in the project root

### 2. Add Your Files

Place any files you want to store inside the `data/` folder:

```
data/
├── photo.jpg
├── song.mp3
└── clip.mp4
```

---

## Usage

```bash
python run.py
```

On first run, a browser window will open for Google OAuth2 authentication. After authorizing, the flow runs automatically:

```
Encoding files...
Uploading to YouTube...
Waiting for video to finish processing...
Current status: uploaded. Checking again in 5 seconds...
Video is ready!
Downloading video...
Decoding and restoring files...
Execution time: 94.3s
```

Your original files are restored from the YouTube video, byte-perfect.

### Optional CLI Arguments

These are passed through `argparser` and can override defaults:

| Argument | Default | Description |
|---|---|---|
| `--file` | `video_encoder.mp4` | Path to the encoded video file |
| `--title` | `Test Title` | YouTube video title |
| `--description` | `Test Description` | YouTube video description |
| `--category` | `22` | YouTube category ID |
| `--keywords` | _(empty)_ | Comma-separated tags |
| `--privacyStatus` | `public` | `public`, `private`, or `unlisted` |

> **Tip:** Use `--privacyStatus=private` or `--privacyStatus=unlisted` to keep your storage videos hidden from your channel.

---

## Limitations & Considerations

- **YouTube re-encodes all uploads.** The encoder must be robust to lossy compression — data is embedded in a way that survives YouTube's transcoding pipeline.
- **Upload speed** is constrained by your internet connection and YouTube's processing time.
- **YouTube ToS** — This project is experimental. Automated or bulk uploads may violate [YouTube's Terms of Service](https://www.youtube.com/t/terms). Use responsibly.
- **Not suitable for sensitive data** — even private/unlisted videos are stored on Google's infrastructure.

---

## License

MIT License. See `LICENSE` for details.
