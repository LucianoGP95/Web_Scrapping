import os
from pathlib import Path
import torch
import clip
from PIL import Image

input_folder = r"D:\1_P\Nuevo"
real_folder = r"D:\1_P\Real"
pictures_folder = r"D:\1_P\Pictures"

# Make sure folders exist
os.makedirs(real_folder, exist_ok=True)
os.makedirs(pictures_folder, exist_ok=True)

# Acceptable extensions
valid_exts = (".jpg", ".jpeg", ".png", ".webp", ".jtif")

# CLIP setup
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)
text = clip.tokenize(["a real porn photo", "an anime porn drawing"]).to(device)

# Process each picture
for filename in os.listdir(input_folder):
    if not filename.lower().endswith(valid_exts):
        continue

    try:
        pic_path = os.path.join(input_folder, filename)
        image = preprocess(Image.open(pic_path).convert("RGB")).unsqueeze(0).to(device)

        with torch.no_grad():
            image_features = model.encode_image(image)
            text_features = model.encode_text(text)
            probs = (image_features @ text_features.T).softmax(dim=-1)

        real_prob = probs[0][0].item()
        drawing_prob = probs[0][1].item()

        print(f"{filename} — Real: {real_prob:.4f}, Drawing: {drawing_prob:.4f}")

        if real_prob > drawing_prob:
            dest_path = os.path.join(real_folder, filename)
        else:
            dest_path = os.path.join(pictures_folder, filename)

        Path(pic_path).rename(dest_path)

    except Exception as e:
        print(f"Error processing {filename}: {e}")
