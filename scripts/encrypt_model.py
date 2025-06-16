# scripts/encrypt_model.py
from cryptography.fernet import Fernet

# Generate key and save it
key = Fernet.generate_key()
with open("../key/secret_key.txt", "wb") as f:
    f.write(key)
print("Encryption key saved.")

# Encrypt model
fernet = Fernet(key)
with open("../model/scripted_model.pt", "rb") as f:
    model_data = f.read()

encrypted = fernet.encrypt(model_data)

with open("../model/encrypted_model.enc", "wb") as f:
    f.write(encrypted)

print("Encrypted model saved.")
