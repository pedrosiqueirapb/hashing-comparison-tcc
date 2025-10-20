import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

repo_root = Path(__file__).resolve().parents[1]
results_dir = repo_root / "results"

# --- 1) carregar arquivos de monitor do John ---
def load_monitor_csv(path):
    df = pd.read_csv(path)
    # garante colunas corretas
    for col in ["cpu_percent", "mem_mb"]:
        if col not in df.columns:
            df[col] = 0
    return df

bcrypt_monitor = load_monitor_csv(results_dir / "john_bcrypt_monitor.csv")
sha_monitor = load_monitor_csv(results_dir / "john_sha256_monitor.csv")

# --- 2) calcular médias de monitor ---
def summarize_monitor(df, label):
    return {
        "algorithm": label,
        "avg_cpu_percent": df["cpu_percent"].mean(),
        "avg_mem_mb": df["mem_mb"].mean(),
        "max_mem_mb": df["mem_mb"].max()
    }

monitor_summary = [
    summarize_monitor(bcrypt_monitor, "bcrypt"),
    summarize_monitor(sha_monitor, "sha256")
]

monitor_summary_df = pd.DataFrame(monitor_summary)
monitor_summary_df.to_csv(results_dir / "monitor_summary.csv", index=False)

# --- 3) ler arquivos .show do John ---
def count_cracked(show_path, total_passwords=9):
    if not show_path.exists():
        return 0

    # tenta ler com várias codificações possíveis (UTF-8, UTF-16, Latin-1)
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

john_results = [
    {
        "algorithm": "bcrypt",
        "cracked": count_cracked(results_dir / "john_bcrypt_show.txt"),
        "total": 9
    },
    {
        "algorithm": "sha256",
        "cracked": count_cracked(results_dir / "john_sha256_show.txt"),
        "total": 9
    }
]

john_results_df = pd.DataFrame(john_results)
john_results_df["percent_cracked"] = (john_results_df["cracked"] / john_results_df["total"] * 100).round(2)
john_results_df.to_csv(results_dir / "john_results.csv", index=False)

# --- 4) carregar server benchmarks (gerados por benchmark_server.py) ---
server_csv = results_dir / "server_benchmarks.csv"
if server_csv.exists():
    server_df = pd.read_csv(server_csv)
    server_df.to_csv(results_dir / "summary_table.csv", index=False)
else:
    print("⚠️ server_benchmarks.csv não encontrado. Verifique se rodou benchmark_server.py")

# --- 5) Plot gráficos ---
plt.figure(figsize=(6,4))
plt.bar(john_results_df["algorithm"], john_results_df["percent_cracked"], color="orange")
plt.ylabel("Percent Cracked (%)")
plt.title("Resistência a Ataque")
plt.savefig(results_dir / "plot_percent_cracked.png")
plt.close()

plt.figure(figsize=(6,4))
plt.bar(monitor_summary_df["algorithm"], monitor_summary_df["avg_mem_mb"], color="green")
plt.ylabel("Média Memória (MB)")
plt.title("Uso de Memória durante Ataque")
plt.savefig(results_dir / "plot_mem_mb.png")
plt.close()

plt.figure(figsize=(6,4))
if server_csv.exists():
    plt.bar(server_df["algorithm"], server_df["mean_s"], color="blue")
    plt.ylabel("Tempo Médio (s)")
    plt.title("Tempo de Hash - Medições do Servidor")
    plt.savefig(results_dir / "plot_time_per_hash.png")
    plt.close()

print("✅ prepare_results.py finalizado. Arquivos CSV e gráficos gerados em results/")