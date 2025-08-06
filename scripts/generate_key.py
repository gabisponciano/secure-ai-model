"""
Gerador de Par de Chaves RSA

Este módulo fornece funcionalidade para gerar pares de chaves RSA (pública e privada)
para uso em sistemas de criptografia assimétrica. As chaves são salvas em formato PEM
no diretório 'key/'.

Características:
- Geração de chaves RSA de 2048 bits
- Exportador público de 65537 (padrão recomendado)
- Chaves salvas em formato PEM padrão
- Criação automática do diretório de saída
- Chave privada sem proteção por senha (para automação)

Uso típico:
    $ python generate_keys.py
    
Arquivos gerados:
    - key/private.pem: Chave privada RSA
    - key/public.pem: Chave pública RSA

Segurança:
    ATENÇÃO: A chave privada é salva sem criptografia. Mantenha-a segura
    e considere adicionar proteção por senha em ambientes de produção.

Dependências:
    - cryptography: Biblioteca de criptografia moderna para Python

Autor: [Seu Nome]
Data: [Data]
Versão: 1.0
"""

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os


def generate_keys():
    """
    Gera um par de chaves RSA (pública e privada) e salva em arquivos PEM.
    
    Cria chaves RSA de 2048 bits usando expoente público 65537 (padrão F4).
    As chaves são salvas no diretório 'key/' em formato PEM:
    - Chave privada: formato TraditionalOpenSSL sem criptografia
    - Chave pública: formato SubjectPublicKeyInfo
    
    Raises:
        OSError: Se não conseguir criar o diretório ou escrever os arquivos
        PermissionError: Se não tiver permissões adequadas para escrita
    
    Returns:
        None
    
    Note:
        - Cria automaticamente o diretório 'key/' se não existir
        - Sobrescreve arquivos existentes sem aviso
        - A chave privada não tem proteção por senha para facilitar automação
        - Recomenda-se usar em ambiente seguro devido à chave desprotegida
    
    Example:
        >>> generate_keys()
        RSA key pair generated in key/
        
    Security Warning:
        A chave privada é salva sem criptografia. Em ambiente de produção,
        considere usar serialization.BestAvailableEncryption(password) para
        proteger a chave privada com senha.
    """
    # Gerar chave privada RSA
    private_key = rsa.generate_private_key(
        public_exponent=65537,  # Expoente F4 (padrão recomendado)
        key_size=2048          # Tamanho da chave em bits
    )
    
    # Extrair chave pública correspondente
    public_key = private_key.public_key()

    # Criar diretório de saída se não existir
    os.makedirs("key", exist_ok=True)

    # Salvar chave privada em formato PEM
    with open("key/private.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()  # Sem senha
        ))

    # Salvar chave pública em formato PEM
    with open("key/public.pem", "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    print("RSA key pair generated in key/")


if __name__ == "__main__":
    generate_keys()