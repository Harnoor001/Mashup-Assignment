import os
import subprocess
import uuid

from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from yt_dlp import YoutubeDL
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME="hsardana_be23@thapar.edu",
    MAIL_PASSWORD="wqompiilowgpabwz",
    MAIL_DEFAULT_SENDER="Himanshu Sardana",
)

mail = Mail(app)

BASE_DIR = "jobs"
os.makedirs(BASE_DIR, exist_ok=True)


def download_videos(search_query, n, out_dir):
    ydl_opts = {
        "quiet": True,
        "format": "bestaudio/best",
        "outtmpl": f"{out_dir}/%(id)s.%(ext)s",
        "playlistend": n,
        "default_search": "ytsearch",
        "nocheckcertificate": True,
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        },
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"ytsearch{n}:{search_query}"])


def extract_audio_snippets(video_dir, duration, audio_dir):
    os.makedirs(audio_dir, exist_ok=True)

    for file in os.listdir(video_dir):
        if not file.lower().endswith((".mp4", ".webm", ".mkv", ".m4a")):
            continue

        input_path = os.path.join(video_dir, file)
        output_path = os.path.join(audio_dir, os.path.splitext(file)[0] + ".mp3")

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                input_path,
                "-t",
                str(duration),
                "-vn",
                "-acodec",
                "mp3",
                output_path,
            ],
            # stdout=subprocess.DEVNULL,
            # stderr=subprocess.DEVNULL,
            check=False,
        )


def merge_audio_files(audio_dir, output_path):
    mp3s = sorted(f for f in os.listdir(audio_dir) if f.endswith(".mp3"))

    if not mp3s:
        raise RuntimeError("No audio files to merge")

    inputs = []
    for file in mp3s:
        inputs.extend(["-i", os.path.join(audio_dir, file)])

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            *inputs,
            "-filter_complex",
            f"concat=n={len(mp3s)}:v=0:a=1",
            "-acodec",
            "mp3",
            "-ab",
            "192k",
            output_path,
        ],
        check=True,
    )

    if not os.path.exists(output_path):
        raise RuntimeError("Merged audio file was not created")


def send_audio_email(to_email, audio_path, query):
    msg = Message(
        subject=f"Merged audio for '{query}'",
        recipients=[to_email],
        body=f"Attached is the merged audio file for your search: '{query}'.",
    )

    with open(audio_path, "rb") as f:
        msg.attach(
            filename="merged_audio.mp3",
            content_type="audio/mpeg",
            data=f.read(),
        )

    mail.send(msg)


@app.route("/process", methods=["POST"])
def process():
    data = request.get_json()

    required = {"query", "n", "duration", "email"}
    if not data or not required.issubset(data):
        return jsonify({
            "error": "Expected JSON with 'query', 'n', 'duration', and 'email'"
        }), 400

    query = data["query"]
    n = int(data["n"])
    duration = int(data["duration"])
    email = data["email"]

    job_id = str(uuid.uuid4())
    job_dir = os.path.join(BASE_DIR, job_id)
    video_dir = os.path.join(job_dir, "videos")
    audio_dir = os.path.join(job_dir, "audio")
    merged_audio_path = os.path.join(job_dir, "merged_audio.mp3")

    os.makedirs(video_dir, exist_ok=True)

    try:
        with open("logs.txt", "a+") as f:
            f.write(f"Downloaded {n} videos for query '{query}, mailing to {email}'\n")
        download_videos(query, n, video_dir)
        extract_audio_snippets(video_dir, duration, audio_dir)
        merge_audio_files(audio_dir, merged_audio_path)
        send_audio_email(email, merged_audio_path, query)

        return jsonify({
            "status": "success",
            "message": f"Merged audio emailed to {email}",
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # shutil.rmtree(job_dir, ignore_errors=True)
        pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6900, debug=True)
