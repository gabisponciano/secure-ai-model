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

IS_PRODUCTION = "dist_protected" in os.path.abspath(os.path.dirname(__file__))

if IS_PRODUCTION:
    from hash_registry_obfuscated import (
    DIST_PROTECTED_MAIN_PY,
    DIST_PROTECTED_SCRIPTS_DECRYPT_MODEL_PY,
    MODEL_MODEL_PTH_ENC
    )
    check_integrity("main.py", DIST_PROTECTED_MAIN_PY)
    check_integrity("scripts/decrypt_model.py", DIST_PROTECTED_SCRIPTS_DECRYPT_MODEL_PY)
    check_integrity("model/model.pth.enc", MODEL_MODEL_PTH_ENC)

    detect_and_block_debugger()
    detect_malicious_modules()
else:
    print("Modo desenvolvimento - skipando checagem de integridade e proteção.")

def run_once():
    metrics = {}
    start_total = time.time()

    start_decrypt = time.time()
    aes_key = decrypt_aes_key(
        resource_path("key/aes_key.enc"),
        resource_path("key/private.pem")
    )
    model_bytes = decrypt_model(resource_path("model/model.pth.enc"), aes_key)
    metrics["decryption_time"] = time.time() - start_decrypt

    start_load = time.time()
    model = load_model_from_bytes(model_bytes)
    model.float()
    metrics["load_time"] = time.time() - start_load

    dummy_input = torch.randn(1, 3, 640, 640)

    start_infer = time.time()
    with torch.no_grad():
        model(dummy_input)
    metrics["inference_time"] = time.time() - start_infer

    metrics["total_time"] = time.time() - start_total

    del model
    del model_bytes
    del aes_key
    del dummy_input
    torch.cuda.empty_cache()

    return metrics

def main():
    runs = 2000
    results = []

    for i in range(runs):
        percent = (i + 1) / runs * 100
        print(f"Progresso: {percent:.1f}% ({i+1}/{runs})", end='\r')
        metrics = run_once()
        results.append(metrics)

    print()

    df = pd.DataFrame(results)
    output_dir = resource_path("results")
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(os.path.join(output_dir, "benchmark.csv"), index=False)
    print("Benchmark concluído e salvo em 'results/benchmark.csv'.")

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
