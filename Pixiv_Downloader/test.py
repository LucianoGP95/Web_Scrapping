import subprocess
import os
from database import Database

def download(urls, base_dir):
    for url in urls:
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

#download(["https://www.pixiv.net/en/artworks/127775110"], "D://1_P//1Art//5_AI//pixiv")

db = Database("pixiv.db", rel_path="./database")
db.consult_tables()
db.examine_table("_62457019_user_wcaz2584")
db.close_conn()