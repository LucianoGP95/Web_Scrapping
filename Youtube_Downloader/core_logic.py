import os, re
import yt_dlp
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError

class Downloader:
    def __init__(self, url, output_folder):
        self.output_folder = output_folder
        self.url = url
        self.ydl_opts = {}
        self.info = {}

    def sanitize_filename(self, filename):
        """Remove non-valid windows characters."""
        return re.sub(r'[<>:"/\\|?*]', '', filename)

    def download_video(self, progress_callback=None):
        """Download video/audio with the correct settings."""
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            self.info = ydl.extract_info(self.url, download=False)

        video_title = self.sanitize_filename(self.info.get('title', 'unknown'))
        ext = self.info.get('ext', 'mp4')
        filename = os.path.join(self.output_folder, f"{video_title}.{ext}")

        if os.path.exists(filename):
            print(f"Skipping: {filename} already exists.")
            return

        def hook(d):
            if progress_callback and d['status'] == 'downloading':
                progress_callback(d['_percent_str'])

        self.ydl_opts['progress_hooks'] = [hook]

        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([self.url])

    def get_audio_opts(self):
        """Configura las opciones para descargar solo audio."""
        self.ydl_opts = {
            'format': 'bestaudio',
            'outtmpl': f"{self.output_folder}/%(title)s.%(ext)s",
            'postprocessors': [
                {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
                {'key': 'FFmpegMetadata'},
                {'key': 'EmbedThumbnail'},
            ],
            'writethumbnail': True,
            'embedthumbnail': True,
            'addmetadata': True,
        }

    def get_video_opts(self):
        """Configura las opciones para descargar video."""
        self.ydl_opts = {
            'outtmpl': f"{self.output_folder}/%(title)s.%(ext)s",
            'quiet': True, 
            'noplaylist': True
        }

    def add_audio_metadata(self):
        """Añade metadatos ID3 a los archivos de audio descargados."""
        if not self.info:
            print("Error: No hay información del archivo. ¿Se descargó correctamente?")
            return

        entries = self.info.get('entries', [self.info]) 

        for entry in entries:
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
                        print(f"Warning: {filename} no tiene encabezado ID3, añadiendo...")
                        audio = EasyID3()
                    
                    audio["title"] = title
                    audio["artist"] = artist
                    audio["album"] = album
                    audio.save()
                    print(f"Metadata added: {filename}")
                except Exception as e:
                    print(f"Error adding metadata to {filename}: {e}")

if __name__ == "__main__":
    extract_audio = True
    downloader = Downloader("https://www.youtube.com/watch?v=hAdJKAordaE", "output_audio")

    if extract_audio:
        downloader.get_audio_opts()
    else:
        downloader.get_video_opts()

    downloader.download_video()

    if extract_audio:
        downloader.add_audio_metadata()