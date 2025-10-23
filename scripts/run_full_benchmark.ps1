param(
    [int]$bcrypt_rounds = 12
)

$johnPath = "C:\john\john-1.9.0-jumbo-1-win64\run\john.exe"
if (-not (Test-Path $johnPath)) {
    Write-Error "john.exe não encontrado em $johnPath - ajuste a variável no script."
    exit 1
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$repoRoot = Resolve-Path (Join-Path $scriptDir "..")
Set-Location $repoRoot

# garantir pastas
$dirs = @(".\results", ".\hashes", ".\data")
foreach ($d in $dirs) { if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d | Out-Null } }

Write-Host "Apagando arquivos antigos em results/ ..."
Remove-Item .\results\* -Force -Recurse -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 200

# 1) gerar hashes
Write-Host "Gerando hashes (bcrypt r$bcrypt_rounds, sha256, argon2)..."
python .\scripts\generate_hashes_full.py --bcrypt-rounds $bcrypt_rounds
if ($LASTEXITCODE -ne 0) { Write-Error "generate_hashes_full.py falhou. Verifique saída."; exit 1 }

# 2) benchmark servidor
Write-Host "Rodando benchmark do servidor..."
python .\scripts\benchmark_server.py
if ($LASTEXITCODE -ne 0) { Write-Warning "benchmark_server.py retornou código diferente de zero. Verifique." }

# função que inicia John e chama o monitor; recebe os args do John e o caminho do arquivo de hash
function Run-John-And-Monitor {
    param(
        [string]$johnArgs,
        [string]$hashFile,
        [string]$outfile_monitor,
        [string]$outfile_show,
        [string]$potfile
    )

    if (-not (Test-Path $hashFile)) {
        Write-Warning "Arquivo de hash não encontrado: $hashFile"
        return
    }

    # start John process
    $proc = Start-Process -FilePath $johnPath -ArgumentList @($johnArgs) -PassThru -WindowStyle Normal
    Start-Sleep -Seconds 1
    if (-not $proc) {
        Write-Warning "John não iniciou para $hashFile"
        return
    }
    Write-Host "John iniciado. PID: $($proc.Id) (hashfile: $hashFile)"

    # rodar monitor_john.ps1 — este script bloqueia até o processo terminar (ele monitora o PID)
    try {
        .\scripts\monitor_john.ps1 -TargetPID $proc.Id -interval 1 -outfile $outfile_monitor
    } catch {
        Write-Warning "Falha ao executar monitor_john.ps1: $_"
    }

    # espera John encerrar (caso monitor não tenha feito)
    $proc.WaitForExit()

    # exporta --show para o arquivo solicitado
    & $johnPath --show $hashFile > $outfile_show
    Write-Host "John terminou. Show salvo em: $outfile_show  (pot: $potfile)"
}

# 3) rodar John para bcrypt
$bcryptFile = ".\hashes\bcrypt_test_r$bcrypt_rounds.txt"
if (-not (Test-Path $bcryptFile)) { Write-Error "Arquivo de hashes bcrypt faltando: $bcryptFile"; exit 1 }
$potB = ".\results\john_bcrypt.pot"
$monitorB = ".\results\john_bcrypt_monitor.csv"
$showB = ".\results\john_bcrypt_show.txt"
$johnArgsB = "--format=bcrypt --wordlist=.\\data\\wordlist_test.txt --rules --pot=$potB $bcryptFile"

Run-John-And-Monitor -johnArgs $johnArgsB -hashFile $bcryptFile -outfile_monitor $monitorB -outfile_show $showB -potfile $potB

# 4) rodar John para SHA-256
$shaFile = ".\hashes\sha256_test.txt"
if (-not (Test-Path $shaFile)) { Write-Error "Arquivo de hashes sha256 faltando: $shaFile"; exit 1 }
$potS = ".\results\john_sha256.pot"
$monitorS = ".\results\john_sha256_monitor.csv"
$showS = ".\results\john_sha256_show.txt"
$johnArgsS = "--format=raw-sha256 --wordlist=.\\data\\wordlist_test.txt --rules --pot=$potS $shaFile"

Run-John-And-Monitor -johnArgs $johnArgsS -hashFile $shaFile -outfile_monitor $monitorS -outfile_show $showS -potfile $potS

# 5) preparar resultados finais
Write-Host "Preparando resultados finais (CSV + gráficos)..."
python .\scripts\prepare_results.py
if ($LASTEXITCODE -ne 0) { Write-Warning "prepare_results.py falhou (verifique se matplotlib está instalado)." }

Write-Host "✅ Processo finalizado. Veja a pasta results/ para outputs."
