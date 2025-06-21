import os, time, sys
import soundfile as sf
from datasets import load_dataset, Audio

# Security check to make sure the script is run from the .ps1 file
if os.getenv("RUN_FROM_PS1") != "true":
    print("This script must be run via the PowerShell script!")
    time.sleep(3)
    sys.exit(1)

# Load dataset (non-streaming mode)
dataset = load_dataset('simon3000/genshin-voice', split='train', streaming=False)

# Ensure audio arrays are decoded
dataset = dataset.cast_column("audio", Audio())

character = "Tighnari"

# Filter for English(US), the specified character, and non-empty transcription
filtered_audio = dataset.filter(
    lambda v: v['language'] == 'English(US)' and v['speaker'] == character and v['transcription']
)

# Create output folder
audio_folder = os.path.abspath(f"./voices/{character}")
os.makedirs(audio_folder, exist_ok=True)

# Process and save audio + transcription
for i, voice in enumerate(filtered_audio):
    audio_info = voice.get('audio', {})
    audio_array = audio_info.get('array')
    sampling_rate = audio_info.get('sampling_rate')

    if audio_array is None or sampling_rate is None:
        print(f"Skipping entry {i} — no audio array found")
        continue

    audio_path = os.path.join(audio_folder, f"{i}_audio.wav")
    transcription_path = os.path.join(audio_folder, f"{i}_transcription.txt")

    print(f"Saving {audio_path}")
    sf.write(audio_path, audio_array, sampling_rate)

    with open(transcription_path, 'w', encoding='utf-8') as f:
        f.write(voice['transcription'])

    print(f"{i} done")
