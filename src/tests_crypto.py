from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, padding as sym_padding
from cryptography.hazmat.backends import default_backend
from secrets import token_bytes

# Generate RSA key pair
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

# Encrypt message with a symmetric key
message = """a cute kitten made out of metal, (cyborg:1.1), ([tail | detailed wire]:1.3), (intricate details), hdr, (intricate details, hyperdetailed:1.2), cinematic shot, vignette, centered
Negative prompt: (deformed, distorted, disfigured:1.3), poorly drawn, bad anatomy, wrong anatomy, extra limb, missing limb, floating limbs, (mutated hands and fingers:1.4), disconnected limbs, mutation, mutated, ugly, disgusting, blurry, amputation, flowers, human, man, woman
ENSD: 31337, Size: 768x1024, Seed: 1791574510, Model: Deliberate, Steps: 26, Sampler: Euler a, CFG scale: 6.5, Model hash: 9aba26abdf"""

symmetric_key = token_bytes(32)
iv = token_bytes(16)
cipher = Cipher(algorithms.AES(symmetric_key),
                modes.CBC(iv), backend=default_backend())
encryptor = cipher.encryptor()
padder = sym_padding.PKCS7(algorithms.AES.block_size).padder()
padded_message = padder.update(message.encode()) + padder.finalize()
encrypted_message = encryptor.update(padded_message) + encryptor.finalize()

# Encrypt symmetric key with RSA
encrypted_key = public_key.encrypt(symmetric_key, asym_padding.OAEP(
    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))

# Decrypt symmetric key with RSA
decrypted_key = private_key.decrypt(encrypted_key, asym_padding.OAEP(
    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))

# Decrypt message with symmetric key
cipher = Cipher(algorithms.AES(decrypted_key),
                modes.CBC(iv), backend=default_backend())
decryptor = cipher.decryptor()
unpadder = sym_padding.PKCS7(algorithms.AES.block_size).unpadder()
unpadded_message = unpadder.update(
    decryptor.update(encrypted_message)) + unpadder.finalize()
decrypted_message = unpadded_message.decode()

print(f'IV: {iv.hex()}')
print(f'Symmetric key: {symmetric_key.hex()}')
print(f'Encrypted key: {encrypted_key.hex()[:64]}...')
print(f'Decrypted key: {decrypted_key.hex()}')
print(f'Original message: {message}')
print(f'Encrypted message: {encrypted_message.hex()}')
print(f'Decrypted message: {decrypted_message}')
