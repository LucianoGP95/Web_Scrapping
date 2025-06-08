import re

def load_text(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

def remove_starred_text(text):
    "Remove text marked by * to only keep conversations."
    return re.sub(r'\*.*?\*', '', text, flags=re.DOTALL)

def split_into_sentences(text):
    "Basic sentence splitter using punctuation."
    return re.split(r'(?<=[.!?])\s+', text)

def group_sentences(sentences, max_chars=300):
    "Create paragraphs with sentences with a maxiumn numbers of characters."
    paragraphs = []
    current_paragraph = ''
    for sentence in sentences:
        if len(current_paragraph) + len(sentence) + 1 <= max_chars:
            current_paragraph += (' ' if current_paragraph else '') + sentence
        else:
            if current_paragraph:
                paragraphs.append(current_paragraph)
            current_paragraph = sentence
    if current_paragraph:
        paragraphs.append(current_paragraph)
    return paragraphs

def save_output(paragraphs, filename='output.txt'):
    with open(filename, 'w', encoding='utf-8') as file:
        for p in paragraphs:
            file.write(p.strip() + '\n\n')

# Main process
text = load_text('input.txt')
clean_text = remove_starred_text(text)
sentences = split_into_sentences(clean_text)
paragraphs = group_sentences(sentences, max_chars=300)
save_output(paragraphs)
