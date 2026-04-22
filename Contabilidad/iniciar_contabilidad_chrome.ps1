$ErrorActionPreference = "Stop"

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir

$pythonExe = Join-Path $projectDir ".venv\Scripts\python.exe"
$chromeExe = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$url = "http://127.0.0.1:8501"

if (-not (Test-Path $pythonExe)) {
    Write-Host "No se encontro Python del entorno virtual:" $pythonExe
    exit 1
}

# Si el puerto ya esta ocupado, no tumbamos nada: abrimos el navegador y listo.
$portInUse = Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue

if (-not $portInUse) {
    Start-Process -FilePath $pythonExe -ArgumentList "-m", "streamlit", "run", "app.py", "--server.address", "127.0.0.1", "--server.port", "8501" -WorkingDirectory $projectDir
    Write-Host "Streamlit iniciado en" $url
} else {
    Write-Host "Puerto 8501 ya en uso. Se abrira la URL existente." 
}

if (Test-Path $chromeExe) {
    Start-Process -FilePath $chromeExe -ArgumentList $url
    Write-Host "Chrome abierto en" $url
} else {
    Start-Process $url
    Write-Host "Chrome no encontrado por ruta directa; se abrio navegador predeterminado en" $url
}
