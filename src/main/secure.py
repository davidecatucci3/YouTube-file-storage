import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def fast_256_transform(input_32_bytes, key_32_bytes):
    if len(input_32_bytes) != 32 or len(key_32_bytes) != 32:
        raise ValueError("Input and Key must be exactly 32 bytes.")

    cipher = Cipher(algorithms.AES(key_32_bytes), modes.ECB())
    encryptor = cipher.encryptor()
    
    return encryptor.update(input_32_bytes) + encryptor.finalize()

def fast_256_revert(output_32_bytes, key_32_bytes):
    cipher = Cipher(algorithms.AES(key_32_bytes), modes.ECB())
    decryptor = cipher.decryptor()

    return decryptor.update(output_32_bytes) + decryptor.finalize()

# --- Execution ---
secret_key = os.urandom(32)  # Your 256-bit Key
raw_input = os.urandom(32)   # Your 256-bit Input Data

# Transform
encoded = fast_256_transform(raw_input, secret_key)
# Revert
original = fast_256_revert(encoded, secret_key)

print(f"Input (Hex):  {raw_input.hex()}")
print(f"Output (Hex): {encoded.hex()}")
print(f"Match:        {raw_input == original}")

bits = ''.join(format(byte, '08b') for byte in encoded)
bits_hex = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))