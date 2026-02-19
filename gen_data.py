import os
import random
import shutil
import requests
import string

# --- Configuration ---
ROOT_DIR = "data"
TOTAL_FILES = 50
MAX_DEPTH = 3         # How deep the folder structure can go
MAX_SUBDIRS = 2       # Max number of subfolders per folder folder

def clean_data_dir():
    """Removes the data directory if it exists and creates a new one."""
    if os.path.exists(ROOT_DIR):
        shutil.rmtree(ROOT_DIR)
    os.makedirs(ROOT_DIR)
    print(f"Cleaned and created '{ROOT_DIR}/' directory.")

def get_random_subpath(current_path, current_depth):
    """
    Recursively builds a random path. 
    It either stops at the current folder or goes deeper.
    """
    if current_depth >= MAX_DEPTH:
        return current_path
    
    # 80% chance to go deeper if not at max depth
    if random.random() > 0.2:
        # Create a random directory name
        dir_name = random.choice(['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta'])
        new_path = os.path.join(current_path, dir_name)
        
        if not os.path.exists(new_path):
            os.makedirs(new_path)
            
        return get_random_subpath(new_path, current_depth + 1)
    
    return current_path

def create_random_text_file(filename):
    """Creates a text file with 10 to 30,000 words."""
    word_count = random.randint(10, 30000)
    
    # A bank of lorem ipsum words
    word_bank = ["lorem", "ipsum", "dolor", "sit", "amet", "consectetur", 
                 "adipiscing", "elit", "python", "code", "data", "test", "variable"]
    
    # Generate content efficiently
    content = " ".join(random.choices(word_bank, k=word_count))
    
    with open(filename, "w") as f:
        f.write(content)
    
    return f"TXT ({word_count} words)"

def download_real_image(filename):
    """Downloads a REAL image with random dimensions between 200 and 2000 px."""
    width = random.randint(200, 700)
    height = random.randint(200, 700)
    
    # Picsum returns a real random photo of the specified size
    url = f"https://picsum.photos/{width}/{height}"
    
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            return f"IMG (Real Photo {width}x{height})"
        else:
            return f"ERROR: Failed to download image (Status {response.status_code})"
    except Exception as e:
        return f"ERROR: {e}"

def generate_dataset():
    clean_data_dir()
    
    print(f"Generating {TOTAL_FILES} files (Real Images + Text) in '{ROOT_DIR}'...")
    print("Downloading images requires an internet connection. Please wait...\n")
    
    for i in range(1, TOTAL_FILES + 1):
        # 1. Choose file type (50/50 chance)
        is_image = random.choice([True, False])
        
        # 2. Get a random directory path inside data/
        file_path = get_random_subpath(ROOT_DIR, 0)
        
        # 3. Create the file
        if is_image:
            name = f"photo_{i}.jpg"
            full_path = os.path.join(file_path, name)
            # Call the downloader
            desc = download_real_image(full_path)
        else:
            name = f"document_{i}.txt"
            full_path = os.path.join(file_path, name)
            # Call the text generator
            desc = create_random_text_file(full_path)
            
        print(f"[{i}/{TOTAL_FILES}] {full_path} -> {desc}")
        
    print("\nDone! Dataset generated.")

if __name__ == "__main__":
    generate_dataset()