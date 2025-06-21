import os

def find_txt_files_with_string(folder, search_text):
    results = []
    for filename in os.listdir(folder):
        if filename.endswith('.txt'):
            filepath = os.path.join(folder, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    if search_text in file.read():
                        results.append(filename)
            except Exception as e:
                print(f"Could not read {filename}: {e}")
    return results

# Usage
folder_path = r'C:\Codebase\Web_Scrapping\text_to_speech\voices\gorou'
search_string = 'General Gorou of'

matches = find_txt_files_with_string(folder_path, search_string)
print("Files containing the string:")
for f in matches:
    print(f)
