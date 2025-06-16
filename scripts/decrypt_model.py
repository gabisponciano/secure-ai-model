import io
from cryptography.fernet import Fernet
import torch

def load_key(path):
    return open(path, "rb").read()

def decrypt_model(enc_model_path: str, key: bytes) -> bytes:
    with open(enc_model_path, "rb") as f:
        encrypted_data = f.read()
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data)
    return decrypted_data

def load_model_from_bytes(model_bytes: bytes):
    buffer = io.BytesIO(model_bytes)
    model = torch.load(buffer, map_location=torch.device("cpu"), weights_only=False)
    model.eval()
    return model

