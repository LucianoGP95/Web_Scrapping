import os
import re
import yt_dlp
import subprocess
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError

class Downloader:
    def __init__(self, url, output_folder):
        self.output_folder = output_folder
        self.url = url
        self.ydl_opts = {}
        self.info = {}
        self.progress_callback = None

    def set_progress_callback(self, callback):
        """Set a callback function to report download progress"""
        self.progress_callback = callback
        
    def _progress_hook(self, d):
        """Hook to capture download progress"""
        if self.progress_callback and d['status'] == 'downloading':
            try:
                percent = d['_percent_str'].strip()
                self.progress_callback(percent)
            except KeyError:
                pass

    def sanitize_filename(self, filename):
        """Remove non-valid windows characters."""
        return re.sub(r'[<>:"/\\|?*]', '', filename)

    def download_video(self):
        """Download video/audio with the correct settings."""
        # Add progress hooks to options
        self.ydl_opts['progress_hooks'] = [self._progress_hook]
        
        # First extract info without downloading
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            self.info = ydl.extract_info(self.url, download=False)

        video_title = self.sanitize_filename(self.info.get('title', 'unknown'))
        ext = self.info.get('ext', 'mp4')
        filename = os.path.join(self.output_folder, f"{video_title}.{ext}")

        if os.path.exists(filename):
            if self.progress_callback:
                self.progress_callback("100%")
            return f"Skipping: {filename} already exists."

        # Proceed with download
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([self.url])

        # Re-fetch the metadata after downloading
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            self.info = ydl.extract_info(self.url, download=True)

        # Use the downloaded information to create the final filename
        ext = self.info.get('ext', 'mp4')
        video_title = self.sanitize_filename(self.info.get('title', 'unknown'))
        mp3_path = os.path.join(self.output_folder, f"{video_title}.mp3")

        if os.path.exists(mp3_path):
            print("Video normalized")
            return self.normalize_audio(mp3_path)

        return "Download completed successfully!"

    def get_audio_opts(self):
        """Configure options for audio download without normalization"""
        postprocessors = [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {'key': 'FFmpegMetadata'},
            {'key': 'EmbedThumbnail'},
        ]

        self.ydl_opts = {
            'format': 'bestaudio',
            'outtmpl': f"{self.output_folder}/%(title)s.%(ext)s",
            'postprocessors': postprocessors,
            'writethumbnail': True,
            'embedthumbnail': True,
            'addmetadata': True,
        }

    def get_video_opts(self):
        """Configure options for downloading video."""
        self.ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': f"{self.output_folder}/%(title)s.%(ext)s",
            'quiet': True, 
            'noplaylist': True
        }

    def add_option(self, option):
        """Add a custom command line option"""
        if 'extra_args' not in self.ydl_opts:
            self.ydl_opts['extra_args'] = []
        self.ydl_opts['extra_args'].append(option)

    def add_audio_metadata(self):
        """Add ID3 metadata to downloaded audio files."""
        if not self.info:
            return "Error: No file information. Was it downloaded correctly?"

        entries = self.info.get('entries', [self.info]) 
        results = []

        for entry in entries:
            print({
                'title': entry.get('title'),
                'uploader': entry.get('uploader'),
                'playlist_title': entry.get('playlist_title'),
                'ext': entry.get('ext'),
                'filename': os.path.join(self.output_folder, f"{self.sanitize_filename(entry.get('title', 'Unknown'))}.mp3"),
            })
            if not entry:
                continue
            title = self.sanitize_filename(entry.get('title', 'Unknown Title'))
            artist = entry.get('uploader', 'Unknown Artist')
            album = entry.get('playlist_title', 'YouTube Playlist')
            filename = os.path.join(self.output_folder, f"{title}.mp3")

            if os.path.exists(filename):
                try:
                    try:
                        audio = EasyID3(filename)
                    except ID3NoHeaderError:
                        results.append(f"Warning: {filename} has no ID3 header, adding...")
                        audio = EasyID3()
                    
                    audio["title"] = title
                    audio["artist"] = artist
                    audio["album"] = album
                    audio.save()
                    results.append(f"Metadata added: {os.path.basename(filename)}")
                except Exception as e:
                    results.append(f"Error adding metadata to {filename}: {e}")
                    
        return "\n".join(results) if results else "No metadata to add."

    def normalize_audio(self, input_path):
        """Normalize audio using ffmpeg loudnorm filter"""
        temp_path = input_path.replace('.mp3', '_normalized.mp3')
        cmd = [
            'ffmpeg', '-i', input_path,
            '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
            '-y', temp_path
        ]
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode == 0:
            os.replace(temp_path, input_path)
            return f"Normalized: {os.path.basename(input_path)}"
        else:
            return f"Normalization failed: {result.stderr.decode()}"
