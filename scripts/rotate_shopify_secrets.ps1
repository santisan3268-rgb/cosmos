$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$envPath = Join-Path $projectRoot ".env.local"
$backupDir = Join-Path $projectRoot ".env-backups"

if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
}

if (Test-Path $envPath) {
    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    Copy-Item $envPath (Join-Path $backupDir ".env.local.$stamp.bak")
    Write-Host "Backup creado en .env-backups/"
}

$current = @{}
if (Test-Path $envPath) {
    Get-Content $envPath | ForEach-Object {
        if ($_ -match '^\s*([A-Z0-9_]+)=(.*)$') {
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

Write-Host "Rotacion guiada de secretos Shopify (.env.local)"
Write-Host "Deja en blanco para conservar valor actual."

$shopUrl = Read-OrCurrent "SHOPIFY_STORE_URL" "SHOPIFY_STORE_URL (ej: tienda.myshopify.com)"
$shop = Read-OrCurrent "SHOPIFY_SHOP" "SHOPIFY_SHOP (ej: tienda)"
$clientId = Read-OrCurrent "SHOPIFY_CLIENT_ID" "SHOPIFY_CLIENT_ID"
$clientSecret = Read-OrCurrent "SHOPIFY_CLIENT_SECRET" "SHOPIFY_CLIENT_SECRET (oculto)" $true
$accessToken = Read-OrCurrent "SHOPIFY_ACCESS_TOKEN" "SHOPIFY_ACCESS_TOKEN (legacy, opcional)" $true
$scopes = Read-OrCurrent "SHOPIFY_SCOPES" "SHOPIFY_SCOPES"

if ([string]::IsNullOrWhiteSpace($scopes)) {
    $scopes = "read_analytics,read_customers,read_orders,read_products,read_reports"
}

$lines = @(
    "SHOPIFY_STORE_URL=$shopUrl",
    "SHOPIFY_SHOP=$shop",
    "SHOPIFY_CLIENT_ID=$clientId",
    "SHOPIFY_CLIENT_SECRET=$clientSecret",
    "",
    "# Compatibilidad temporal con flujo legacy (dejar vacio en flujo 2026)",
    "SHOPIFY_ACCESS_TOKEN=$accessToken",
    "",
    "SHOPIFY_SCOPES=$scopes"
)

Set-Content -Path $envPath -Value $lines -Encoding UTF8
Write-Host ".env.local actualizado"

# Validacion rapida de formato
$required = @("SHOPIFY_STORE_URL", "SHOPIFY_SHOP", "SHOPIFY_CLIENT_ID", "SHOPIFY_CLIENT_SECRET")
$missing = @()
foreach ($k in $required) {
    if (-not $current.ContainsKey($k) -and ($lines -notmatch "^$k=")) {
        $missing += $k
    }
}

if ($missing.Count -gt 0) {
    Write-Host "Advertencia: faltan variables requeridas: $($missing -join ', ')"
} else {
    Write-Host "Variables principales presentes."
}
