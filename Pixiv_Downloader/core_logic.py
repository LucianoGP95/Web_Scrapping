import subprocess, os
from get_a_single_tab import get_browser_url_specific
from get_all_tabs import get_all_pixiv_tabs
from utilities import get_config

def download(urls, output_path):
    for url in urls:
        os.makedirs(output_path, exist_ok=True)
        command = [
            "gallery-dl", 
            "--config", ".\\config\\config.json", 
            "-d", output_path, 
            url
            ]
        print(f"Download for starting: {url}")
        subprocess.run(command)  # Queues all the downloads
        print("Finished download!")

def update_authors(author_urls, output_path):
    print("Updating authors")
    if not author_urls:
        print("No valid author URLs.")
        return
    author_amount =len(author_urls)
    print(f"Updating {len(author_urls)} authors...")
    authors = [author for author in author_urls.keys()]
    [print(f"{author}  total tracking: {author_amount}") for author in authors]

    urls = [url for url in author_urls.values()]
    download(urls, output_path)

def get_tabs(urls):
    if not urls:
        print("No valid URLs in open tabs.")
        return
    
    print(f"Downloading {len(urls)} tabs...")
    download(urls)

def download_tabs():
    # Get the starting maximized window and tab url
    starting_url = get_browser_url_specific()
    # Determine the workflow by using the starting url initial subtring
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

# Test script
if __name__ == "__main__":
    # Path allocation
    root_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(root_path)
    # Configuration file loading
    config_file = ".\\config\\config.txt"
    config = get_config(config_file)
    author_file = ".\\config\\authors.txt"
    author_urls = get_config(author_file)
    # Configuration variables assigment
    output_path = config.get("output_path")
    update_authors(author_urls)
    download_tabs()


