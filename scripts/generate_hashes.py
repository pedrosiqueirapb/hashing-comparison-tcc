import hashlib
import secrets
import base64
import bcrypt
from argon2 import PasswordHasher
from pathlib import Path

pw_list = ["senha123", "P@ssw0rd2024", "Tr3ndMUsic!99"]

# parâmetros (valores para testes rápidos; aumente para experimento real)
BCRYPT_ROUNDS_TEST = 4            # rounds baixos para testes rápidos
ARGON2_TIME = 2                   # tempo (iteração) para argon2 (teste)
ARGON2_MEMORY_KB = 16384          # memória em KiB (16 MiB) - modesto para testes
ARGON2_PARALLELISM = 1
SCRYPT_N = 16384                  # cost factor
SCRYPT_r = 8
SCRYPT_p = 1
SCRYPT_DKLEN = 64                 # bytes

# ---------- PATHS (usa estrutura do repo) ----------
repo_root = Path(__file__).resolve().parents[1]  # pasta do repositório (repo/)
data_dir = repo_root / "data"
hashes_dir = repo_root / "hashes"
results_dir = repo_root / "results"

data_dir.mkdir(parents=True, exist_ok=True)
hashes_dir.mkdir(parents=True, exist_ok=True)
results_dir.mkdir(parents=True, exist_ok=True)

# ---------- Arquivos de saída (nomes claros) ----------
wl_path = data_dir / "wordlist_test.txt"
bcrypt_out = hashes_dir / "bcrypt_test_r4.txt"
sha256_out = hashes_dir / "sha256_test.txt"
argon2_out = hashes_dir / "argon2_test.txt"
scrypt_out = hashes_dir / f"scrypt_N{SCRYPT_N}_r{SCRYPT_r}_p{SCRYPT_p}.txt"

# 1) cria wordlist_test.txt
with wl_path.open("w", encoding="utf-8") as f:
    for p in pw_list:
        f.write(p + "\n")

# 2) gera bcrypt (arquivo)
with bcrypt_out.open("w", encoding="utf-8") as f:
    for p in pw_list:
        h = bcrypt.hashpw(p.encode("utf-8"), bcrypt.gensalt(BCRYPT_ROUNDS_TEST)).decode("utf-8")
        f.write(h + "\n")

# 3) gera sha256 (hex)
with sha256_out.open("w", encoding="utf-8") as f:
    for p in pw_list:
        h = hashlib.sha256(p.encode("utf-8")).hexdigest()
        f.write(h + "\n")

# 4) gera argon2 (PHC string)
ph = PasswordHasher(time_cost=ARGON2_TIME, memory_cost=ARGON2_MEMORY_KB, parallelism=ARGON2_PARALLELISM)
with argon2_out.open("w", encoding="utf-8") as f:
    for p in pw_list:
        h = ph.hash(p)
        f.write(h + "\n")

# 5) gera scrypt (formato PHC-like)
#    formato: id:$scrypt$N=...,r=...,p=...$<salt_b64>$<dk_hex>
with scrypt_out.open("w", encoding="utf-8") as f:
    for idx, p in enumerate(pw_list, start=1):
        salt = secrets.token_bytes(16)
        dk = hashlib.scrypt(p.encode("utf-8"), salt=salt, n=SCRYPT_N, r=SCRYPT_r, p=SCRYPT_p, dklen=SCRYPT_DKLEN)
        salt_b64 = base64.b64encode(salt).decode("ascii")
        dk_hex = dk.hex()
        f.write(f"{idx}:$scrypt$N={SCRYPT_N},r={SCRYPT_r},p={SCRYPT_p}${salt_b64}${dk_hex}\n")

# 6) resumo para usuário
print("Arquivos gerados (todos UTF-8 sem BOM):")
print(" - wordlist      :", wl_path)
print(" - bcrypt (test) :", bcrypt_out)
print(" - sha256        :", sha256_out)
print(" - argon2        :", argon2_out)
print(" - scrypt        :", scrypt_out)