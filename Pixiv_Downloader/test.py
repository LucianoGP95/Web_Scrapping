import os

root_path = os.path.dirname(os.path.realpath(__file__))
print(root_path)
folderpath = os.path.join(root_path, "folder")
print(folderpath)
filepath = os.path.join(root_path, os.path.join("folder", "file"))