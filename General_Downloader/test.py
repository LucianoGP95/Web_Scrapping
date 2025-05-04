import os

def rename_files_ending_with_jpg(root_folder):
    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            name, ext = os.path.splitext(filename)
            if name.endswith('.jpg'):
                new_name = name[:-4] + ext  # Remove 'jpg' from end of name, keep extension
                old_path = os.path.join(dirpath, filename)
                new_path = os.path.join(dirpath, new_name)
                os.rename(old_path, new_path)
                print(f'Renamed: {old_path} -> {new_path}')

# Example usage
rename_files_ending_with_jpg(r'C:\Users\lucio\Downloads\gallery_dl')