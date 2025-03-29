import time
import pygetwindow as gw
import pyperclip
import keyboard
from itertools import count

def get_all_pixiv_tabs():
    '''Scans all the tabs of the open browser to get all the urls and qeues the downloads for every one. Requires a maximized pixiv window on the screen'''
    print("Searching for active Pixiv windows...")
    browser_windows = [w for w in gw.getWindowsWithTitle("") if "pixiv" in w.title.lower() and not w.isMinimized]

    if not browser_windows:
        print("No Pixiv windows found.")
        return []
    else: 
        print("First window found:")
        print(browser_windows[0].title)

    browser_windows[0].activate()
    time.sleep(0.3)

    urls = set()
    iterator = count(start=0, step=1)
    for i in iterator:
        # Gets the url
        keyboard.press_and_release("ctrl+l")
        time.sleep(0.2)
        keyboard.press_and_release("ctrl+c")
        time.sleep(0.3)
        set_url = pyperclip.paste()
        # Checks if the url is repeated as stopping condition
        if set_url in urls:
            break
        # Filters undesired urls
        if set_url.startswith("https://www.pixiv.net/en/artworks") and set_url not in urls:
            urls.add(set_url)
        # Moves to the next tab
        keyboard.press_and_release("ctrl+tab")
        time.sleep(0.3)

    print(f"URLs detectadas: {urls}")
    return list(urls)

# Test script
if __name__ == "__main__":
    print(get_all_pixiv_tabs())