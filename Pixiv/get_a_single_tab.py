import time
import pygetwindow as gw
import pyperclip
import subprocess
import keyboard
from selenium import webdriver

def get_browser_url_specific():
    # Print all window titles for debugging
    print("Active windows:")
    visible_windows = [w for w in gw.getWindowsWithTitle("") if "pixiv" in w.title and not w.isMinimized]
    
    for window in visible_windows:
        print(f"Visible window: {window.title}")  # Print visible window title

        # Make sure the window is in the foreground and active
        window.activate()
        time.sleep(0.5)  # Wait for the window to become active

        # Focus the address bar and copy the URL
        keyboard.press_and_release("ctrl+l")  # Select the address bar
        time.sleep(0.2)
        keyboard.press_and_release("ctrl+c")  # Copy URL
        time.sleep(0.5)

        url = pyperclip.paste()
        if url.startswith("http"):
            return url

    return None

# Get the URL(s)
url = get_browser_url_specific()
print(f"URL: {url}")

if url:
    print(f"Current url: {url}")
    # Execute gallery-dl for each URL
    command = "gallery-dl", url, "-d", r"D:\1_P\1Art\5 AI"
    subprocess.run(command)
else:
    print("No valid url found.")