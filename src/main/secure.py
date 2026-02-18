from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

# 1. Your 8-element input
input_arr = [10, 20, 30, 40, 50, 60, 70, 80]
data_bytes = bytes(input_arr)

# 2. Setup (Key must be 32 bytes, Nonce/IV must be 16 bytes for AES)
key = os.urandom(32) 
nonce = os.urandom(16)
base_nonce_int = int.from_bytes(nonce, 'big')
current_nonce_int = (base_nonce_int + 2) % (2**128)
current_nonce_bytes = current_nonce_int.to_bytes(16, 'big')

# 3. Initialize AES in CTR mode (Stream cipher mode)
cipher = Cipher(algorithms.AES(key), modes.CTR(current_nonce_bytes))
encryptor = cipher.encryptor()

# 4. Encrypt
encrypted_bytes = encryptor.update(data_bytes) + encryptor.finalize()

# 5. Convert back to a list of 8 elements
encrypted_arr = list(encrypted_bytes)

decryptor = cipher.decryptor()

# 3. Decrypt
decrypted_bytes = decryptor.update(encrypted_bytes) + decryptor.finalize()

# 4. Convert back to a list of integers
original_arr = list(decrypted_bytes)

print(input_arr)
print(f"Encrypted Input: {encrypted_arr}")
print(f"Decrypted Output: {original_arr}")

