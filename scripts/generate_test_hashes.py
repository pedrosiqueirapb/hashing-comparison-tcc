# Gera 3 hashes de teste (bcrypt, sha256, argon2) e cria wordlist_test.txt
import bcrypt
import hashlib
from argon2 import PasswordHasher
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
data_dir = repo_root / "data"
hashes_dir = repo_root / "hashes"
results_dir = repo_root / "results"

data_dir.mkdir(exist_ok=True)
hashes_dir.mkdir(exist_ok=True)
results_dir.mkdir(exist_ok=True)

pw_list = ["senha123", "P@ssw0rd2024", "Tr3ndMUsic!99"]

# criar wordlist de teste (uma senha por linha) - UTF-8 sem BOM
wl_path = data_dir / "wordlist_test.txt"
with wl_path.open("w", encoding="utf-8") as f:
    for p in pw_list:
        f.write(p + "\n")

# bcrypt (rounds=4) - arquivo: hashes/bcrypt_test_r4.txt
with (hashes_dir / "bcrypt_test_r4.txt").open("w", encoding="utf-8") as f:
    for p in pw_list:
        h = bcrypt.hashpw(p.encode(), bcrypt.gensalt(4)).decode()  # rounds=4 para teste rápido
        f.write(h + "\n")

# sha256 (hex) - arquivo: hashes/sha256_test.txt
with (hashes_dir / "sha256_test.txt").open("w", encoding="utf-8") as f:
    for p in pw_list:
        h = hashlib.sha256(p.encode()).hexdigest()
        f.write(h + "\n")

# argon2 (parâmetros modestos para teste) - arquivo: hashes/argon2_test.txt
# memory_cost em kibibytes; aqui usamos 16384 KB = 16 MB (rápido suficiente para testes)
ph = PasswordHasher(time_cost=2, memory_cost=16384, parallelism=1)
with (hashes_dir / "argon2_test.txt").open("w", encoding="utf-8") as f:
    for p in pw_list:
        h = ph.hash(p)
        f.write(h + "\n")

print("Gerado:")
print(" -", wl_path)
print(" -", hashes_dir / "bcrypt_test_r4.txt")
print(" -", hashes_dir / "sha256_test.txt")
print(" -", hashes_dir / "argon2_test.txt")