import re

class TextPreProcess:
    def __init__(self, input_file, output_file='output.txt', max_chars=300):
        self.input_file = input_file
        self.output_file = output_file
        self.max_chars = max_chars

    def load_text(self):
        try:
            with open(self.input_file, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            print(f"Error: El archivo {self.input_file} no existe.")
            return ""

    def remove_starred_text(self, text):
        """Remove text between *...* including multiline."""
        return re.sub(r'\*.*?\*', '', text, flags=re.DOTALL)

    def split_into_sentences(self, text):
        """Basic sentence splitter using punctuation."""
        return re.split(r'(?<=[.!?])\s+', text.strip())

    def delete_tags(self, sentences):
        new_sentences = []
        for sentence in sentences:
            # Si tiene tag "tag: texto", devolver solo "texto"
            if ":" in sentence:
                new_sentences.append(sentence.split(":", 1)[1].strip())
            else:
                new_sentences.append(sentence.strip())
        return new_sentences

    def generate_metadata(self, sentences):
        tags = []
        for sentence in sentences:
            tag = sentence.split(":", 1)[0].strip() if ":" in sentence else None
            tags.append(tag)
        sentences = self.delete_tags(sentences)
        return sentences, tags

    def group_sentences(self, sentences):
        """Group sentences into paragraphs of max_chars length."""
        paragraphs = []
        current_paragraph = ''
        for sentence in sentences:
            # +1 for space between sentences
            if len(current_paragraph) + len(sentence) + 1 <= self.max_chars:
                current_paragraph += (' ' if current_paragraph else '') + sentence
            else:
                if current_paragraph:
                    paragraphs.append(current_paragraph.strip())
                current_paragraph = sentence
        if current_paragraph:
            paragraphs.append(current_paragraph.strip())
        return paragraphs

    def save_output(self, paragraphs):
        with open(self.output_file, 'w', encoding='utf-8') as file:
            for p in paragraphs:
                file.write(p.strip() + '\n\n')

    def process(self, mode="paragraphs"):
        text = self.load_text()
        if not text:
            return [], []

        clean_text = self.remove_starred_text(text)
        sentences = self.split_into_sentences(clean_text)

        if mode == "sentences":
            sentences, metadata = self.generate_metadata(sentences)
            self.save_output(sentences)
            return sentences, metadata
        elif mode == "paragraphs":
            sentences = self.delete_tags(sentences)
            paragraphs = self.group_sentences(sentences)
            self.save_output(paragraphs)
            return paragraphs, None