import numpy as np
import config
import cv2
import os

def img_decompresser(frame: list, output_folder: str, frame_count: int, data_files: list[str], imgs_size: list[tuple[int, int]]) -> list:
    filename = os.path.join(output_folder, f"frame_{frame_count:04d}.{data_files[frame_count].split('.')[-1]}")

    os.makedirs('out', exist_ok=True)

    block_size = config.block_size
    input_h, input_w = 1080, 1920
    target_w, target_h = imgs_size[frame_count]

    # A. Sampling (Center of blocks)
    offset = block_size // 2
    sampled_grid = frame[:, offset:input_h:block_size, offset:input_w:block_size, :]

    # B. Thresholding
    bits_recovered = (sampled_grid > 127).astype(np.uint8)

    # C. Flatten to bit stream
    # Shape: (Total_Bits_Vertical, 3)
    # Because of our encoder Transpose, this is now correctly ordered:
    # Row 0: [Pixel0_Bit0_B, Pixel0_Bit0_G, Pixel0_Bit0_R]
    flat_bits = bits_recovered.reshape(-1, 3)

    # D. Truncate Padding
    total_pixels = target_w * target_h
    # We need exactly 8 rows per pixel (8 bits)
    required_rows = total_pixels * 8
    flat_bits = flat_bits[:required_rows]

    # E. Reshape for Packing
    # We group every 8 rows together. 
    # Shape becomes: (Pixels, 8_Bits, 3_Channels)
    flat_bits_grouped = flat_bits.reshape(total_pixels, 8, 3)

    # F. Pack Bits
    # We pack along axis 1 (the 8 bits).
    # Result: (Pixels, 1, 3)
    img_packed = np.packbits(flat_bits_grouped, axis=1)

    # G. Final Reshape
    img_final = img_packed.reshape(target_h, target_w, 3)

    cv2.imwrite(filename, img_final)