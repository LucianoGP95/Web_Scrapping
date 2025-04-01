import subprocess
import os
from get_a_single_tab import get_browser_url_specific
from get_all_tabs import get_all_pixiv_tabs
from utilities import get_config

# Path allocation
root_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(root_path)
# Configuration file loading
config_file = ".\\config\\config.txt"
config = get_config(config_file)
author_file = ".\\config\\authors.txt"
author_urls = get_config(author_file)
# Configuration variables assigment
directory_path = config.get("directory_path")

def download(urls):
    for url in urls:
        os.makedirs(directory_path, exist_ok=True)
        command = [
            "gallery-dl", 
            "--config", ".\\config\\config.json", 
            "-d", directory_path, 
            url
            ]
        print(f"Download for starting: {url}")
        subprocess.run(command)  # Queues all the downloads

def update_authors(author_urls):
    print("Updating authors")
    if not author_urls:
        print("No valid author URLs.")
        return
    
    print(f"Updating {len(author_urls)} authors...")
    authors = [author for author in author_urls.keys()]
    [print(author) for author in authors]

    urls = [url for url in author_urls.values()]
    download(urls)

def get_tabs(urls):
    if not urls:
        print("No valid URLs in open tabs.")
        return
    
    print(f"Downloading {len(urls)} tabs...")
    download(urls)

# Main script
update_authors(author_urls)
starting_url = get_browser_url_specific()
if starting_url.startswith("https://www.pixiv.net/en/artworks"):
    workflow = "https://www.pixiv.net/en/artworks"
    pixiv_urls = get_all_pixiv_tabs(workflow)
    get_tabs(pixiv_urls)
elif starting_url.startswith("https://www.pixiv.net/en/users"):
    workflow = "https://www.pixiv.net/en/users"
    pixiv_urls = get_all_pixiv_tabs(workflow)
    get_tabs(pixiv_urls)
else:
    print("No valid pixiv url")
    pass


