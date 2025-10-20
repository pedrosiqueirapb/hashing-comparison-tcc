import time, psutil, os, hashlib, csv
from statistics import mean, stdev
import bcrypt
from argon2 import PasswordHasher

repo_root = os.path.dirname(os.path.dirname(__file__))
data_file = os.path.join(repo_root, "data", "wordlist_test.txt")

def load_passwords():
    with open(data_file, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

# funções que geram hash (simulando custo do servidor ao criar/verificar)
def do_sha256(pw):
    hashlib.sha256(pw.encode("utf-8")).hexdigest()

def do_bcrypt(pw, rounds=12):
    bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt(rounds))

def do_argon2(pw, time_cost=2, memory_kib=16384, parallelism=1):
    ph = PasswordHasher(time_cost=time_cost, memory_cost=memory_kib, parallelism=parallelism)
    ph.hash(pw)

def measure(func, password, repeats=3, **kwargs):
    times = []
    mem_usages = []
    for _ in range(repeats):
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss
        t0 = time.perf_counter()
        func(password, **kwargs)
        t1 = time.perf_counter()
        mem_after = process.memory_info().rss
        times.append(t1 - t0)
        mem_usages.append(mem_after - mem_before)
    avg_time = sum(times) / len(times)
    avg_mem = sum(mem_usages) / len(mem_usages)
    std_time = (sum((t - avg_time) ** 2 for t in times) / len(times)) ** 0.5
    return avg_time, std_time, avg_mem

def main():
    pws = load_passwords()
    results = []
    bcrypt_rounds = [4, 12] # 4 é para teste rápido, 12 para parâmetro real (exemplo)
    argon2_configs = [
        {"time":2, "mem_kib":16384, "par":1},
    ]
    # measure SHA-256
    for pw in pws:
        t, sd, mem = measure(do_sha256, pw, repeats=10)
        results.append(["sha256", "none", pw, t, sd, mem])

    # measure bcrypt (one param set)
    for rounds in bcrypt_rounds:
        for pw in pws:
            t, sd, mem = measure(do_bcrypt, pw, repeats=5, rounds=rounds)
            results.append(["bcrypt", f"rounds={rounds}", pw, t, sd, mem])

    # measure argon2 configs
    for cfg in argon2_configs:
        for pw in pws:
            t, sd, mem = measure(do_argon2, pw, repeats=3, time_cost=cfg["time"], memory_kib=cfg["mem_kib"], parallelism=cfg["par"])
            results.append(["argon2", f"t={cfg['time']},m={cfg['mem_kib']}KiB,p={cfg['par']}", pw, t, sd, mem])

    # salvar CSV
    outcsv = os.path.join(repo_root, "results", "server_benchmarks.csv")
    with open(outcsv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["algorithm","param","password","mean_s","stdev_s","mem_rss_bytes"])
        writer.writerows(results)
    print("Saved:", outcsv)

if __name__ == "__main__":
    main()
