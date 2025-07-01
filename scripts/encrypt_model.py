from cryptography.fernet import Fernet

def load_key():
    return open("key/secret.key", "rb").read()

def encrypt_model(model_path: str, enc_path: str, key: bytes):
    with open(model_path, "rb") as f:
        data = f.read()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    with open(enc_path, "wb") as f:
        f.write(encrypted)
    print(f"Model '{model_path}' encrypted and saved to '{enc_path}'")

if __name__ == "__main__":
    key = load_key()
    encrypt_model("model/model.pth", "model/model.pth.enc", key)
