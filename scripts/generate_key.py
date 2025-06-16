from cryptography.fernet import Fernet

def generate_key():
    key = Fernet.generate_key()
    with open("key/secret.key", "wb") as key_file:
        key_file.write(key)
    print(f"Chave Fernet gerada e salva em key/secret.key:\n{key.decode()}")

if __name__ == "__main__":
    generate_key()
