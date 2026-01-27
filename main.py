import os
import sys
import zipfile
import subprocess
from yt_dlp import YoutubeDL


def download_videos(search_query, n, out_dir):
    ydl_opts = {
        "quiet": True,
        "format": "bestaudio/best",
        "outtmpl": f"{out_dir}/%(title)s.%(ext)s",
        "noplaylist": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"ytsearch{n}:{search_query}"])


def extract_audio_snippets(video_dir, seconds, audio_dir):
    os.makedirs(audio_dir, exist_ok=True)

    for file in os.listdir(video_dir):
        if not file.lower().endswith((".mp4", ".webm", ".mkv", ".m4a")):
            continue

        input_path = os.path.join(video_dir, file)
        output_name = os.path.splitext(file)[0] + ".mp3"
        output_path = os.path.join(audio_dir, output_name)

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_path,
            "-t",
            str(seconds),
            "-vn",
            "-acodec",
            "mp3",
            output_path,
        ]

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def zip_audio(audio_dir, zip_name):
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in os.listdir(audio_dir):
            zipf.write(os.path.join(audio_dir, file), arcname=file)


def main():
    if len(sys.argv) < 3:
        print('Usage: python script.py "search query" N')
        sys.exit(1)

    search_query = sys.argv[1]
    n = int(sys.argv[2])

    base_dir = "output"
    video_dir = os.path.join(base_dir, "videos")
    audio_dir = os.path.join(base_dir, "audio")
    zip_name = "audio_snippets.zip"

    os.makedirs(video_dir, exist_ok=True)

    print("Downloading videos...")
    download_videos(search_query, n, video_dir)

    print("Extracting audio...")
    extract_audio_snippets(video_dir, n, audio_dir)

    print("Creating zip...")
    zip_audio(audio_dir, zip_name)

    print(f"Done! Output saved as {zip_name}")


if __name__ == "__main__":
    main()
