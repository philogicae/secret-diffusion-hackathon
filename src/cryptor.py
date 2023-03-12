from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization, padding as sym_padding
from cryptography.hazmat.backends import default_backend
from secrets import token_bytes


class Cryptor:
    SECRETS_DIR = "src/keys"

    @staticmethod
    def save_pk(name, pk):
        with open(f'{Cryptor.SECRETS_DIR}/{name}.txt', 'w') as f:
            f.write(pk)

    @staticmethod
    def load_pk(name):
        with open(f'{Cryptor.SECRETS_DIR}/{name}.txt', 'r') as f:
            return f.read()

    @staticmethod
    def generate_pk():
        pk = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        private_key_pem = pk.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return private_key_pem.decode()

    @staticmethod
    def public_key(pk):
        private_key_pem = pk.encode()
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None
        )
        return private_key.public_key()

    @staticmethod
    def encrypt(pk, message):
        public_key = Cryptor.public_key(pk)
        symmetric_key = token_bytes(32)
        iv = token_bytes(16)
        cipher = Cipher(algorithms.AES(symmetric_key),
                        modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        padder = sym_padding.PKCS7(algorithms.AES.block_size).padder()

        # Encrypt message with symmetric key and iv
        padded_message = padder.update(message.encode()) + padder.finalize()
        encrypted_message = encryptor.update(
            padded_message) + encryptor.finalize()

        # Encrypt symmetric key with RSA
        encrypted_key = public_key.encrypt(symmetric_key, asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
        return iv.hex() + encrypted_key.hex() + encrypted_message.hex()

    @staticmethod
    def decrypt(pk, secret):
        iv, encrypted_key, encrypted_message = bytes.fromhex(
            secret[:32]), bytes.fromhex(secret[32:544]), bytes.fromhex(secret[544:])

        # Decrypt symmetric key with RSA
        private_key_pem = pk.encode()
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None
        )
        decrypted_key = private_key.decrypt(encrypted_key, asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))

        # Decrypt message with symmetric key and iv
        cipher = Cipher(algorithms.AES(decrypted_key),
                        modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        unpadder = sym_padding.PKCS7(algorithms.AES.block_size).unpadder()
        unpadded_message = unpadder.update(
            decryptor.update(encrypted_message)) + unpadder.finalize()
        return unpadded_message.decode()


if __name__ == '__main__':
    message = 'Hello, world!'
    pk = Cryptor.generate_pk()
    secret = Cryptor.encrypt(pk, message)
    Cryptor.save_pk('pk', pk)
    # Later...
    pk = Cryptor.load_pk('pk')
    decrypted = Cryptor.decrypt(pk, secret)
    print(f'Message: {message}\nSecret: {secret}\nDecrypted: {decrypted}')
