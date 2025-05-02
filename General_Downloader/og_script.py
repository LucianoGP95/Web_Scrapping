import os
import json
import subprocess
import time
import pygetwindow as gw
import pyperclip
import keyboard
from itertools import count

def download(urls, base_dir=None):
    config_path = r"D:\1_P\Web_Scraper\Pixiv_Downloader\config\config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Map each supported source to its config key and url prefix
    sources = {
        "pixiv": {
            "key": "pixiv",
            "url_prefix": "https://www.pixiv.net/en/artworks"
        },
        "rule34": {
            "key": "rule34",
            "url_prefix": "https://rule34.xxx"
        },
        "danbooru": {
            "key": "danbooru",
            "url_prefix": "https://danbooru.donmai.us/posts"
        }
    }

    for url in urls:
        # Determine which source this url belongs to
        source = None
        for name, info in sources.items():
            if url.startswith(info["url_prefix"]):
                source = name
                break

        if not source:
            print(f"Unknown source for url: {url}")
            continue

        # Determine base_dir and archive_dir
        if not base_dir:
            base_dir_local = config["extractor"][sources[source]["key"]]["base-directory"]
            archive_dir = os.path.join(os.path.dirname(base_dir_local), "archive.txt")
        else:
            base_dir_local = base_dir
            archive_dir = os.path.join(os.path.dirname(base_dir_local), "archive.txt")

        os.makedirs(base_dir_local, exist_ok=True)
        command = [
            "gallery-dl",
            "-d", base_dir_local,
            "--download-archive", archive_dir,
            "--config", ".\\config\\config.json",
            "--write-metadata",
            url
        ]
        print(f"Download start: {url}")
        subprocess.run(command)

def get_browser_url_specific(galleries):
    '''Gets the url for the open window browser if it matches any gallery keyword.'''
    print("Active windows:")
    visible_windows = [
        w for w in gw.getWindowsWithTitle("")
        if any(gallery in w.title for gallery in galleries) and not w.isMinimized
    ]
    if not visible_windows:
        print("No valid window found")
        return "No window"
    for window in visible_windows:
        print(f"Visible window: {window.title}")
        window.activate()
        time.sleep(0.5)
        keyboard.press_and_release("ctrl+l")
        time.sleep(0.2)
        keyboard.press_and_release("ctrl+c")
        time.sleep(0.5)
        url = pyperclip.paste()
        if url.startswith("http"):
            return url
        else:
            print("No valid url found")
            return "No url"

def get_all_tabs(workflow: list, galleries: list):
    '''Scans all browser tabs to get all URLs and queues downloads for each one.'''
    print("Searching for active gallery windows...")
    browser_windows = [
        w for w in gw.getWindowsWithTitle("")
        if any(gallery in w.title for gallery in galleries) and not w.isMinimized
    ]

    if not browser_windows:
        print("No supported windows found.")
        return []
    else:
        print("First window found:")
        print(browser_windows[0].title)

    browser_windows[0].activate()
    time.sleep(0.3)

    urls = set()
    iterator = count(start=0, step=1)
    for i in iterator:
        keyboard.press_and_release("ctrl+l")
        time.sleep(0.2)
        keyboard.press_and_release("ctrl+c")
        time.sleep(0.3)
        set_url = pyperclip.paste()
        if not set_url.startswith("http"):
            print("Clipboard did not contain a valid URL, skipping...")
            continue
        if set_url in urls:
            break
        if any(set_url.startswith(w) for w in workflow) and set_url not in urls:
            urls.add(set_url)
        keyboard.press_and_release("ctrl+tab")
        time.sleep(0.3)

    print(f"URLs detected: {urls}")
    return list(urls)

if __name__ == "__main__":
    # Add "Danbooru" to galleries for window title matching
    galleries = ["Rule", "pixiv", "Danbooru", "danbooru"]
    # Add Danbooru to workflow for URL prefix matching
    workflow = [
        "https://rule34.xxx",
        "https://www.pixiv.net/en/artworks",
        "https://danbooru.donmai.us/posts"
    ]
    starting_url = get_browser_url_specific(galleries)
    if any(starting_url.startswith(w) for w in workflow):
        urls = get_all_tabs(workflow, galleries)
        base_dir = None
        download(urls, base_dir=base_dir)
