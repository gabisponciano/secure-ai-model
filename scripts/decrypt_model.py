"""
Sistema de Descriptografia e Carregamento de Modelos YOLO Criptografados

Este módulo implementa a descriptografia e carregamento de modelos YOLO que foram
protegidos usando criptografia híbrida AES-GCM + RSA-OAEP. Projetado para trabalhar
com modelos da biblioteca Ultralytics em ambientes protegidos ou distribuíveis.

Funcionalidades Principais:
- Descriptografia de chaves AES protegidas por RSA
- Descriptografia de modelos usando AES-GCM
- Carregamento flexível de modelos YOLO em diferentes formatos
- Suporte a executáveis PyInstaller (sys._MEIPASS)
- Configuração automática de globals seguros para torch.load()

Fluxo de Descriptografia:
1. Descriptografa chave AES usando chave privada RSA
2. Usa chave AES para descriptografar modelo (AES-GCM)
3. Carrega modelo PyTorch a partir dos bytes descriptografados
4. Configura modelo YOLO DetectionModel conforme necessário

Compatibilidade:
- Modelos YOLO da Ultralytics (YOLOv8, etc.)
- Arquivos .pt e .pth do PyTorch
- Executáveis empacotados com PyInstaller
- Diferentes formatos de serialização de modelo

Dependências:
    - cryptography: Operações criptográficas
    - torch: Framework de deep learning
    - ultralytics: Biblioteca YOLO
    - io: Operações de buffer em memória

Autor: [Seu Nome]
Data: [Data]
Versão: 1.0
"""

import io
import os
import sys
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import torch
from ultralytics.nn.tasks import DetectionModel
import torch.serialization

# Configurar globals seguros para carregamento de modelos YOLO
torch.serialization.add_safe_globals([DetectionModel])


def resource_path(relative_path, for_output=False):
    """
    Resolve caminhos de recursos para diferentes ambientes de execução.
    
    Função utilitária que trata caminhos de arquivos tanto em desenvolvimento
    quanto em executáveis empacotados (PyInstaller). Essencial para localizar
    recursos em aplicações distribuíveis.
    
    Args:
        relative_path (str): Caminho relativo para o recurso desejado
        for_output (bool, optional): Se True, retorna caminho absoluto simples.
                                   Se False, considera ambiente PyInstaller. Default: False
    
    Returns:
        str: Caminho absoluto para o recurso
    
    Behavior:
        - for_output=True: Usado para arquivos de saída, retorna path absoluto direto
        - for_output=False: Detecta ambiente PyInstaller via sys._MEIPASS
        - Em executável PyInstaller: Usa sys._MEIPASS como base
        - Em desenvolvimento: Usa diretório atual como base
    
    PyInstaller Support:
        Quando empacotado com PyInstaller, os recursos são extraídos para um
        diretório temporário referenciado por sys._MEIPASS. Esta função
        automaticamente detecta e usa o caminho correto.
    
    Example:
        >>> # Em desenvolvimento
        >>> resource_path("model/model.pth.enc")
        '/projeto/model/model.pth.enc'
        
        >>> # Em executável PyInstaller
        >>> resource_path("model/model.pth.enc")  
        '/tmp/_MEI123456/model/model.pth.enc'
        
        >>> # Para arquivos de saída
        >>> resource_path("results/output.csv", for_output=True)
        '/projeto/results/output.csv'
    
    Note:
        - Essencial para aplicações que precisam funcionar empacotadas
        - for_output=True deve ser usado apenas para arquivos que serão criados
        - Caminho base é determinado automaticamente pelo ambiente
    """
    if for_output:
        return os.path.abspath(relative_path)
    
    try:
        # Tentar obter caminho base do PyInstaller
        base_path = sys._MEIPASS
    except Exception:
        # Fallback para diretório atual (desenvolvimento)
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


def decrypt_aes_key(enc_key_path, private_key_path):
    """
    Descriptografa chave AES usando chave privada RSA com OAEP padding.
    
    Implementa a descriptografia da chave AES que foi protegida usando
    RSA-OAEP. Esta é a primeira etapa do processo de descriptografia híbrida,
    recuperando a chave simétrica necessária para descriptografar o modelo.
    
    Args:
        enc_key_path (str): Caminho para o arquivo da chave AES criptografada
        private_key_path (str): Caminho para a chave privada RSA em formato PEM
    
    Returns:
        bytes: Chave AES descriptografada (128 bits / 16 bytes)
    
    Raises:
        FileNotFoundError: Se qualquer arquivo não existir
        ValueError: Se chave privada for inválida ou corrompida
        cryptography.exceptions.InvalidSignature: Se descriptografia falhar
        PermissionError: Se não tiver permissões para ler arquivos
    
    Cryptographic Details:
        - Usa RSA-OAEP (Optimal Asymmetric Encryption Padding)
        - MGF1 com SHA-256 como função de máscara
        - SHA-256 como algoritmo de hash principal
        - Sem label adicional (padrão seguro)
    
    Security Features:
        - Padding OAEP previne ataques de texto cifrado adaptativo
        - SHA-256 oferece resistência criptográfica adequada
        - Chave privada carregada sem senha (para automação)
    
    Example:
        >>> aes_key = decrypt_aes_key(
        ...     "key/aes_key.enc", 
        ...     "key/private.pem"
        ... )
        >>> len(aes_key)
        16  # 128 bits
    
    Note:
        - Chave privada deve corresponder à pública usada na criptografia
        - Processo é computacionalmente mais lento que AES (normal para RSA)
        - Chave AES resultante será usada para descriptografar o modelo
    """
    # Ler chave AES criptografada
    with open(enc_key_path, "rb") as f:
        enc_key = f.read()
    
    # Carregar chave privada RSA
    with open(private_key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)
    
    # Descriptografar chave AES usando RSA-OAEP
    return private_key.decrypt(
        enc_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),  # MGF1 com SHA-256
            algorithm=hashes.SHA256(),                     # Hash principal
            label=None                                     # Sem label adicional
        )
    )


def decrypt_model(model_path, aes_key):
    """
    Descriptografa modelo usando AES-GCM com chave fornecida.
    
    Implementa a descriptografia do modelo PyTorch usando AES-GCM.
    Extrai o nonce do arquivo e usa a chave AES previamente descriptografada
    para recuperar os dados originais do modelo.
    
    Args:
        model_path (str): Caminho para o arquivo do modelo criptografado
        aes_key (bytes): Chave AES descriptografada (16 bytes para AES-128)
    
    Returns:
        bytes: Dados do modelo descriptografados (formato PyTorch original)
    
    Raises:
        FileNotFoundError: Se arquivo do modelo não existir
        cryptography.exceptions.InvalidTag: Se autenticação AES-GCM falhar
        ValueError: Se chave AES for inválida ou dados corrompidos
        PermissionError: Se não tiver permissão para ler arquivo
    
    File Format Expected:
        O arquivo deve conter: [12 bytes nonce] + [dados AES-GCM criptografados]
        - Nonce: 12 bytes iniciais (padrão AES-GCM)
        - Ciphertext: Restante do arquivo (dados + tag de autenticação)
    
    Cryptographic Details:
        - Usa AES-GCM (Galois/Counter Mode)
        - Nonce de 12 bytes (96 bits) - padrão recomendado
        - Autenticação integrada (detecta modificações)
        - Sem dados adicionais autenticados (AAD=None)
    
    Security Features:
        - Autenticação integrada previne modificações maliciosas
        - Nonce único garante segurança semântica
        - AES-128 oferece segurança adequada com boa performance
    
    Example:
        >>> aes_key = decrypt_aes_key("key/aes_key.enc", "key/private.pem")
        >>> model_data = decrypt_model("model/model.pth.enc", aes_key)
        >>> type(model_data)
        <class 'bytes'>
    
    Note:
        - Arquivo deve ter sido criptografado com mesmo formato (nonce + dados)
        - Falha na autenticação indica arquivo corrompido ou chave incorreta
        - Dados retornados são bytes brutos do arquivo .pth original
    """
    # Ler arquivo completo do modelo criptografado
    with open(model_path, "rb") as f:
        data = f.read()
    
    # Separar nonce (12 bytes) e dados criptografados
    nonce, ciphertext = data[:12], data[12:]
    
    # Inicializar AES-GCM com chave descriptografada
    aesgcm = AESGCM(aes_key)
    
    # Descriptografar e autenticar dados
    return aesgcm.decrypt(nonce, ciphertext, None)


def load_model_from_bytes(model_bytes: bytes):
    """
    Carrega modelo YOLO a partir de bytes descriptografados.
    
    Implementa carregamento flexível de modelos YOLO que podem estar em
    diferentes formatos de serialização. Trata automaticamente modelos
    salvos como objetos DetectionModel ou como state_dict.
    
    Args:
        model_bytes (bytes): Dados do modelo PyTorch em formato bytes
    
    Returns:
        DetectionModel: Modelo YOLO carregado e configurado para inferência
    
    Raises:
        TypeError: Se formato do modelo não for suportado
        torch.serialization.pickle.UnpicklingError: Se dados estiverem corrompidos
        FileNotFoundError: Se arquivo de configuração YOLO não existir
        RuntimeError: Se houver erro no carregamento do PyTorch
    
    Supported Formats:
        1. Dict com chave "model" contendo DetectionModel
        2. Dict com chave "model" contendo state_dict
        3. Dict contendo state_dict diretamente
        4. DetectionModel serializado diretamente
    
    Loading Strategy:
        - Carrega dados em CPU para compatibilidade máxima
        - Detecta formato automaticamente
        - Cria novo modelo com configuração padrão se necessário
        - Configura modelo para modo de inferência (eval)
    
    YOLO Configuration:
        - Usa 'yolov8n.yaml' como configuração padrão para novos modelos
        - Compatível com modelos YOLOv8 da Ultralytics
        - Suporte a DetectionModel (detecção de objetos)
    
    Example:
        >>> model_data = decrypt_model("model.pth.enc", aes_key)
        >>> model = load_model_from_bytes(model_data)
        >>> model.eval()  # Já configurado automaticamente
        >>> type(model)
        <class 'ultralytics.nn.tasks.DetectionModel'>
    
    Note:
        - Modelo é automaticamente configurado para modo eval()
        - Carregamento em CPU permite uso em diferentes dispositivos
        - Requer configuração YOLO (yolov8n.yaml) acessível
        - add_safe_globals([DetectionModel]) deve ser chamado antes do uso
    """
    # Criar buffer em memória a partir dos bytes
    buffer = io.BytesIO(model_bytes)
    
    # Carregar dados do PyTorch (CPU para compatibilidade)
    loaded = torch.load(buffer, map_location=torch.device("cpu"))

    # Processar diferentes formatos de modelo
    if isinstance(loaded, dict):
        if "model" in loaded:
            model_data = loaded["model"]
            
            if isinstance(model_data, DetectionModel):
                # Formato: {"model": DetectionModel_object}
                model = model_data
            elif isinstance(model_data, dict):
                # Formato: {"model": state_dict}
                model = DetectionModel('yolov8n.yaml')
                model.load_state_dict(model_data)
            else:
                raise TypeError(f"Unsupported model data type: {type(model_data)}")
        else:
            # Formato: state_dict direto
            model = DetectionModel('yolov8n.yaml')
            model.load_state_dict(loaded)
            
    elif isinstance(loaded, DetectionModel):
        # Formato: DetectionModel direto
        model = loaded
    else:
        raise TypeError(f"Unexpected loaded type: {type(loaded)}")

    # Configurar modelo para inferência
    model.eval()
    return model