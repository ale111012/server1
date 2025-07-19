import os
import threading
import time
import yt_dlp
from moviepy.editor import VideoFileClip
from PIL import Image
import pygame
import sys

# --- Core Conversion Functions ---

ASCII_CHARS = "@%#*+=-:. "

def resize_image(image, new_width=100):
    width, height = image.size
    aspect_ratio = height / float(width)
    new_height = int(aspect_ratio * new_width * 0.55)
    resized_image = image.resize((new_width, new_height))
    return resized_image

def grayify(image):
    return image.convert("L")

def pixels_to_ascii(image):
    pixels = image.getdata()
    characters = "".join([ASCII_CHARS[pixel * (len(ASCII_CHARS) - 1) // 255] for pixel in pixels])
    return characters

def image_to_ascii(image, new_width=100):
    image = resize_image(image, new_width)
    image = grayify(image)
    ascii_str = pixels_to_ascii(image)

    img_width = image.width
    ascii_str_len = len(ascii_str)
    ascii_img = ""
    for i in range(0, ascii_str_len, img_width):
        ascii_img += ascii_str[i:i+img_width] + "\n"

    return ascii_img

# --- Main Application Class ---

class AsciiPlayerApp:
    def __init__(self, url):
        self.url = url
        self.video_path = None
        self.audio_path = None
        self.ascii_frames = []
        self.fps = 0
        self.is_playing = False

    def process_video(self):
        try:
            # --- Download Video ---
            print("Downloading video...")
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': 'temp_video.%(ext)s',
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            self.video_path = 'temp_video.mp4'

            # --- Extract Audio ---
            print("Extracting audio...")
            video_clip = VideoFileClip(self.video_path)
            self.audio_path = 'temp_audio.wav'
            video_clip.audio.write_audiofile(self.audio_path, codec='pcm_s16le')

            # --- Process Frames ---
            print("Processing frames...")
            self.fps = video_clip.fps
            self.ascii_frames = []

            for frame in video_clip.iter_frames():
                pil_image = Image.fromarray(frame)
                ascii_frame = image_to_ascii(pil_image)
                self.ascii_frames.append(ascii_frame)

            print("Ready to play!")
            self.save_output()

        except Exception as e:
            print(f"An error occurred: {e}")
            self.cleanup()

    def save_output(self):
        if not self.ascii_frames:
            return

        with open("output.txt", "w") as f:
            for frame in self.ascii_frames:
                f.write(frame)
                f.write("\n---FRAME---\n")

        print("ASCII frames saved to output.txt")
        self.cleanup()


    def cleanup(self):
        if self.video_path and os.path.exists(self.video_path):
            os.remove(self.video_path)
        if self.audio_path and os.path.exists(self.audio_path):
            os.remove(self.audio_path)

        self.video_path = None
        self.audio_path = None
        self.ascii_frames = []
        print("Finished or stopped.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <youtube_url>")
        sys.exit(1)

    url = sys.argv[1]
    app = AsciiPlayerApp(url)
    app.process_video()
