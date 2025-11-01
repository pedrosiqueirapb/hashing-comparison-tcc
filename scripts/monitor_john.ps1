param(
    [Parameter(Mandatory=$true)][int]$TargetPID,
    [double]$interval = 0.5,
    [string]$outfile = "..\results\john_monitor.csv"
)

# cabeçalho
"timestamp,cpu_percent,mem_mb" | Out-File -FilePath $outfile -Encoding utf8

# tenta pegar o processo; se não existir, termina
try {
    $proc = Get-Process -Id $TargetPID -ErrorAction Stop
} catch {
    Write-Host "Processo $TargetPID não encontrado. Monitor encerrado."
    exit 0
}

$prevCPU = $proc.TotalProcessorTime.TotalSeconds
$prevTime = Get-Date
while ($true) {
    Start-Sleep -Seconds $interval
    $proc.Refresh()
    if ($proc.HasExited) { break }
    $curCPU = $proc.TotalProcessorTime.TotalSeconds
    $curTime = Get-Date
    $elapsed = ($curTime - $prevTime).TotalSeconds
    if ($elapsed -gt 0) {
        $cpuPct = (($curCPU - $prevCPU)/$elapsed) * 100
    } else {
        $cpuPct = 0
    }
    $memMB = [math]::Round($proc.WorkingSet64 / 1MB, 2)
    "$($curTime.ToString('o')),$([math]::Round($cpuPct,2)),$memMB" | Out-File -FilePath $outfile -Append -Encoding utf8
    $prevCPU = $curCPU
    $prevTime = $curTime
}