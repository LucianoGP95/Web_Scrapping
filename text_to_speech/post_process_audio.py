import os
from pydub import AudioSegment

class AudioPostProcessor:
    def __init__(self, input_folder, output_filepath, audio_extensions=None):
        self.input_folder = input_folder
        self.output_filepath = output_filepath
        self.audio_extensions = audio_extensions or (".mp3", ".wav", ".ogg", ".flac", ".m4a")

    def is_audio_file(self, filename):
        return filename.lower().endswith(self.audio_extensions)

    def join_audio_files(self, audio_files):
        combined = AudioSegment.empty()
        self.used_audio_files = []
        for filename in sorted(audio_files):
            if not self.is_audio_file(filename):
                #print(f"Skipping unsupported file: {filename}")
                continue
            file_path = os.path.join(self.input_folder, filename)
            if not os.path.isfile(file_path):
                print(f"File not found: {file_path}")
                continue
            print(f"Adding: {file_path}")
            audio = AudioSegment.from_file(file_path)
            combined += audio
            self.used_audio_files.append(file_path)
        return combined

    def export(self, audio_segment):
        format_ = self.output_filepath.split('.')[-1]
        audio_segment.export(self.output_filepath, format=format_)
        [os.remove(f) for f in self.used_audio_files]
        print(f"\n✅ Done! Output saved as: {self.output_filepath}")

    def process(self, audio_files):
        combined_audio = self.join_audio_files(audio_files)
        self.export(combined_audio)