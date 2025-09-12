import os
import requests

# List of (filename, url) pairs
icons = [
    ("museum-14.svg", "https://www.svgrepo.com/download/354645/museum-14.svg"),
    ("monument-14.svg", "https://www.svgrepo.com/download/354642/monument-14.svg"),
    ("guidepost-14.svg", "https://www.svgrepo.com/download/354616/guidepost-14.svg"),
    ("castle-14.svg", "https://www.svgrepo.com/download/354615/castle-14.svg"),
    ("ruins-14.svg", "https://www.svgrepo.com/download/354666/ruins-14.svg"),
    ("peak-14.svg", "https://www.svgrepo.com/download/354653/peak-14.svg"),
    ("rock-14.svg", "https://www.svgrepo.com/download/354667/rock-14.svg"),
    ("power-wind-14.svg", "https://www.svgrepo.com/download/354662/power-wind-14.svg"),
    ("mast-14.svg", "https://www.svgrepo.com/download/354634/mast-14.svg"),
    ("village-14.svg", "https://www.svgrepo.com/download/354668/village-14.svg"),
    ("memorial-14.svg", "https://www.svgrepo.com/download/354638/memorial-14.svg"),
    ("palette-14.svg", "https://www.svgrepo.com/download/354669/palette-14.svg"),
]

icons_dir = os.path.join(os.path.dirname(__file__), "icons")
os.makedirs(icons_dir, exist_ok=True)

for filename, url in icons:
    dest = os.path.join(icons_dir, filename)
    print(f"Downloading {filename} ...")
    r = requests.get(url)
    if r.status_code == 200:
        with open(dest, "wb") as f:
            f.write(r.content)
        print(f"Saved to {dest}")
    else:
        print(f"Failed to download {url} (status {r.status_code})")

print("All downloads complete.")
