import os
from PIL import Image, ImageChops, ImageStat

# --- 1. LEVENSHTEIN DISTANCE FUNCTION ---
def levenshtein_distance(s1, s2):
    """
    Calculates the minimum number of single-character edits (insertions, deletions, or substitutions)
    required to change s1 into s2.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

# --- 2. HELPER TO GET FILES ---
def get_files(path, extensions, recursive=False):
    found_files = []
    if recursive:
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.lower().endswith(extensions) and f != '.DS_Store':
                    found_files.append(os.path.join(root, f))
    else:
        try:
            for f in os.listdir(path):
                if f.lower().endswith(extensions) and f != '.DS_Store':
                    found_files.append(os.path.join(path, f))
        except OSError:
            pass
    return found_files

# --- 3. PREPARE THE DATA ---
print("Scanning and aligning files...")

x_imgs = get_files('data', ('.png', '.jpg', '.jpeg'), recursive=True)
y_imgs = get_files('out', ('.png', '.jpg', '.jpeg'), recursive=False)
x_txts = get_files('data', ('.txt', '.py'), recursive=True)
y_txts = get_files('out', ('.txt', '.py'), recursive=False)

# Sort by filename
x_imgs.sort(key=lambda f: os.path.basename(f))
y_imgs.sort(key=lambda f: os.path.basename(f))
x_txts.sort(key=lambda f: os.path.basename(f))
y_txts.sort(key=lambda f: os.path.basename(f))

# --- 4. COMPARE IMAGES ---
print("\n--- Image Comparison ---")
for i, (path_x, path_y) in enumerate(zip(x_imgs, y_imgs)):
    name_x = os.path.basename(path_x)
    name_y = os.path.basename(path_y)
    match_tag = "MATCH" if name_x == name_y else "MISMATCH"
    
    try:
        img1 = Image.open(path_x).convert('RGB')
        img2 = Image.open(path_y).convert('RGB')
        
        if img1.size != img2.size:
            print(f"[{i}] {match_tag} names ({name_x}) | Dimensions differ: {img1.size} vs {img2.size}")
        else:
            diff = ImageChops.difference(img1, img2)
            stat = ImageStat.Stat(diff)
            avg_diff = sum(stat.mean)
            if avg_diff > 0:
                print(f"[{i}] {match_tag} names ({name_x}) | Avg Color Diff: {avg_diff:.4f}")
            else:
                print(f"[{i}] {match_tag} names ({name_x}) | Images are identical.")
    except Exception as e:
        print(f"[{i}] Error processing {name_x}: {e}")

# --- 5. COMPARE TEXT (NORMALIZED) ---
import os
import difflib

# --- LEVENSHTEIN DISTANCE FUNCTION (unchanged) ---
def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

# --- HELPER TO GET FILES (unchanged) ---
def get_files(path, extensions, recursive=False):
    found_files = []
    if recursive:
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.lower().endswith(extensions) and f != '.DS_Store':
                    found_files.append(os.path.join(root, f))
    else:
        try:
            for f in os.listdir(path):
                if f.lower().endswith(extensions) and f != '.DS_Store':
                    found_files.append(os.path.join(path, f))
        except OSError:
            pass
    return found_files

# --- MAIN LOGIC ---
print("Scanning and aligning files...")
x_txts = get_files('data', ('.txt', '.py'), recursive=True)
y_txts = get_files('out', ('.txt', '.py'), recursive=False)

x_txts.sort(key=lambda f: os.path.basename(f))
y_txts.sort(key=lambda f: os.path.basename(f))

print("\n--- Text Comparison ---")
for i, (path_x, path_y) in enumerate(zip(x_txts, y_txts)):
    name_x = os.path.basename(path_x)
    name_y = os.path.basename(path_y)
    match_tag = "MATCH" if name_x == name_y else "MISMATCH"
    
    try:
        with open(path_x, 'r', encoding='utf-8', errors='replace') as f1, \
             open(path_y, 'r', encoding='utf-8', errors='replace') as f2:
            
            words1 = f1.read().split()
            words2 = f2.read().split()
            
            # Calculate overall stats
            word_edits = levenshtein_distance(words1, words2)
            max_len = max(len(words1), len(words2))
            
            if max_len > 0:
                error_rate_percent = (word_edits / max_len) * 100
                print(f"[{i}] {match_tag} names ({name_x}) | Word Edits: {word_edits} | Error Rate: {error_rate_percent:.2f}%")
                
                # --- PRINT FIRST 15 WORD MISMATCHES ---
                if word_edits > 0:
                    matcher = difflib.SequenceMatcher(None, words1, words2)
                    count_words_printed = 0
                    limit = 15
                    
                    print(f"    First 15 Word Mismatches:")
                    
                    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                        if tag == 'equal':
                            continue
                        
                        # Get the mismatched chunk
                        chunk1 = words1[i1:i2] # Expected
                        chunk2 = words2[j1:j2] # Actual
                        
                        # If the chunk is larger than our remaining limit, slice it!
                        remaining = limit - count_words_printed
                        
                        # Prepare display strings (truncated if necessary)
                        c1_disp = chunk1[:remaining]
                        c2_disp = chunk2[:remaining]
                        
                        # Construct the string to print
                        str1_text = " ".join(c1_disp)
                        str2_text = " ".join(c2_disp)
                        
                        # Add ellipsis if we are truncating a long block
                        if len(chunk1) > remaining or len(chunk2) > remaining:
                            suffix = "..."
                        else:
                            suffix = ""

                        if tag == 'replace':
                            print(f"      * '{str1_text}{suffix}' -> '{str2_text}{suffix}'")
                            # Count how many words we just showed (max of expected vs actual)
                            count_words_printed += max(len(c1_disp), len(c2_disp))
                            
                        elif tag == 'delete':
                            print(f"      * '{str1_text}{suffix}' -> (MISSING)")
                            count_words_printed += len(c1_disp)
                            
                        elif tag == 'insert':
                            print(f"      * (MISSING) -> '{str2_text}{suffix}'")
                            count_words_printed += len(c2_disp)

                        if count_words_printed >= limit:
                            print("      ... (limit reached)")
                            break
                    print("") 
            else:
                print(f"[{i}] {match_tag} names ({name_x}) | Both files are empty.")
                
    except Exception as e:
        print(f"[{i}] Error processing {name_x}: {e}")