import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

repo_root = Path(__file__).resolve().parents[1]
results_dir = repo_root / "results"

# --- 1) carregar arquivos de monitor do John ---
def load_monitor_csv(path):
    df = pd.read_csv(path)
    for col in ["cpu_percent", "mem_mb"]:
        if col not in df.columns:
            df[col] = 0
    return df

bcrypt_monitor = load_monitor_csv(results_dir / "john_bcrypt_monitor.csv")
sha_monitor = load_monitor_csv(results_dir / "john_sha256_monitor.csv")

# --- 2) calcular médias ---
def summarize_monitor(df, label):
    return {
        "algoritmo": label,
        "memória_MB_média": df["mem_mb"].mean()
    }

monitor_summary = [
    summarize_monitor(bcrypt_monitor, "bcrypt"),
    summarize_monitor(sha_monitor, "sha256")
]

monitor_summary_df = pd.DataFrame(monitor_summary)
monitor_summary_df.to_csv(results_dir / "monitor_summary.csv", index=False)

# --- 3) ler arquivos .show do John ---
def count_cracked(show_path, total_passwords):
    if not show_path.exists():
        return 0
    for enc in ("utf-8", "utf-16", "latin-1"):
        try:
            lines = show_path.read_text(encoding=enc).splitlines()
            break
        except Exception as e:
            print(f"❌ Falha ao ler {show_path.name} com {enc}: {e}")
    else:
        print(f"🚫 Não foi possível ler {show_path.name} com nenhuma codificação.")
        return 0
    return len(lines)

total_pw = 100
john_results = [
    {
        "algoritmo": "bcrypt",
        "percentual_quebrado": (count_cracked(results_dir / "john_bcrypt_show.txt", total_pw) / total_pw * 100)
    },
    {
        "algoritmo": "sha256",
        "percentual_quebrado": (count_cracked(results_dir / "john_sha256_show.txt", total_pw) / total_pw * 100)
    }
]

john_results_df = pd.DataFrame(john_results)
john_results_df.to_csv(results_dir / "john_results.csv", index=False)

# --- 4) gráfico combinado ---
fig, ax1 = plt.subplots(figsize=(7,5))

algorithms = ["bcrypt", "sha256"]
x = np.arange(len(algorithms))
width = 0.35

# Eixo esquerdo: percentual de quebra (%)
ax1.bar(x - width/2, john_results_df["percentual_quebrado"], width, label="Percentual quebrado (%)", color="orange")
ax1.set_ylabel("Percentual de Quebra (%)", color="orange")
ax1.tick_params(axis="y", labelcolor="orange")

# Eixo direito: memória média (MB)
ax2 = ax1.twinx()
ax2.bar(x + width/2, monitor_summary_df["memória_MB_média"], width, label="Memória média (MB)", color="green")
ax2.set_ylabel("Memória Média (MB)", color="green")
ax2.tick_params(axis="y", labelcolor="green")

# Configurações gerais
plt.title("Comparativo: Resistência e Uso de Memória por Algoritmo")
ax1.set_xticks(x)
ax1.set_xticklabels(algorithms)
fig.tight_layout()

plt.savefig(results_dir / "plot_cracked_vs_memoria.png")
plt.close()

print("✅ prepare_results.py finalizado. Gráfico combinado gerado em results/")