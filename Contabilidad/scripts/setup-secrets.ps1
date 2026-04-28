# Script para configurar variables de entorno de seguridad
# Uso: .\scripts\setup-secrets.ps1

param(
    [string]$Password = "",
    [int]$SessionHours = 8,
    [string]$AllowedIPs = ""
)

# Validar que se proporcione contraseña
if ([string]::IsNullOrWhiteSpace($Password)) {
    Write-Host "ERROR: Debes proporcionar una contraseña" -ForegroundColor Red
    Write-Host "Uso: .\scripts\setup-secrets.ps1 -Password 'TuContraseña'" -ForegroundColor Yellow
    exit 1
}

Write-Host "Configurando variables de entorno..." -ForegroundColor Cyan

# Configurar permanentemente en el registro de Windows
[Environment]::SetEnvironmentVariable("CONTA_APP_PASSWORD", $Password, "User")
[Environment]::SetEnvironmentVariable("CONTA_SESSION_HOURS", $SessionHours.ToString(), "User")

if (-not [string]::IsNullOrWhiteSpace($AllowedIPs)) {
    [Environment]::SetEnvironmentVariable("CONTA_ALLOWED_IPS", $AllowedIPs, "User")
} else {
    [Environment]::SetEnvironmentVariable("CONTA_ALLOWED_IPS", "", "User")
}

# Configurar también en la sesión actual
$env:CONTA_APP_PASSWORD = $Password
$env:CONTA_SESSION_HOURS = $SessionHours.ToString()
$env:CONTA_ALLOWED_IPS = $AllowedIPs

Write-Host "✓ CONTA_APP_PASSWORD configurado" -ForegroundColor Green
Write-Host "✓ CONTA_SESSION_HOURS configurado a $SessionHours horas" -ForegroundColor Green
Write-Host "✓ CONTA_ALLOWED_IPS configurado" -ForegroundColor Green
Write-Host "" -ForegroundColor Green
Write-Host "Variables configuradas exitosamente. Reinicia PowerShell para que surta efecto global." -ForegroundColor Green

# Verificar
Write-Host "" -ForegroundColor Cyan
Write-Host "Verificación (sesión actual):" -ForegroundColor Cyan
Write-Host "  CONTA_APP_PASSWORD: $(if ($env:CONTA_APP_PASSWORD) { '***' } else { 'NO CONFIGURADO' })" -ForegroundColor Gray
Write-Host "  CONTA_SESSION_HOURS: $env:CONTA_SESSION_HOURS" -ForegroundColor Gray
Write-Host "  CONTA_ALLOWED_IPS: $(if ($env:CONTA_ALLOWED_IPS) { $env:CONTA_ALLOWED_IPS } else { '(por defecto)' })" -ForegroundColor Gray
