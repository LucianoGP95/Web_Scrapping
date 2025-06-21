import os
import re
import csv
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS
from pre_process_text import TextPreProcess
from post_process_audio import AudioPostProcessor

def determine_output_filename(folderpath: str, project: str) -> str:
    prefix = project if project else "unnamed"
    files = os.listdir(folderpath)
    pattern = re.compile(rf"{re.escape(prefix)}_(\d+)\.wav")
    numbers = [int(m.group(1)) for f in files if (m := pattern.match(f))]
    next_number = max(numbers, default=0) + 1
    filename = f"{prefix}_{next_number}.wav"
    print(f"Processing {filename}")
    return filename

def synthesize_audio(input_texts: list, metadata: list | None, project: str) -> list:
    audio_files = []
    os.makedirs(temp_folder, exist_ok=True)

    with open(os.path.join(output_folder, 'log.csv'), 'w', encoding='utf-8', newline='') as log_file:
        writer = csv.writer(log_file)
        writer.writerow(['Texto', 'Archivo de audio', 'Voz'])

        for i, input_text in enumerate(input_texts):
            print(f"Processing {i+1} items of {len(input_texts)}")
            use_metadata = metadata is not None and metadata[i]
            if AUDIO_PROMPT_PATH or use_metadata:  # Voice cloning
                ref_voice = os.path.abspath(f"./voices/{metadata[i]}_voice_1.wav") if use_metadata else AUDIO_PROMPT_PATH
                wav = model.generate(input_text, audio_prompt_path=ref_voice, exaggeration=EXAGGERATION, cfg_weight=CFG)
                voice_name = metadata[i] if use_metadata else "Default"
            else:  # Random voice
                wav = model.generate(input_text, exaggeration=EXAGGERATION, cfg_weight=CFG)
                voice_name = "Random"

            filename_temp = determine_output_filename(temp_folder, project)
            paragraph_file = os.path.join(temp_folder, filename_temp)
            audio_files.append(paragraph_file)

            ta.save(paragraph_file, wav, model.sr)
            print(f"Saved to {paragraph_file}")

            writer.writerow([input_text, paragraph_file, voice_name])

    # Join all audio files into one final output
    filename_output = determine_output_filename(output_folder, project)
    post_processor = AudioPostProcessor(temp_folder, os.path.join(output_folder, filename_output))
    post_processor.process(audio_files)

    return audio_files

# === Configuración ===
PROJECT = "Gorou"
AUDIO_PROMPT_PATH = os.path.abspath("./voices/Gorou_voice_1.wav")
EXAGGERATION = 0.8
CFG = 1 # Pace
MODE = "sentences"  # "paragraphs" o "sentences"
input_folder = os.path.abspath("./input")
output_folder = os.path.abspath("./output")
temp_folder = os.path.abspath("./temp")
os.makedirs(output_folder, exist_ok=True)

# === Entrada principal ===
if __name__ == "__main__":
    model = ChatterboxTTS.from_pretrained(device="cuda")
    pre_processor = TextPreProcess(
        os.path.join(input_folder, "input.txt"),
        os.path.join(temp_folder, "temp.txt")
    )

    result = pre_processor.process(mode=MODE)
    if not result or (MODE == "sentences" and not result[0]):
        print("No se encontró texto válido. Abortando.")
        exit(1)

    if MODE == "paragraphs":
        paragraphs = result[0]
        audio_files = synthesize_audio(paragraphs, None, PROJECT)
    else:
        sentences, metadata = result
        audio_files = synthesize_audio(sentences, metadata, PROJECT)