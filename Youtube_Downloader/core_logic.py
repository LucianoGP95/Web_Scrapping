import os, re
import yt_dlp
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError

class Downloader:
    def __init__(self, url, output_folder):
        self.output_folder = output_folder
        self.url = url
        self.ydl_opts = {}  # Inicializar como diccionario vacío
        self.info = {}

    def sanitize_filename(self, filename):
        """Remueve caracteres no válidos para nombres de archivos."""
        return re.sub(r'[<>:"/\\|?*]', '', filename)

    def download_video(self):
        """Descarga el video/audio con las opciones configuradas."""
        # Obtener información sin descargar
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            self.info = ydl.extract_info(self.url, download=False)
        
        # Extraer datos del video
        video_title = self.sanitize_filename(self.info.get('title', 'unknown'))
        ext = self.info.get('ext', 'mp4')
        filename = os.path.join(self.output_folder, f"{video_title}.{ext}")

        # Verificar si el archivo ya existe
        if os.path.exists(filename):
            print(f"Skipping: {filename} already exists.")
            return

        # Descargar el video/audio
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([self.url])

    def get_audio_opts(self):
        """Configura las opciones para descargar solo audio."""
        self.ydl_opts = {
            'format': 'bestaudio',
            'outtmpl': f"{self.output_folder}/%(title)s.%(ext)s",
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                },
                {
                    'key': 'FFmpegMetadata',
                },
            ],
            'writethumbnail': False,
            'embedthumbnail': False,
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

        entries = self.info.get('entries', [self.info])  # Manejo de listas y videos individuales

        for entry in entries:
            if not entry:
                continue
            title = self.sanitize_filename(entry.get('title', 'Unknown Title'))
            artist = entry.get('uploader', 'Unknown Artist')
            album = entry.get('playlist_title', 'YouTube Playlist')
            filename = os.path.join(self.output_folder, f"{title}.mp3")

            if os.path.exists(filename):
                try:
                    # Verificar si el archivo tiene etiquetas ID3
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

""" output_path = ""

def download_video(url, output_folder="output_video"):
    # Get video info first
    ydl_opts_info = {'quiet': True, 'noplaylist': True}
    with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
        info = ydl.extract_info(url, download=False)  # Get video metadata
    
    video_title = info.get('title')
    ext = info.get('ext', 'mp4')  # Default to mp4 if no extension is found
    filename = f"{output_folder}/{video_title}.{ext}"
    
    # Check if file exists
    if os.path.exists(filename):
        print(f"Skipping: {filename} already exists.")
        return
    
    # Download the video
    ydl_opts = {
        'format': 'best',
        'outtmpl': filename,
        'noplaylist': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def download_audio(url, output_folder="output_audio"):
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Download entire playlist
    ydl_opts = {
        'format': 'bestaudio',
        'outtmpl': f"{output_folder}/%(title)s.%(ext)s",
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {
                'key': 'FFmpegMetadata',  # Ensures metadata is preserved
            },
        ],
        'writethumbnail': False,  # Download thumbnails if available
        'embedthumbnail': False,  # Embed thumbnails in MP3
        'addmetadata': True,  # Add metadata automatically
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    print("Download complete!")

    # Manually add metadata if needed
    for entry in info['entries']:
        if not entry:  # Skip empty entries
            continue
        title = entry.get('title', 'Unknown Title')
        artist = entry.get('uploader', 'Unknown Artist')
        album = entry.get('playlist_title', 'YouTube Playlist')
        filename = f"{output_folder}/{title}.mp3"

        if os.path.exists(filename):
            try:
                audio = EasyID3(filename)
                audio["title"] = title
                audio["artist"] = artist
                audio["album"] = album
                audio.save()
                print(f"Metadata added: {filename}")
            except Exception as e:
                print(f"Error adding metadata to {filename}: {e}")

# Example usage
#download_video("https://www.youtube.com/watch?v=9DJlKmw8TSM&list=PL0ZLaoztzqEMu7IEXHJjtKU05he9FTzZy&index=6&ab_channel=AmazonPrimeVideoEspa%C3%B1a")

download_audio("https://www.youtube.com/watch?v=hAdJKAordaE&list=PLVjh-wyn2z0shapFTld4TMa_HxsF7WIFg&index=3&ab_channel=DylanSkie") """