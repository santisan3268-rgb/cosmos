$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $projectRoot '.venv\Scripts\python.exe'

if (Test-Path $venvPython) {
    $pythonCmd = $venvPython
} else {
    $pythonCmd = 'python'
}

Push-Location $projectRoot
try {
    & $pythonCmd -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }

    & $pythonCmd -m py_compile app.py sql_horas_app.py conta_core\parser_utils.py conta_core\sql_utils.py conta_core\export_utils.py
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }

    Write-Host 'Checks de calidad completados.' -ForegroundColor Green
} finally {
    Pop-Location
}
