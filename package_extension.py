#!/usr/bin/env python3
import os
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ZIP_OUTPUT = os.path.join(BASE_DIR, "youtube-noai-brave.zip")

FILES_TO_PACK = [
    "manifest.json",
    "background.js",
    "content/main-world-trap.js",
    "content/content.js",
    "content/content.css",
    "popup/popup.html",
    "popup/popup.css",
    "popup/popup.js",
    "icons/icon-16.png",
    "icons/icon-48.png",
    "icons/icon-128.png"
]

def build_zip():
    print(f"Packaging extension into: {ZIP_OUTPUT}")
    with zipfile.ZipFile(ZIP_OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel_path in FILES_TO_PACK:
            full_path = os.path.join(BASE_DIR, rel_path)
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"Missing required file: {full_path}")
            zf.write(full_path, arcname=rel_path)
            print(f" + Added {rel_path} ({os.path.getsize(full_path)} bytes)")

    print(f"\nSuccessfully built {ZIP_OUTPUT} ({os.path.getsize(ZIP_OUTPUT)} bytes)")

if __name__ == "__main__":
    build_zip()
