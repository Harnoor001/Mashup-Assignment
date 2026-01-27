# YouTube Artist Mashup Generator

A Flask-based mashup application that automatically creates an audio mashup from an artist’s top YouTube videos and delivers it straight to your inbox 📩.

This app takes an **artist name**, **duration**, **email address**, and a **number (n)**, then:

1. Searches YouTube for the top `n` videos of the artist
2. Downloads the videos using `yt_dlp`
3. Extracts audio using `ffmpeg`
4. Trims each audio to the specified duration
5. Merges all audio clips into a single mashup
6. Emails the final mashup to the provided email address

---

## Features

- Automatic YouTube search based on artist name
- Video downloading via `yt_dlp`
- Audio extraction & trimming using `ffmpeg`
- Seamless audio merging into a single file
- Email delivery using `Flask-Mail`
- Automatic cleanup of temporary files

---

## Tech Stack

- **Backend**: Flask (Python)
- **YouTube Downloader**: `yt_dlp`
- **Audio Processing**: `ffmpeg`
- **Email Service**: `Flask-Mail`
- **CORS Support**: `flask-cors`

---

## Input Parameters

The API accepts the following inputs:

| Parameter  | Description                                   |
| ---------- | --------------------------------------------- |
| `artist`   | Name of the artist to search on YouTube       |
| `n`        | Number of top YouTube videos to download      |
| `duration` | Duration (in seconds) to trim each audio clip |
| `email`    | Email address to send the mashup to           |

---

## Output

- A **single merged audio file** (MP3)
- Delivered directly to the provided email address as an attachment

---

# Submitted by - Harnoor Singh Khalsa 
# Roll No - 102303260
# Group - 2C21
