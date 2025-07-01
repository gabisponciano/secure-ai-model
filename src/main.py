import time
from scripts.decrypt_model import load_key, decrypt_model
import torch
import io
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_model_from_bytes(model_bytes: bytes):
    buffer = io.BytesIO(model_bytes)
    model = torch.load(buffer, map_location=torch.device("cpu"), weights_only=False)
    model.eval()
    return model

def main():
    print("Decrypting model...")

    key_path = resource_path("key/secret.key")
    enc_model_path = resource_path("model/model.pth.enc")

    key = load_key(key_path)
    model_bytes = decrypt_model(enc_model_path, key)

    print("Loading model into memory...")
    model = load_model_from_bytes(model_bytes)

    dummy_input = torch.randn(1, 3, 640, 640)

    print("Running inference with YOLOv8...")

    start_time = time.time()
    with torch.no_grad():
        output = model(dummy_input)
    end_time = time.time()

    elapsed = end_time - start_time
    print(f"Inference output: {output}")
    print(f"Inference time: {elapsed:.4f} seconds")

if __name__ == "__main__":
    main()
