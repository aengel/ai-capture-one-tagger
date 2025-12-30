
import os
import sys
import time
import argparse
import xml.etree.ElementTree as ET
from PIL import Image
from sentence_transformers import SentenceTransformer
import warnings
import torch
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Suppress warnings
warnings.filterwarnings("ignore")

# --- CONFIGURATION ---
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.arw', '.cr2', '.nef', '.dng', '.raf', '.orf'}

GENRES = [
    "Landscape", "Portrait", "Street Photography", "Macro", 
    "Bird", "Wildlife", "Architecture", "Abstract", "Night", "Astro"
]

# Universal Content
CONTENT_TAGS = [
    "dog", "cat", "tree", "mountain", "beach", "snow", 
    "water", "sun", "cloud", "forest", "road", "sky", "sunset"
]

# Specialized Lists
STREET_TAGS = [
    "neon", "shadows", "reflection", "silhouette", "bus", "taxi", "bicycle", 
    "subway", "train", "crowd", "umbrella", "rain", "night life", "urban geometry",
    "graffiti", "street art", "facade", "window", "concrete", "alley"
]

BIRD_SPECIES = [
    "Eagle", "Hawk", "Falcon", "Owl", "Sparrow", "Robin", "Blue Tit", "Great Tit",
    "Starling", "Blackbird", "Pigeon", "Dove", "Magpie", "Crow", "Raven", "Seagull",
    "Heron", "Stork", "Swan", "Duck", "Goose", "Pelican", "Kingfisher", "Woodpecker",
    "Parrot", "Flamingo", "Penguin", "Hummingbird", "Finches", "Swallow"
]

INSECT_SPECIES = [
    "Butterfly", "Moth", "Bee", "Wasp", "Ant", "Fly", "Dragonfly", "Damselfly",
    "Beetle", "Ladybug", "Spider", "Grasshopper", "Cricket", "Mantis", 
    "Caterpillar", "Snail", "Slug", "Mosquito"
]

# --- XMP HELPER FUNCTIONS ---
def get_xmp_path(image_path):
    """Returns the expected .xmp sidecar path."""
    return os.path.splitext(image_path)[0] + '.xmp'

def read_xmp_subjects(xmp_path):
    """Reads existing dc:subject keywords from XMP."""
    if not os.path.exists(xmp_path):
        return []
    
    try:
        with open(xmp_path, 'r', encoding='utf-8') as f:
            raw_data = f.read()
        
        # Simple extraction using regex
        import re
        subject_match = re.search(r'<dc:subject>(.*?)</dc:subject>', raw_data, re.DOTALL)
        if subject_match:
            items = re.findall(r'<rdf:li>(.*?)</rdf:li>', subject_match.group(1))
            return [str(item).strip() for item in items]
    except Exception as e:
        pass # Ignore read errors, assume empty
    
    return []

def is_already_tagged(image_path):
    xmp_path = get_xmp_path(image_path)
    if not os.path.exists(xmp_path):
        return False
    tags = read_xmp_subjects(xmp_path)
    return len(tags) > 0

def write_xmp_sidecar(image_path, keywords):
    """Creates or updates a basic XMP sidecar."""
    xmp_path = get_xmp_path(image_path)
    
    # Merge with existing
    existing = read_xmp_subjects(xmp_path)
    all_keywords = sorted(list(set(existing + keywords)))
    
    if not all_keywords:
        return

    # Basic XMP Template
    items_xml = "\n".join([f"    <rdf:li>{k}</rdf:li>" for k in all_keywords])
    
    xmp_content = f"""<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Adobe XMP Core 5.6-c140">
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about=""
    xmlns:dc="http://purl.org/dc/elements/1.1/">
   <dc:subject>
    <rdf:Bag>
{items_xml}
    </rdf:Bag>
   </dc:subject>
  </rdf:Description>
 </rdf:RDF>
</x:xmpmeta>"""

    try:
        with open(xmp_path, 'w', encoding='utf-8') as f:
            f.write(xmp_content)
    except Exception as e:
        print(f"Error writing XMP: {e}")

# --- AI FUNCTIONS ---
MODEL = None

def load_model():
    global MODEL
    if MODEL is None:
        print("Loading CLIP model (clip-ViT-B-32)...")
        MODEL = SentenceTransformer('clip-ViT-B-32')
    return MODEL

def get_top_tags(model, img, candidates, top_k=1, threshold=0.22):
    # Predict similarity
    similarity = model.similarity(model.encode(img), model.encode(candidates))
    scores = similarity[0].tolist()
    scored_candidates = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    
    return [tag for tag, score in scored_candidates[:top_k] if score > threshold]

def process_file(model, image_path):
    try:
        img = Image.open(image_path)
        
        # 1. Determine Genre
        # We allow up to 2 genres if they are close
        found_genres = get_top_tags(model, img, GENRES, top_k=2, threshold=0.23)
        
        tags = list(found_genres)
        
        # 2. General Content Check
        tags += get_top_tags(model, img, CONTENT_TAGS, top_k=2, threshold=0.22)
        
        # 3. Conditional Checks based on Genre
        # We check if *any* of the found genres match our criteria
        genre_str = " ".join(found_genres).lower()
        
        if "bird" in genre_str or "wildlife" in genre_str:
            # Check for specific birds
            tags += get_top_tags(model, img, BIRD_SPECIES, top_k=1, threshold=0.21)
            
        if "macro" in genre_str or "insect" in genre_str:
             # Check for insects
            tags += get_top_tags(model, img, INSECT_SPECIES, top_k=1, threshold=0.21)
            
        if "street" in genre_str or "architecture" in genre_str:
            # Check deeper street tags
            tags += get_top_tags(model, img, STREET_TAGS, top_k=3, threshold=0.20)

        # Cleanup duplicates
        return sorted(list(set(tags)))
        
    except Exception as e:
        print(f"Failed {image_path}: {e}")
        return []

# --- WATCHER ---
class NewImageHandler(FileSystemEventHandler):
    def __init__(self, model):
        self.model = model

    def on_created(self, event):
        if event.is_directory:
            return
        
        ext = os.path.splitext(event.src_path)[1].lower()
        if ext in IMAGE_EXTENSIONS:
            print(f"New file detected: {event.src_path}")
            # Wait a tick for file copy to complete
            time.sleep(1) 
            tag_and_write(self.model, event.src_path, force=True) # Always tag new files

# --- MAIN LOGIC ---

def tag_and_write(model, path, force=False):
    if not force:
        if is_already_tagged(path):
            print(f"Skipping (Already Tagged): {os.path.basename(path)}")
            return

    print(f"Processing: {os.path.basename(path)}...", end="\r")
    tags = process_file(model, path)
    if tags:
        print(f"Tagged {os.path.basename(path)}: {tags}          ")
        write_xmp_sidecar(path, tags)
    else:
        print(f"No reliable tags found for {os.path.basename(path)}          ")

def scan(folder, force=False):
    model = load_model()
    print(f"Scanning: {folder}")
    if force:
        print("FORCE MODE: Creating new tags for all files.")
    
    count = 0
    for root, _, files in os.walk(folder):
        for file in files:
            if os.path.splitext(file)[1].lower() in IMAGE_EXTENSIONS:
                path = os.path.join(root, file)
                tag_and_write(model, path, force=force)
                count += 1

def watch(folder):
    model = load_model()
    print(f"WATCH MODE: Monitoring {folder} for new images...")
    
    event_handler = NewImageHandler(model)
    observer = Observer()
    observer.schedule(event_handler, folder, recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Image Tagger for Capture One")
    parser.add_argument("folder", help="Folder to scan")
    parser.add_argument("--watch", action="store_true", help="Monitor folder for new files")
    parser.add_argument("--force", action="store_true", help="Retag all images even if XMP exists")
    
    args = parser.parse_args()
    
    if args.watch:
        watch(args.folder)
    else:
        scan(args.folder, force=args.force)
