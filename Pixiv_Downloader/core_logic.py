import subprocess, os
from get_a_single_tab import get_browser_url_specific
from get_all_tabs import get_all_pixiv_tabs
from utilities import get_config

def download(urls, base_dir, db):
    for url in urls:
        duplicate_check = check_database(url, db)
        if duplicate_check:
            print(f"Previously downloaded!\nSkipping {url}")
            continue
        os.makedirs(base_dir, exist_ok=True)
        command = [
        "gallery-dl",
        "-d", base_dir,
        "--config", ".\\config\\config.json",
        "--write-metadata",
        url
        ]
        print(f"Download for starting: {url}")
        subprocess.run(command)  # Queues all the downloads
        print("Finished download!")

def update_authors(author_urls, base_dir, db):
    print("Updating authors")
    if not author_urls:
        print("No valid author URLs.")
        return
    author_amount =len(author_urls)
    print(f"Updating {len(author_urls)} authors...")
    authors = [author for author in author_urls.keys()]
    [print(f"{author}  total tracking: {author_amount}") for author in authors]

    urls = [url for url in author_urls.values()]
    download(urls, base_dir, db)

def get_tabs(urls, base_dir, db):
    if not urls:
        print("No valid URLs in open tabs.")
        return
    
    print(f"Downloading {len(urls)} tabs...")
    download(urls, base_dir, db)

def download_tabs(base_dir, db):
    # Get the starting maximized window and tab url
    starting_url = get_browser_url_specific()
    # Determine the workflow by using the starting url initial subtring
    if starting_url.startswith("https://www.pixiv.net/en/artworks"):
        workflow = "https://www.pixiv.net/en/artworks"
        pixiv_urls = get_all_pixiv_tabs(workflow)
        get_tabs(pixiv_urls, base_dir, db)
    elif starting_url.startswith("https://www.pixiv.net/en/users"):
        workflow = "https://www.pixiv.net/en/users"
        pixiv_urls = get_all_pixiv_tabs(workflow)
        get_tabs(pixiv_urls, base_dir, db)
    else:
        print("No valid pixiv url")
        pass

def check_database(url, db):
    id = url.split("/")[-1]
    db.reconnect("pixiv.db")
    repeated = db.is_url_downloaded(id)
    db.close_conn()
    return repeated

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
    base_dir = config.get("base_dir")
    update_authors(author_urls)
    download_tabs(base_dir)


