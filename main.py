"""
Módulo de Benchmarking de Modelo ML Criptografado

Este módulo realiza benchmarking de performance de um modelo de Machine Learning
que está armazenado de forma criptografada. Executa múltiplas iterações medindo
tempos de descriptografia, carregamento e inferência.

Características:
- Suporte para modo de produção com verificações de integridade
- Proteção contra debugging e módulos maliciosos
- Descriptografia segura usando chaves AES e RSA
- Geração de métricas detalhadas de performance
- Exportação de resultados em formato CSV
"""

import os
import time
import torch
import pandas as pd
import matplotlib.pyplot as plt
from scripts.decrypt_model import resource_path, decrypt_aes_key, decrypt_model, load_model_from_bytes
from scripts.code_protection import  (
    detect_and_block_debugger,
    detect_malicious_modules,
    check_integrity
)

# Determina se está executando em modo de produção baseado no caminho
IS_PRODUCTION = "dist_protected" in os.path.abspath(os.path.dirname(__file__))

if IS_PRODUCTION:
    from hash_registry_obfuscated import (
    DIST_PROTECTED_MAIN_PY,
    DIST_PROTECTED_SCRIPTS_DECRYPT_MODEL_PY,
    MODEL_MODEL_PTH_ENC
    )
    # Verificações de segurança em modo de produção
    check_integrity("main.py", DIST_PROTECTED_MAIN_PY)
    check_integrity("scripts/decrypt_model.py", DIST_PROTECTED_SCRIPTS_DECRYPT_MODEL_PY)
    check_integrity("model/model.pth.enc", MODEL_MODEL_PTH_ENC)

    detect_and_block_debugger()
    detect_malicious_modules()
else:
    print("Modo desenvolvimento - skipando checagem de integridade e proteção.")


def run_once():
    """
    Executa uma única iteração completa do benchmark.
    
    Realiza o processo completo de descriptografia, carregamento e inferência
    do modelo, medindo o tempo de cada etapa individualmente.
    
    Returns:
        dict: Dicionário contendo as métricas de tempo coletadas:
            - decryption_time (float): Tempo gasto na descriptografia em segundos
            - load_time (float): Tempo gasto no carregamento do modelo em segundos
            - inference_time (float): Tempo gasto na inferência em segundos
            - total_time (float): Tempo total da execução em segundos
    
    Note:
        - Utiliza entrada dummy de tamanho (1, 3, 640, 640) para inferência
        - Limpa recursos da memória após execução para evitar vazamentos
        - Esvazia cache CUDA se disponível
    """
    metrics = {}
    start_total = time.time()

    # Medir tempo de descriptografia
    start_decrypt = time.time()
    aes_key = decrypt_aes_key(
        resource_path("key/aes_key.enc"),
        resource_path("key/private.pem")
    )
    model_bytes = decrypt_model(resource_path("model/model.pth.enc"), aes_key)
    metrics["decryption_time"] = time.time() - start_decrypt

    # Medir tempo de carregamento
    start_load = time.time()
    model = load_model_from_bytes(model_bytes)
    model.float()
    metrics["load_time"] = time.time() - start_load

    # Preparar entrada dummy para inferência
    dummy_input = torch.randn(1, 3, 640, 640)

    # Medir tempo de inferência
    start_infer = time.time()
    with torch.no_grad():
        model(dummy_input)
    metrics["inference_time"] = time.time() - start_infer

    metrics["total_time"] = time.time() - start_total

    # Limpeza de memória
    del model
    del model_bytes
    del aes_key
    del dummy_input
    torch.cuda.empty_cache()

    return metrics


def main():
    """
    Função principal que executa o benchmark completo.
    
    Executa múltiplas iterações do benchmark (2000 por padrão), coletando
    métricas de performance e gerando relatórios estatísticos.
    
    Funcionalidades:
    - Executa 2000 iterações do benchmark
    - Mostra progresso em tempo real
    - Calcula estatísticas resumidas (médias)
    - Salva resultados detalhados em CSV
    - Exibe relatório final no console
    
    Outputs:
        - Arquivo CSV: results/benchmark.csv com todas as métricas
        - Relatório no console com médias de tempo
    
    Note:
        Cria automaticamente o diretório 'results' se não existir.
    """
    runs = 2000
    results = []

    print(f"Iniciando benchmark com {runs} execuções...")
    
    # Loop principal de execução
    for i in range(runs):
        percent = (i + 1) / runs * 100
        print(f"Progresso: {percent:.1f}% ({i+1}/{runs})", end='\r')
        metrics = run_once()
        results.append(metrics)

    print()

    # Processamento e salvamento dos resultados
    df = pd.DataFrame(results)
    output_dir = resource_path("results")
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(os.path.join(output_dir, "benchmark.csv"), index=False)
    print("Benchmark concluído e salvo em 'results/benchmark.csv'.")

    # Cálculo e exibição de estatísticas
    mean_decrypt = df["decryption_time"].mean()
    mean_load = df["load_time"].mean()
    mean_infer = df["inference_time"].mean()
    mean_total = df["total_time"].mean()

    print(f"\nMédias após {runs} execuções:")
    print(f"  Decryption: {mean_decrypt:.4f} s")
    print(f"  Load:       {mean_load:.4f} s")
    print(f"  Inference:  {mean_infer:.4f} s")
    print(f"  Total:      {mean_total:.4f} s\n")


if __name__ == "__main__":
    main()