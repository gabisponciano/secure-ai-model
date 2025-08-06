"""
Sistema Avançado de Proteção de Código Python

Este módulo implementa múltiplas camadas de proteção contra engenharia reversa,
debugging, hooking e modificação de código. Projetado para proteger aplicações
Python sensíveis em ambientes onde a integridade e confidencialidade são críticas.

Camadas de Proteção Implementadas:
1. Anti-Debug: Detecta e bloqueia debuggers ativos
2. Anti-Hooking: Previne injeção de código e hooks maliciosos
3. Verificação de Integridade: Valida hash SHA-256 de arquivos críticos
4. Detecção de Processos: Identifica ferramentas de análise ativas
5. Validação de Ambiente: Verifica módulos e caminhos suspeitos

Técnicas de Detecção:
- Análise de stack trace para debuggers
- Verificação de threads de debugging
- Detecção de timing anômalo (anti-stepping)
- Validação de variáveis de ambiente
- Monitoramento de processos do sistema
- Análise de módulos carregados

Compatibilidade:
- Suporta detecção específica para Windows (IsDebuggerPresent)
- Funciona em ambientes Unix/Linux com limitações
- Compatível com Python 3.6+

Dependências:
    - psutil: Monitoramento de processos do sistema
    - ctypes: Interface com APIs do sistema (Windows)

Autor: [Seu Nome]
Data: [Data]
Versão: 2.0

Warning:
    Este código implementa técnicas anti-debug que podem ser consideradas
    hostis por alguns sistemas de segurança. Use apenas em aplicações
    legítimas onde a proteção é necessária.
"""

import sys
import os
import hashlib
import ctypes
import inspect
import time
import threading
import sysconfig
import psutil
import traceback

# ========== Proteções Anti-Debug ==========

def detect_and_block_debugger():
    """
    Detecta e bloqueia a execução de debuggers usando múltiplas técnicas.
    
    Implementa um sistema robusto de detecção anti-debug que verifica:
    - Tracer ativo via sys.gettrace()
    - Debuggers no stack trace (pdb, pydevd, etc.)
    - Módulos de debugging carregados
    - Threads de debugging ativas
    - API IsDebuggerPresent no Windows
    - Variáveis de ambiente de debug
    - Timing attacks para detectar stepping
    
    Raises:
        SystemExit: Termina a aplicação imediatamente se debugger detectado
    
    Returns:
        None: Retorna silenciosamente se nenhum debugger for detectado
    
    Detection Methods:
        1. sys.gettrace(): Detecta tracers Python ativos
        2. Stack Analysis: Procura por arquivos de debugging no call stack
        3. Module Detection: Verifica módulos de debug em sys.modules
        4. Thread Detection: Identifica threads de debugging (pydevd)
        5. Windows API: Usa IsDebuggerPresent() no Windows
        6. Environment Variables: Verifica PYTHONBREAKPOINT e PYDEV_DEBUG
        7. Timing Analysis: Detecta execução anormalmente lenta (stepping)
    
    Security Level: CRITICAL
        Primeira linha de defesa contra análise dinâmica
    
    Note:
        - Timing check pode gerar falsos positivos em sistemas lentos
        - Detecção Windows requer privilégios adequados
        - Algumas técnicas podem ser contornadas por debuggers avançados
    
    Example:
        >>> detect_and_block_debugger()  # Execução normal continua
        >>> # Com debugger ativo: "Debugger detectado via sys.gettrace(). Abortando."
    """
    # 1. Detectar tracer ativo via sys.gettrace()
    if sys.gettrace() is not None:
        print("Debugger detectado via sys.gettrace(). Abortando.")
        sys.exit(1)
    
    # 2. Verificar stack trace por debuggers conhecidos
    for frame_info in inspect.stack():
        filename = frame_info.filename.lower()
        if any(debugger_str in filename for debugger_str in ["pdb", "pydevd", "debug"]):
            print("[!] Debugger detectado via stack trace!")
            sys.exit(1)

    # 3. Verificar módulos de debugging carregados
    if "debugpy" in sys.modules:
        print("Debugger detectado via módulo debugpy carregado. Abortando.")
        sys.exit(1)

    # 4. Verificar threads de debugging ativas
    for thread in threading.enumerate():
        if thread.name.startswith("pydevd"):
            print("Debugger detectado via thread pydevd. Abortando.")
            sys.exit(1)

    # 5. Verificar API IsDebuggerPresent no Windows
    if os.name == "nt":
        try:
            if ctypes.windll.kernel32.IsDebuggerPresent() != 0:
                print("Debugger detectado via IsDebuggerPresent. Abortando.")
                sys.exit(1)
        except Exception:
            pass  # Falha silenciosa se API não disponível

    # 6. Verificar variáveis de ambiente de debug
    for var in ["PYTHONBREAKPOINT", "PYDEV_DEBUG"]:
        if os.getenv(var):
            print(f"Debugger detectado via variável {var}. Abortando.")
            sys.exit(1)

    # 7. Timing attack para detectar stepping/breakpoints
    t1 = time.perf_counter()
    for _ in range(10000):
        pass  # Loop simples para medir tempo
    t2 = time.perf_counter()
    if (t2 - t1) > 0.01:  # Threshold: 10ms para 10k iterações
        print("Debugger detectado via atraso suspeito. Abortando.")
        sys.exit(1)


# ========== Proteções contra Hooking e Injeção ==========

def detect_malicious_modules():
    """
    Detecta módulos maliciosos, hooks e ferramentas de análise.
    
    Implementa verificação abrangente contra:
    - Frameworks de hooking e injeção
    - Bibliotecas de análise dinâmica
    - Debuggers e disassemblers
    - Módulos de instrumentação
    - Processos de análise ativos
    - Caminhos de módulos suspeitos
    
    Security Checks:
        1. Module Scanning: Verifica sys.modules por bibliotecas suspeitas
        2. Path Validation: Analisa origem de módulos carregados
        3. Process Monitoring: Detecta ferramentas de análise ativas
    
    Raises:
        SystemExit: Termina aplicação se ameaça detectada
    
    Returns:
        None: Retorna silenciosamente se ambiente for seguro
    
    Detected Threats:
        - Frida framework e variantes
        - Python debuggers (pdb, pydevd, etc.)
        - Hooking libraries (ctypeshook, pyhook)
        - Memory analysis tools (pymem, volatility)
        - Disassemblers (capstone, keystone)
        - Reverse engineering tools (IDA, x64dbg, etc.)
        - Network analyzers (Wireshark)
    
    Path Security:
        Valida que módulos são carregados apenas de:
        - Biblioteca padrão Python
        - Site-packages oficiais
        - Diretórios protegidos da aplicação
    
    Security Level: HIGH
        Segunda camada de defesa contra análise estática/dinâmica
    
    Note:
        - Pode gerar falsos positivos com ferramentas legítimas
        - Requer privilégios para acessar informações de processo
        - Lista de ameaças pode necessitar atualização periódica
    """
    # Módulos considerados suspeitos/maliciosos
    suspicious_modules = [
        "frida", "pydbg", "ctypeshook", "pyhook", "pydevd", "winappdbg",
        "pyinjector", "injector", "pymem", "ptrace", "volatility", "hexdump",
        "pyxhook", "capstone", "keystone", "unicorn", "tracer", "hooker",
        "ipdb", "rpdb", "remote_pdb", "pydebugger", "pytrace", "pyspoofer",
        "python_hooker", "hunter", "snoop", "manhole", "xhook", "pyrebox",
        "objdump"
    ]

    # Processos considerados maliciosos
    suspicious_processes = [
        "frida-server", "frida-trace", "ollydbg", "ida64", "ida32", "x64dbg", "x32dbg",
        "wireshark", "dnspy", "cheatengine", "gdb", "radare2", "immunitydebugger"
    ]

    # 1. Verifica se módulos suspeitos estão carregados
    for mod in sys.modules:
        mod_lower = mod.lower()
        if any(s in mod_lower for s in suspicious_modules):
            print(f"[!] Módulo suspeito detectado: {mod}. Abortando.")
            sys.exit(1)

    # 2. Verifica caminhos suspeitos para módulos não-stdlib/site-packages
    allowed_paths = [
        sysconfig.get_paths()["stdlib"].lower(),  # Biblioteca padrão
        os.path.join(sys.base_prefix.lower(), "dlls"),  # DLLs Python
        os.path.join(sys.base_prefix.lower(), "libs"),  # Bibliotecas Python
        os.path.join(sys.base_prefix.lower(), "lib", "site-packages"),  # Site-packages
    ]

    for mod_name, mod in sys.modules.items():
        path = getattr(mod, "__file__", None)
        if path is None:
            continue  # Módulos built-in não têm __file__
        
        path = os.path.abspath(path).lower()

        # Exceções para módulos legítimos
        if mod_name == "__main__" or "pyarmor_runtime" in mod_name:
            continue
        if "dist_protected" in path:  # Aplicação protegida
            continue
        if any(path.startswith(p) for p in allowed_paths):
            continue

        print(f"[!] Módulo {mod_name} carregado de caminho suspeito: {path}")
        sys.exit(1)

    # 3. Verifica se há processos maliciosos ativos no sistema
    for proc in psutil.process_iter(["name", "exe", "cmdline"]):
        try:
            name = (proc.info["name"] or "").lower()
            cmd = " ".join(proc.info["cmdline"] or []).lower()
            
            if any(s in name or s in cmd for s in suspicious_processes):
                print(f"[!] Processo suspeito detectado: {name or cmd}. Abortando.")
                sys.exit(1)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue  # Processo inacessível ou já terminado


# ========== Verificação de Integridade ==========

def check_integrity(file_path: str, expected_hash: str):
    """
    Verifica integridade de arquivo usando hash SHA-256.
    
    Implementa verificação criptográfica de integridade para detectar:
    - Modificação de arquivos críticos
    - Corrupção de dados
    - Tentativas de patch/hook
    - Substituição de arquivos
    
    Args:
        file_path (str): Caminho para o arquivo a ser verificado
        expected_hash (str): Hash SHA-256 esperado em hexadecimal (64 caracteres)
    
    Raises:
        SystemExit: Termina aplicação se integridade comprometida
        FileNotFoundError: Se arquivo não existir
        PermissionError: Se não tiver permissão de leitura
    
    Returns:
        None: Retorna silenciosamente se integridade OK
    
    Security Features:
        - Usa SHA-256 (resistente a colisões)
        - Lê arquivo completo para evitar ataques de timing
        - Comparação segura de hash
        - Tratamento de erros robusto
    
    Security Level: MEDIUM
        Proteção contra modificação de arquivos críticos
    
    Example:
        >>> expected = "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"
        >>> check_integrity("model.pth", expected)  # OK se hash correto
        >>> check_integrity("modified.pth", expected)  # "Integridade comprometida. Abortando."
    
    Note:
        - Hash deve ser calculado do arquivo original não modificado
        - Arquivo é lido integralmente na memória
        - Verificação deve ser feita antes do uso do arquivo
        - Hashes devem ser armazenados de forma segura
    """
    try:
        # Ler arquivo completo e calcular hash SHA-256
        with open(file_path, "rb") as f:
            file_content = f.read()
            file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Comparação segura de hash
        if file_hash != expected_hash:
            print("Integridade comprometida. Abortando.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Falha ao verificar integridade: {e}")
        sys.exit(1)