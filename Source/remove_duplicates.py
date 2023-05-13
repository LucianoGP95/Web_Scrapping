import os
from PIL import Image
import imagehash

def remove_duplicates(directory):
    image_hashes = {}
    
    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        # Skip non-image files
        if not os.path.isfile(file_path) or not file_path.lower().endswith(target_files):
            continue
        
        try:
            # Calculate the hash value of the image
            with Image.open(file_path) as img:
                hash_value = imagehash.average_hash(img)
        except (OSError, Image.UnidentifiedImageError):
            # Ignore files that cannot be opened as images
            continue
        
        # Check if the hash value already exists
        if hash_value in image_hashes:
            # Remove the duplicate image
            os.remove(file_path)
            print(f"Removed duplicate: {filename}")
        else:
            # Store the hash value for future comparison
            image_hashes[hash_value] = file_path

# Provide the path to the directory containing the pictures
remove_duplicates(directory_path)
