from pathlib import Path

results_dir = Path("results")

def try_read(path):
    for enc in ("utf-8", "utf-16", "latin-1"):
        try:
            text = path.read_text(encoding=enc)
            print(f"\n✅ Lido com sucesso usando {enc}: {path.name}")
            print("-" * 50)
            print(text[:300])
            print("-" * 50)
            return
        except Exception as e:
            print(f"❌ Falha com {enc}: {e}")
    print(f"🚫 Nenhuma codificação funcionou para {path.name}")

for name in ["john_bcrypt_show.txt", "john_sha256_show.txt"]:
    file_path = results_dir / name
    if file_path.exists():
        try_read(file_path)
    else:
        print(f"⚠️ Arquivo não encontrado: {file_path}")