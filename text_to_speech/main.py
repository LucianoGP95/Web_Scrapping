import os
import re
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS
from pre_process_text import TextPreProcess
from post_process_audio import AudioPostProcessor

# === Configuration ===
PROJECT = "Gorou"  # or "" if unnamed
AUDIO_PROMPT_PATH = os.path.abspath("./voices/Gorou.wav")
input_folder = os.path.abspath("./input")
output_folder = os.path.abspath("./output")
temp_folder = os.path.abspath("./temp")
os.makedirs(output_folder, exist_ok=True)
os.makedirs(temp_folder, exist_ok=True)

# Load model and processors
pre_processor = TextPreProcess(os.path.join(input_folder, "input.txt"), os.path.join(temp_folder, "temp.txt"))
post_processor = AudioPostProcessor(temp_folder, os.path.join(output_folder, f"{PROJECT or 'merged'}.wav"))
model = ChatterboxTTS.from_pretrained(device="cuda")

# Text to synthesize
paragraphs = pre_processor.process()

audio_files = []
for paragraph in paragraphs:
    if AUDIO_PROMPT_PATH:
        wav = model.generate(paragraph, audio_prompt_path=AUDIO_PROMPT_PATH)
    else:
        wav = model.generate(paragraph)

    # Determine output filename
    prefix = PROJECT if PROJECT else "unnamed"
    files = os.listdir(temp_folder)
    pattern = re.compile(rf"{re.escape(prefix)}_(\d+)\.wav")
    numbers = [int(m.group(1)) for f in files if (m := pattern.match(f))]
    next_number = max(numbers, default=0) + 1
    filename = f"{prefix}_{next_number}.wav"
    audio_files.append(filename)

    paragraph_file = os.path.join(temp_folder, filename)

    # Save audio
    ta.save(paragraph_file, wav, model.sr)
    print(f"Saved to {paragraph_file}")

# Join audio
post_processor.process(audio_files)
