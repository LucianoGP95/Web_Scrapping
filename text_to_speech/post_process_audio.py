from pydub import AudioSegment
import os

# === Configuration ===
input_folder = os.path.abspath("./input")
output_folder = os.path.abspath("./output")
output_filepath = os.path.join(output_folder, "final_audio.mp3")  # You can use .wav, .ogg, etc.

# === Supported audio extensions ===
audio_extensions = (".mp3", ".wav", ".ogg", ".flac", ".m4a")

# === Load and join audio files ===
combined = AudioSegment.empty()

# Sort files to join in alphabetical order
for filename in sorted(os.listdir(input_folder)):
    if filename.lower().endswith(audio_extensions):
        file_path = os.path.join(input_folder, filename)
        print(f"Adding: {file_path}")
        audio = AudioSegment.from_file(file_path)
        combined += audio

# === Export the final audio ===
combined.export(output_filepath, format=output_filepath.split('.')[-1])
print(f"\n✅ Done! Output saved as: {output_filepath}")
