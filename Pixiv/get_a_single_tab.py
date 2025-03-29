import time
import pygetwindow as gw
import pyperclip
import subprocess
import keyboard

def get_browser_url_specific():
    '''Gets the url for the open window browser if it is a pixiv gallery. Requires a maximized pixiv window on the screen'''
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

# Test script
if __name__ == "__main__":
    print(get_browser_url_specific())