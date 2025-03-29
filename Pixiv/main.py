import subprocess
import os
from get_all_tabs import get_all_pixiv_tabs
from utilities import get_config

root_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(root_path)
config_file = "config.txt"
config = get_config(config_file)
directory_path = config.get("directory_path")
print(directory_path)

def download_images(urls):
    if not urls:
        print("No valid URLs.")
        return
    
    print(f"Downloading {len(urls)} tabs...")

    for url in urls:
        os.makedirs(directory_path, exist_ok=True)
        command = ["gallery-dl", "-d", directory_path, url]
        print(f"Download starting: {url}")
        subprocess.run(command)  # Queues all the downloads

# Main script

pixiv_urls = get_all_pixiv_tabs()
download_images(pixiv_urls)
