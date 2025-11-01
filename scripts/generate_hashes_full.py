import argparse
import hashlib
import bcrypt
from argon2 import PasswordHasher
from pathlib import Path
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("--bcrypt-rounds", type=int, default=12)
args = parser.parse_args()

repo_root = Path(__file__).resolve().parents[1]
data_dir = repo_root / "data"
hashes_dir = repo_root / "hashes"
results_dir = repo_root / "results"

data_dir.mkdir(parents=True, exist_ok=True)
hashes_dir.mkdir(parents=True, exist_ok=True)
results_dir.mkdir(parents=True, exist_ok=True)

xlsx_path = data_dir / "passwords.xlsx"
if not xlsx_path.exists():
    raise SystemExit("ERRO: data/passwords.xlsx não encontrado. Preencha e rode novamente.")

df = pd.read_excel(xlsx_path)
cols = {c.lower(): c for c in df.columns}
if "password" in cols:
    pw_list = df[cols["password"]].astype(str).dropna().tolist()
else:
    first_col = df.columns[0]
    pw_list = df[first_col].astype(str).dropna().tolist()

pw_list = [p.strip() for p in pw_list]

wl_path = data_dir / "wordlist_test.txt"
bcrypt_out = hashes_dir / f"bcrypt_test_r{args.bcrypt_rounds}.txt"
sha256_out = hashes_dir / "sha256_test.txt"
argon2_out = hashes_dir / "argon2_test.txt"

# 1) wordlist
with wl_path.open("w", encoding="utf-8") as f:
    for p in pw_list:
        f.write(p + "\n")

# 2) bcrypt
with bcrypt_out.open("w", encoding="utf-8") as f:
    for p in pw_list:
        h = bcrypt.hashpw(p.encode("utf-8"), bcrypt.gensalt(args.bcrypt_rounds)).decode("utf-8")
        f.write(h + "\n")

# 3) sha256
with sha256_out.open("w", encoding="utf-8") as f:
    for p in pw_list:
        h = hashlib.sha256(p.encode("utf-8")).hexdigest()
        f.write(h + "\n")

# 4) argon2
ARGON2_TIME = 2
ARGON2_MEMORY_KB = 16384
ARGON2_PARALLELISM = 1
ph = PasswordHasher(time_cost=ARGON2_TIME, memory_cost=ARGON2_MEMORY_KB, parallelism=ARGON2_PARALLELISM)
with argon2_out.open("w", encoding="utf-8") as f:
    for p in pw_list:
        h = ph.hash(p)
        f.write(h + "\n")

print("Gerado com sucesso:")
print(" -", wl_path)
print(" -", bcrypt_out)
print(" -", sha256_out)
print(" -", argon2_out)