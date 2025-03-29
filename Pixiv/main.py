import time
import pygetwindow as gw
import pyperclip
import subprocess
import keyboard
from get_all_tabs import get_all_pixiv_tabs

def download_images(urls):
    if not urls:
        print("No valid URLs.")
        return
    
    print(f"Downloading {len(urls)} tabs...")

    for url in urls:
        command = ["gallery-dl", "-d", r"D:\1_P\1Art\5 AI", url]
        print(f"Download starting: {url}")
        subprocess.run(command)  # Espera a que termine antes de continuar con la siguiente

# Ejecutar el proceso
pixiv_urls = get_all_pixiv_tabs()
download_images(pixiv_urls)
