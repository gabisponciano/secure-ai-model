from cryptography.fernet import Fernet
import torch
import tempfile
import os

# Carrega chave
with open("../key/secret_key.txt", "rb") as f:
    key = f.read()

fernet = Fernet(key)

# Descriptografa o modelo
with open("../model/encrypted_model.enc", "rb") as f:
    encrypted_model = f.read()

decrypted_model = fernet.decrypt(encrypted_model)

# Salva temporariamente para carregar
with tempfile.NamedTemporaryFile(delete=False, suffix=".pt") as tmp:
    tmp.write(decrypted_model)
    temp_model_path = tmp.name

# Carrega o modelo
model = torch.jit.load(temp_model_path)
model.eval()

# Inferência dummy
input_data = torch.rand(1, 28*28)
output = model(input_data)

print("Output:", output)

# Opcional: apaga o arquivo temporário
os.remove(temp_model_path)
