import subprocess
import os
from get_a_single_tab import get_browser_url_specific
from get_all_tabs import get_all_pixiv_tabs
from utilities import get_config, get_authors

# Path allocation
root_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(root_path)
# Configuration file loading
config_file = "config.txt"
config = get_config(config_file)
author_file = "authors.txt"
author_urls = get_authors(author_file)
# Configuration variables assigment
directory_path = config.get("directory_path")

def update_authors(author_urls):
    print("Updating authors")
    if not author_urls:
        print("No valid author URLs.")
        return
    
    print(f"Updating {len(author_urls)} authors...")

    for url in author_urls:
        os.makedirs(directory_path, exist_ok=True)
        command = ["gallery-dl", "-d", directory_path, url]
        print(f"Download starting: {url}")
        subprocess.run(command)  # Queues all the downloads

def download_images(urls):
    if not urls:
        print("No valid URLs in open tabs.")
        return
    
    print(f"Downloading {len(urls)} tabs...")

    for url in urls:
        os.makedirs(directory_path, exist_ok=True)
        command = ["gallery-dl", "-d", directory_path, url]
        print(f"Download starting: {url}")
        subprocess.run(command)  # Queues all the downloads

# Main script
print(author_urls)
update_authors(author_urls)
starting_url = get_browser_url_specific()
if starting_url.startswith("https://www.pixiv.net/en/artworks"):
    workflow = "https://www.pixiv.net/en/artworks"
    pixiv_urls = get_all_pixiv_tabs(workflow)
    download_images(pixiv_urls)
elif starting_url.startswith("https://www.pixiv.net/en/users"):
    workflow = "https://www.pixiv.net/en/users"
    pixiv_urls = get_all_pixiv_tabs(workflow)
    download_images(pixiv_urls)


