# SECURITY_SETUP.md – Guía de Configuración de Seguridad

## Resumen rápido

Antes de ejecutar `streamlit run app.py`, necesitas configurar **UNA** de estas opciones:

### ⚡ Opción Rápida (Recomendada para usuarios Windows)

```powershell
cd C:\Users\Santiago Sanchez\Desktop\cosmos\Contabilidad
.\scripts\setup-secrets.ps1 -Password "MiContraseñaSegura123"
```

Reinicia PowerShell y ejecuta:
```powershell
python -m streamlit run app.py
```

### 🔐 Opción Manual: secrets.toml

1. Copia ``.streamlit/secrets.toml.example` → `.streamlit/secrets.toml`
2. Edita el archivo con tu contraseña
3. Ejecuta: `python -m streamlit run app.py`

### ☁️ Opción Cloud: Streamlit Community Cloud

1. Sube el proyecto a GitHub
2. Conecta repositorio en https://streamlit.io/cloud
3. En Settings → Secrets, agrega:
   ```
   APP_PASSWORD = "TuContraseña"
   ```
4. Deploy

---

## Variables de configuración disponibles

| Variable | Env var | Descripción | Default | Requerido |
|----------|---------|-------------|---------|-----------|
| APP_PASSWORD | CONTA_APP_PASSWORD | Contraseña de acceso | - | ✓ Sí |
| APP_SESSION_HOURS | CONTA_SESSION_HOURS | Horas de sesión activa | 8 | ✗ No |
| APP_ALLOWED_IPS | CONTA_ALLOWED_IPS | IPs permitidas (CSV/CIDR) | 127.0.0.1, ::1, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 | ✗ No |

---

## Seguridad: Reglas importantes

- **NUNCA** subas `.streamlit/secrets.toml` a GitHub (está en `.gitignore`)
- **NUNCA** incluyas contraseñas en el código
- **NUNCA** compartas variables de entorno por chat/email
- Usa contraseñas **fuertes** (mínimo 12 caracteres mixtos)
- Cambia contraseña cada **3 meses**
- Las sesiones expiran después de **8 horas** (configurable)
- Las IPs que no estén en whitelist son **rechazadas automáticamente**

---

## Troubleshooting

**"ERROR: APP_PASSWORD no está configurado"**
→ Ejecuta `.\scripts\setup-secrets.ps1` o crea `.streamlit/secrets.toml`

**"No estás autorizado (IP bloqueada)"**
→ Tu IP no está en `APP_ALLOWED_IPS`. Verifica con `ipconfig` y agrega tu rango

**"Sesión expirada"**
→ Normal. Inicia sesión de nuevo. Las sesiones duran 8 horas por defecto

**"¿Dónde está mi contraseña?"**
→ En variables de entorno (`setx CONTA_APP_PASSWORD`) o en `.streamlit/secrets.toml` (local only)

---

## Para agentes de IA (CLAUDE.md)

Cuando trabajes en este proyecto:
1. **NUNCA** escribas contraseñas en código
2. Verifica que secrets.toml esté en .gitignore
3. Las contraseñas se leen desde `_get_secret_or_env()` en app.py
4. Documentación de seguridad en CLAUDE.md línea ~40
