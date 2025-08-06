
# 🔐 Secure AI Model – Proteção de Modelos de IA com Criptografia e Ofuscação

Este projeto implementa um sistema completo de proteção de modelos de IA, combinando **criptografia híbrida (AES-256 + RSA-2048)**, **verificação de integridade** e **ofuscação de código** para evitar engenharia reversa, extração ou uso indevido do modelo.

---

## 📁 Estrutura do Projeto

```
secure-ai-model/
│
├── key/                    # Armazena as chaves RSA
│   ├── private.pem         # Chave privada (gerada)
│   └── public.pem          # Chave pública (gerada)
│
├── model/                  # Armazena os arquivos criptografados
│   ├── model.pth.enc       # Modelo criptografado (AES)
│   └── aes_key.enc         # Chave AES criptografada (RSA)
│
├── scripts/                # Scripts de proteção
│   ├── generate_key.py     # Gera par de chaves RSA
│   ├── encrypt_model.py    # Criptografa o modelo
│   ├── decrypt_model.py    # Descriptografa durante execução
│   └── code_protection.py  # (Opcional) Ofusca código com PyArmor
│
├── main.py                 # Executa benchmark com modelo protegido
├── build.bat               # Pipeline de build e proteção (Windows)
├── requirements.txt        # Dependências do projeto
└── meumodelo.pt            # Modelo original (antes da criptografia)
```

---

## ⚙️ Requisitos

- Python 3.10+
- Sistema Windows (recomendado para `.bat`)
- Pip + venv (opcional)
- Framework usado no modelo (ex: `torch`, `sklearn`, etc.)

---

## 📦 Instalação

Clone o repositório e instale as dependências:

```bash
git clone hhttps://github.com/gabisponciano/secure-ai-model.git
cd secure-ai-model
pip install -r requirements.txt
```

---

## 🚀 Como usar

### 1. 📁 Treine ou obtenha seu modelo

Coloque seu modelo treinado no diretório raiz.  
Exemplo com PyTorch:

```python
torch.save(model.state_dict(), "meumodelo.pt")
```

---

A proteção suporta diferentes modelos como: TensorFlow (.pb), ONNX, Scikit-learn (.pkl) e entre outros.

### 2. 🔐 Gere as chaves RSA

```bash
python scripts/generate_key.py
```

---

### 3. 🔒 Criptografe seu modelo

```bash
python scripts/encrypt_model.py
```

---

### 4. 🧪 Rode o sistema protegido

```bash
python main.py
```

---

### 5. 🤖 Automatize tudo com `build.bat`

```bash
build.bat
```

---

## 🔒 Sobre a Criptografia

Este projeto usa criptografia híbrida:

- **AES-256-GCM**: Criptografa o modelo com autenticação integrada
- **RSA-2048 OAEP**: Protege a chave AES
- **Execução segura**: Descriptografado somente na RAM, nunca no disco

---

## 🛡️ Segurança em tempo de execução (opcional)

- Anti-debug (sys.gettrace, variáveis de ambiente)
- Detecção de módulos maliciosos (`frida`, `pydbg`)
- Verificação de integridade por hash SHA-256
- Ofuscação com PyArmor (requer licença para produção)

---

## ✅ Suporte a outros modelos

Você pode proteger **qualquer modelo de IA** desde que ele seja salvo como um arquivo (como `.pt`, `.pkl`, `.onnx`, etc.) e possa ser carregado a partir de bytes.

---

## 🧠 Autores / Créditos

Baseado no projeto original:  
🔗 https://github.com/wildneifrank/secure-ai-model

---

## 📜 Licença

Este projeto está sob a licença MIT.

