"""
Sistema de Criptografia Híbrida para Modelos de Machine Learning

Este módulo implementa um sistema de criptografia híbrida (AES + RSA) para proteger
modelos de Machine Learning. Utiliza criptografia simétrica AES-GCM para o modelo
e criptografia assimétrica RSA-OAEP para proteger a chave AES.

Arquitetura de Segurança:
- AES-GCM 128-bit para criptografia rápida do modelo (simétrica)
- RSA-OAEP com SHA-256 para proteção da chave AES (assimétrica)
- Nonce único gerado aleatoriamente para cada criptografia
- Autenticação integrada via AES-GCM

Fluxo de Criptografia:
1. Gera chave AES aleatória de 128 bits
2. Criptografa o modelo com AES-GCM
3. Criptografa a chave AES com RSA público
4. Salva modelo criptografado (nonce + dados) e chave protegida

Arquivos de Saída:
- model.pth.enc: Modelo criptografado (nonce + dados criptografados)
- aes_key.enc: Chave AES criptografada com RSA

Dependências:
    - cryptography: Biblioteca de criptografia moderna

Autor: [Seu Nome]
Data: [Data]  
Versão: 1.0
"""

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
import os


def encrypt_model(model_path, enc_model_path, enc_key_path, public_key_path):
    """
    Criptografa um modelo usando sistema híbrido AES-GCM + RSA-OAEP.
    
    Implementa criptografia híbrida combinando velocidade da criptografia simétrica
    com a segurança da criptografia assimétrica. O modelo é criptografado com AES-GCM
    e a chave AES é protegida com RSA-OAEP.
    
    Args:
        model_path (str): Caminho para o arquivo do modelo a ser criptografado
        enc_model_path (str): Caminho de saída para o modelo criptografado
        enc_key_path (str): Caminho de saída para a chave AES criptografada
        public_key_path (str): Caminho para a chave pública RSA em formato PEM
    
    Raises:
        FileNotFoundError: Se algum arquivo de entrada não existir
        PermissionError: Se não tiver permissões para ler/escrever arquivos
        ValueError: Se a chave pública RSA for inválida ou corrompida
        OSError: Se não conseguir criar diretórios de saída
    
    Returns:
        None
    
    Security Features:
        - Chave AES única gerada aleatoriamente para cada execução
        - Nonce único de 12 bytes para AES-GCM (padrão recomendado)
        - RSA-OAEP com MGF1-SHA256 para máxima segurança
        - Autenticação integrada via AES-GCM (detecta alterações)
    
    File Format:
        - Modelo criptografado: [12 bytes nonce] + [dados AES-GCM criptografados]
        - Chave criptografada: [dados RSA-OAEP criptografados]
    
    Example:
        >>> encrypt_model(
        ...     "model.pth", 
        ...     "encrypted/model.pth.enc",
        ...     "encrypted/aes_key.enc", 
        ...     "keys/public.pem"
        ... )
        Model and AES key encrypted.
    
    Note:
        - Cria automaticamente diretórios pai se não existirem
        - Sobrescreve arquivos de saída existentes sem aviso
        - Chave AES de 128 bits oferece segurança adequada com boa performance
        - Nonce é incluído no arquivo para não precisar ser gerenciado separadamente
    """
    # Gerar chave AES aleatória de 128 bits
    aes_key = AESGCM.generate_key(bit_length=128)
    
    # Gerar nonce único para esta operação de criptografia
    nonce = os.urandom(12)  # 12 bytes é o tamanho recomendado para AES-GCM
    
    # Inicializar cifra AES-GCM
    aesgcm = AESGCM(aes_key)

    # Ler dados do modelo original
    with open(model_path, "rb") as f:
        model_data = f.read()

    # Criptografar modelo com AES-GCM
    encrypted_model = aesgcm.encrypt(nonce, model_data, None)
    
    # Criar diretório de saída se necessário
    os.makedirs(os.path.dirname(enc_model_path), exist_ok=True)
    
    # Salvar modelo criptografado (nonce + dados criptografados)
    with open(enc_model_path, "wb") as f:
        f.write(nonce + encrypted_model)

    # Carregar chave pública RSA
    with open(public_key_path, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())

    # Criptografar chave AES com RSA-OAEP
    encrypted_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),  # MGF1 com SHA-256
            algorithm=hashes.SHA256(),                     # Hash principal SHA-256
            label=None                                     # Sem label adicional
        )
    )

    # Criar diretório para chave se necessário
    os.makedirs(os.path.dirname(enc_key_path), exist_ok=True)
    
    # Salvar chave AES criptografada
    with open(enc_key_path, "wb") as f:
        f.write(encrypted_key)

    print("Model and AES key encrypted.")


if __name__ == "__main__":
    encrypt_model(
        "yolov8n.pt", 
        "model/model.pth.enc",
        "key/aes_key.enc",
        "key/public.pem"
    )