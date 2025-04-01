from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

def has_thumbnail(mp3_file):
    audio = MP3(mp3_file, ID3=ID3)
    for tag in audio.tags.values():
        if isinstance(tag, APIC):  # APIC stores album art
            return True
    return False

mp3_path = r"D:\1_P\Web_Scraper\Youtube_Downloader\downloads\audio\Ona Hei.mp3"  # Replace with your file path
print("Thumbnail found!" if has_thumbnail(mp3_path) else "No thumbnail found.")