param(
    [switch]$TestConnection
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$secretsDir = Join-Path $projectRoot ".streamlit"
$secretsPath = Join-Path $secretsDir "secrets.toml"
$backupDir = Join-Path $secretsDir "backups"

if (-not (Test-Path $secretsDir)) {
    New-Item -ItemType Directory -Path $secretsDir | Out-Null
}
if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
}

if (Test-Path $secretsPath) {
    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    Copy-Item $secretsPath (Join-Path $backupDir "secrets_$stamp.toml")
    Write-Host "Backup creado en .streamlit/backups"
}

Write-Host "Rotacion guiada de credenciales SQL"
Write-Host "Deja en blanco para conservar el valor actual cuando exista."

$current = @{}
if (Test-Path $secretsPath) {
    Get-Content $secretsPath | ForEach-Object {
        if ($_ -match '^\s*([A-Z_]+)\s*=\s*"?(.*?)"?\s*$') {
            $current[$matches[1]] = $matches[2]
        }
    }
}

function Read-OrCurrent([string]$name, [string]$prompt, [bool]$isSecret = $false) {
    if ($isSecret) {
        $secure = Read-Host -Prompt $prompt -AsSecureString
        $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
        try {
            $plain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
        } finally {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
        }
        if ([string]::IsNullOrWhiteSpace($plain)) {
            return $current[$name]
        }
        return $plain
    }

    $v = Read-Host -Prompt $prompt
    if ([string]::IsNullOrWhiteSpace($v)) {
        return $current[$name]
    }
    return $v
}

$dbServer = Read-OrCurrent "DB_SERVER" "DB_SERVER"
$dbPort = Read-OrCurrent "DB_PORT" "DB_PORT (ej: 1433)"
$dbName = Read-OrCurrent "DB_NAME" "DB_NAME"
$dbUser = Read-OrCurrent "DB_USER" "DB_USER"
$dbPass = Read-OrCurrent "DB_PASSWORD" "DB_PASSWORD (oculto)" $true
$dbValidateHost = Read-OrCurrent "DB_VALIDATE_HOST" "DB_VALIDATE_HOST [true/false]"

if ([string]::IsNullOrWhiteSpace($dbPort)) { $dbPort = "1433" }
if ([string]::IsNullOrWhiteSpace($dbValidateHost)) { $dbValidateHost = "true" }

$toml = @(
    "DB_SERVER = `"$dbServer`"",
    "DB_PORT = $dbPort",
    "DB_NAME = `"$dbName`"",
    "DB_USER = `"$dbUser`"",
    "DB_PASSWORD = `"$dbPass`"",
    "DB_VALIDATE_HOST = $dbValidateHost"
)

Set-Content -Path $secretsPath -Value $toml -Encoding UTF8
Write-Host "secrets.toml actualizado en .streamlit/"

if ($TestConnection) {
    $pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path $pythonExe)) {
        Write-Host "No se encontro Python del entorno virtual para probar conexion."
        exit 0
    }

    $testCode = @"
import os
import streamlit as st
import pytds

cfg = {
  'server': st.secrets.get('DB_SERVER', os.getenv('DB_SERVER')),
  'port': int(st.secrets.get('DB_PORT', os.getenv('DB_PORT', '1433'))),
  'name': st.secrets.get('DB_NAME', os.getenv('DB_NAME')),
  'user': st.secrets.get('DB_USER', os.getenv('DB_USER')),
  'password': st.secrets.get('DB_PASSWORD', os.getenv('DB_PASSWORD')),
}
validate_host = str(st.secrets.get('DB_VALIDATE_HOST', os.getenv('DB_VALIDATE_HOST', 'true'))).lower() in {'1','true','yes','y','si','on'}

conn = pytds.connect(server=cfg['server'], port=cfg['port'], database=cfg['name'], user=cfg['user'], password=cfg['password'], validate_host=validate_host)
cur = conn.cursor()
cur.execute('SELECT 1')
print('SQL_OK' if cur.fetchone()[0] == 1 else 'SQL_FAIL')
conn.close()
"@

    & $pythonExe -c $testCode
}
