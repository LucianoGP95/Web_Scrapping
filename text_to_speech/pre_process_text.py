import re

class TextPreProcess:
    def __init__(self, input_file, output_file='output.txt', max_chars=300):
        self.input_file = input_file
        self.output_file = output_file
        self.max_chars = max_chars

    def load_text(self):
        with open(self.input_file, 'r', encoding='utf-8') as file:
            return file.read()

    def remove_starred_text(self, text):
        """Remove text marked by * to only keep conversations."""
        return re.sub(r'\*.*?\*', '', text, flags=re.DOTALL)

    def split_into_sentences(self, text):
        """Basic sentence splitter using punctuation."""
        return re.split(r'(?<=[.!?])\s+', text)

    def group_sentences(self, sentences):
        """Create paragraphs with a maximum number of characters."""
        paragraphs = []
        current_paragraph = ''
        for sentence in sentences:
            if len(current_paragraph) + len(sentence) + 1 <= self.max_chars:
                current_paragraph += (' ' if current_paragraph else '') + sentence
            else:
                if current_paragraph:
                    paragraphs.append(current_paragraph)
                current_paragraph = sentence
        if current_paragraph:
            paragraphs.append(current_paragraph)
        return paragraphs

    def save_output(self, paragraphs):
        with open(self.output_file, 'w', encoding='utf-8') as file:
            for p in paragraphs:
                file.write(p.strip() + '\n\n')

    def process(self):
        text = self.load_text()
        clean_text = self.remove_starred_text(text)
        sentences = self.split_into_sentences(clean_text)
        paragraphs = self.group_sentences(sentences)
        self.save_output(paragraphs)
        return paragraphs
