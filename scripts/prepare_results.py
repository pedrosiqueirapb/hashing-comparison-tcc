import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# --- Configuração de diretórios ---
repo_root = Path(__file__).resolve().parents[1]
results_dir = repo_root / "results"

# --- 1) Carregar arquivos de monitor do John ---
def load_monitor_csv(path):
    if not path.exists():
        return pd.DataFrame(columns=["timestamp", "cpu_percent", "mem_mb"])
    df = pd.read_csv(path)
    for col in ["cpu_percent", "mem_mb"]:
        if col not in df.columns:
            df[col] = 0
    return df

bcrypt_monitor = load_monitor_csv(results_dir / "john_bcrypt_monitor.csv")
sha_monitor = load_monitor_csv(results_dir / "john_sha256_monitor.csv")

# --- 2) Calcular médias de uso de memória ---
def summarize_monitor(df, label):
    # em caso de df vazio, média será 0
    mem_mean = df["mem_mb"].mean() if not df.empty else 0.0
    return {
        "algoritmo": label,
        "memoria_media_MB": mem_mean
    }

monitor_summary = [
    summarize_monitor(bcrypt_monitor, "bcrypt"),
    summarize_monitor(sha_monitor, "sha256")
]
monitor_summary_df = pd.DataFrame(monitor_summary)
monitor_summary_df.to_csv(results_dir / "monitor_summary.csv", index=False)

# --- 3) Ler arquivos .show do John (para percentual de quebra) ---
def count_cracked(show_path, total_passwords=100):
    if not show_path.exists():
        return 0
    for enc in ("utf-8", "utf-16", "latin-1"):
        try:
            lines = show_path.read_text(encoding=enc).splitlines()
            break
        except Exception:
            continue
    else:
        return 0
    # cada linha do --show normalmente representa um hash quebrado; contamos linhas
    return len(lines)

john_results = [
    {
        "algoritmo": "bcrypt",
        "percentual_quebrado": (count_cracked(results_dir / "john_bcrypt_show.txt", 100) / 100 * 100)
    },
    {
        "algoritmo": "sha256",
        "percentual_quebrado": (count_cracked(results_dir / "john_sha256_show.txt", 100) / 100 * 100)
    }
]
john_results_df = pd.DataFrame(john_results)
john_results_df.to_csv(results_dir / "john_results.csv", index=False)

# --- 4) Carregar medições do servidor ---
server_csv = results_dir / "server_benchmarks.csv"
if server_csv.exists():
    server_df = pd.read_csv(server_csv)
    # salva copy raw para referência
    server_df.to_csv(results_dir / "summary_table.csv", index=False)
else:
    print("⚠️  server_benchmarks.csv não encontrado. Verifique se rodou benchmark_server.py")
    server_df = pd.DataFrame()

# --- 5) Gráfico combinado (Percentual quebrado x Memória média) ---
algorithms = ["bcrypt", "sha256"]
x = np.arange(len(algorithms))
width = 0.35

fig, ax1 = plt.subplots(figsize=(7, 5))
bar1 = ax1.bar(x - width/2, john_results_df["percentual_quebrado"], width,
               label="Percentual de Quebra (%)", color="#007acc")
bar2 = ax1.bar(x + width/2, monitor_summary_df["memoria_media_MB"], width,
               label="Memória Média (MB)", color="#ff7f0e")

ax1.set_xticks(x)
ax1.set_xticklabels(algorithms)
ax1.set_ylabel("Percentual de Quebra (%)  /  Memória Média (MB)")
ax1.set_title("Comparativo: Resistência e Uso de Memória por Algoritmo")
ax1.legend(loc="upper right")
ax1.grid(axis="y", linestyle="--", alpha=0.5)

for bar in list(bar1) + list(bar2):
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2, yval + (0.01 * max(1, yval)), f"{yval:.1f}",
             ha='center', va='bottom', fontsize=8)

fig.tight_layout()
plt.savefig(results_dir / "plot_cracked_vs_memoria.png")
plt.close()

# --- 6) Gráfico de tempo médio de hash (do servidor) ---
if not server_df.empty:
    if "mean_s" not in server_df.columns:
        print("⚠️ Coluna 'mean_s' não encontrada em server_benchmarks.csv — pulando plot_time_per_hash.")
    else:
        # agregação: média do mean_s por algoritmo (se houver várias linhas por senha)
        agg = server_df.groupby("algorithm", as_index=False)["mean_s"].mean()
        # assegura ordem consistente (sha256, bcrypt, argon2) quando possível
        preferred_order = ["sha256", "bcrypt", "argon2"]
        agg["order"] = agg["algorithm"].apply(lambda a: preferred_order.index(a) if a in preferred_order else 99)
        agg = agg.sort_values("order").drop(columns=["order"])

        plt.figure(figsize=(7,5))
        ax = plt.gca()
        ax.bar(agg["algorithm"], agg["mean_s"], color="#2ca02c")
        ax.set_yscale("log")  # <-- escala logarítmica para melhorar leitura
        ax.set_ylabel("Tempo Médio por Hash (s) — escala log")
        ax.set_title("Desempenho do Servidor: Tempo de Hash por Algoritmo (escala log)")
        ax.grid(axis="y", linestyle="--", alpha=0.5, which="both")
        
        for i, v in enumerate(agg["mean_s"]):
            if v > 0:
                label = f"{v:.3e}"
            else:
                label = "0"
            ax.text(i, v * 1.2, label, ha="center", va="bottom", fontsize=8)
        plt.tight_layout()
        plt.savefig(results_dir / "plot_time_per_hash.png")
        plt.close()
else:
    print("⚠️ server_df vazio — pulando plot_time_per_hash.")

print("✅ prepare_results.py finalizado. Todos os arquivos CSV e gráficos foram gerados em 'results/'")