import struct
import os
from PIL import Image
import numpy as np

def print_mp4_details(file_path):
    CONTAINERS = {b'moov', b'trak', b'mdia', b'minf', b'stbl', b'dinf', b'edts'}

    def parse_atoms(f, end_offset, indent_level=0):
        while f.tell() < end_offset:
            # 1. Read Header
            header_data = f.read(8)
            if len(header_data) < 8: break
            atom_size, atom_type = struct.unpack('>I4s', header_data)
            payload_size = atom_size - 8
            
            indent = "  " * indent_level
            print(f"{indent}[{atom_type.decode('utf-8', 'ignore')}] - Size: {atom_size:,} bytes")

            # 2. Logic: Dive into Containers, Parse Tables, or Skip Data
            if atom_type in CONTAINERS:
                parse_atoms(f, f.tell() + payload_size, indent_level + 1)
            
            # --- NEW: PARSE SAMPLE SIZES (stsz) ---
            elif atom_type == b'stsz':
                # Read Version (1) + Flags (3) = 4 bytes
                f.read(4) 
                
                # Read Uniform Size (4 bytes) & Sample Count (4 bytes)
                uniform_size, sample_count = struct.unpack('>II', f.read(8))
                
                print(f"{indent}  -> Sample Count: {sample_count}")
                
                if uniform_size == 0:
                    # Variable sizes: Read the table
                    print(f"{indent}  -> Table (Size per Frame):")
                    # Limit output to first 10 to avoid spamming console
                    for i in range(sample_count):
                        size = struct.unpack('>I', f.read(4))[0]
                        if i < 10: 
                            print(f"{indent}     Frame {i}: {size} bytes")
                        elif i == 10:
                            print(f"{indent}     ... (remaining {sample_count-10} frames hidden)")
                else:
                    print(f"{indent}  -> All frames are {uniform_size} bytes")
                    # Skip the rest if any (should strictly be end of atom)
                    remaining = payload_size - 12
                    f.seek(remaining, 1)

            # --- NEW: PARSE CHUNK OFFSETS (stco) ---
            elif atom_type == b'stco':
                # Read Version (1) + Flags (3) = 4 bytes
                f.read(4)
                
                # Read Entry Count (4 bytes)
                entry_count = struct.unpack('>I', f.read(4))[0]
                
                print(f"{indent}  -> Chunk Count: {entry_count}")
                print(f"{indent}  -> Table (File Offsets):")
                
                for i in range(entry_count):
                    offset = struct.unpack('>I', f.read(4))[0]
                    if i < 10:
                        print(f"{indent}     Chunk {i} @ Byte {offset}")
                    elif i == 10:
                        print(f"{indent}     ... (remaining {entry_count-10} chunks hidden)")

            else:
                # Skip generic payload
                f.seek(payload_size, 1)

    if not os.path.exists(file_path): return
    file_size = os.path.getsize(file_path)
    with open(file_path, 'rb') as f:
        print(f"File: {file_path} (Total: {file_size:,} bytes)\n" + "-"*40)
        parse_atoms(f, file_size)

# Run it on your file
print_mp4_details('video1.mp4')

import struct
import os

def get_frame0_bytes(filename, num_bytes=100):
    if not os.path.exists(filename):
        print(f"Error: {filename} not found.")
        return

    with open(filename, 'rb') as f:
        # 1. FIND THE OFFSET OF FRAME 0
        # We need to find the 'stco' atom inside moov -> trak -> mdia -> minf -> stbl
        # To keep it simple, we will search for the 'stco' byte signature directly.
        # (In production, you'd parse the tree properly, but this works for 99% of files)
        
        # Read the whole file into memory (okay for small files) to find 'stco'
        data = f.read()
        stco_pos = data.find(b'stco')
        
        if stco_pos == -1:
            print("Error: Could not find 'stco' atom (Index).")
            return

        # Jump to stco data
        # stco layout: [Size(4)] [Type(4)] [Version(1)+Flags(3)] [EntryCount(4)] [Offsets...]
        f.seek(stco_pos + 12) # Skip Size(4) + Type(4) + Ver/Flags(4)
        
        # Read the number of chunks (though we only care about the first one)
        entry_count = struct.unpack('>I', f.read(4))[0]
        
        # Read the FIRST offset (4 bytes, Big Endian)
        # This is the location of Frame 0 in the file
        frame0_offset = struct.unpack('>I', f.read(4))[0]
        
        print(f"-> Found 'stco' at byte {stco_pos}")
        print(f"-> Frame 0 starts at File Byte: {frame0_offset}")
        
        # 2. SEEK AND READ
        f.seek(frame0_offset)
        raw_bytes = f.read(num_bytes)
        
        # 3. PRINT OUTPUT
        print(f"\n--- First {num_bytes} Bytes of Frame 0 ---")
        print_hex_dump(raw_bytes)

def print_hex_dump(data):
    # Helper to print nicely formatted Hex + ASCII
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_str = ' '.join(f'{b:02X}' for b in chunk)
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f"{i:04x}  {hex_str:<48}  |{ascii_str}|")

# Run it
get_frame0_bytes('video1.mp4')

img = Image.open('data/extracted_2.jpg')

resized_img = img.resize((1280, 720))

frame = np.array(resized_img)


import numpy as np

def inspect_raw_frame():
    # 1. Create the frame exactly as you do in your code
    # (Let's recreate your (1,1,1) frame example)
    width, height = 1280, 720
    
    # Create a frame where every pixel is (1, 1, 1) - dark gray/black
    img = Image.open('data/extracted_2.jpg')

    resized_img = img.resize((1280, 720))

    frame = np.array(resized_img)

    # 2. Convert to raw bytes (flat stream)
    raw_bytes = frame.tobytes()
    
    # 3. Print the first 100 bytes
    print(f"--- First 100 Raw Bytes of Frame in RAM ---")
    print(f"Total Frame Size: {len(raw_bytes):,} bytes")
    print("-" * 50)
    
    # Helper to print nicely
    for i in range(0, 100, 16):
        chunk = raw_bytes[i:i+16]
        hex_str = ' '.join(f'{b:02X}' for b in chunk)
        # ASCII representation (replace non-printable with .)
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f"{i:04x}  {hex_str:<48}  |{ascii_str}|")

inspect_raw_frame()