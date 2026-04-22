# Guía Visual: Crear App Personalizada en Dev Dashboard (2026)

## 🎯 Objetivo Final

Obtener `Client ID` y `Client Secret` para conectar tu dashboard Next.js a Shopify GraphQL Admin API.

---

## PASO 1: Acceder al Dev Dashboard

### Opción A: Desde el Admin de Shopify

1. Abre https://admin.shopify.com/store/calzado-cosmos/
2. Haz clic en tu nombre de tienda **(arriba a la derecha)**
3. Selecciona **"Dev Dashboard"**

### Opción B: Acceso Directo

- Abre directamente https://dev.shopify.com/dashboard/

```
┌─────────────────────────────────────┐
│  Your Store Name                    │
│  ┌─────────────────────────────────┐│
│  │  Dev Dashboard          ← Click  ││
│  │  Settings                       ││
│  │  Notifications                  ││
│  │  Logout                         ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
```

---

## PASO 2: Crear Nueva App

### Vista del Dashboard

```
┌─ DEV DASHBOARD ──────────────────────────────┐
│                                              │
│  APPS (en panel izquierdo)                  │
│  ├─ Create app ────────────┐                │
│  │                         │                │
│  └─────────────────────────┘                │
│                                              │
│  (si tienes apps existentes aparecerán)    │
│                                              │
└──────────────────────────────────────────────┘
```

### Acciones:

1. En el panel izquierdo, asegúrate de estar en **APPS**
2. Haz clic en botón azul **"Create app"** (arriba a la derecha)

---

## PASO 3: Seleccionar Tipo de App

```
┌─ CREATE APP ─────────────────────────────────┐
│                                              │
│  ┌─ Start from Dev Dashboard ──────────┐   │
│  │  Para: Backend, API, Automatización │   │
│  │  Selecciona esto →                  │ ✅│
│  └──────────────────────────────────────┘   │
│                                              │
│  ┌─ (Other options for CLI apps) ───┐     │
│  │  Shopify CLI (ignorar por ahora)  │     │
│  └──────────────────────────────────┘      │
│                                              │
└──────────────────────────────────────────────┘
```

**Opción correcta:** "Start from Dev Dashboard"

---

## PASO 4: Nombrar tu App

```
┌─ NOMBRE DE LA APP ────────────────────────────┐
│                                              │
│  Nombre: ┌────────────────────────────────┐ │
│          │ FYC Calzado Analytics Dashboard│ │
│          └────────────────────────────────┘ │
│                                              │
│  Descripción (opcional):                    │
│  ┌────────────────────────────────────┐     │
│  │ Dashboard de analytics integrado   │     │
│  │ con Shopify GraphQL Admin API      │     │
│  └────────────────────────────────────┘     │
│                                              │
│                            [Cancelar] [Crear]│
└──────────────────────────────────────────────┘
```

**Tu nombre sugerido:** "FYC Calzado Analytics Dashboard"

---

## PASO 5: Crear Versión (Importante)

Una vez creada la app, necesitas crear una **Versión** antes de instalar.

```
┌─ Tu App > VERSIONS ──┐
│                      │
│  [Release Version]   │
│                      │
│  Nombre (opcional):  │
│  [v1.0]             │
│                      │
│  Descripción:       │
│  [Initial Release]  │
│                      │
└──────────────────────┘
```

### Campos a Completar:

#### 1️⃣ **App URLs**

```
┌─ App URLs ────────────────────────────┐
│                                       │
│ App Home URL *                        │
│ ┌─────────────────────────────────────┐
│ │ https://shopify.dev/apps/...        │
│ │ (o tu URL si tienes servidor)       │
│ └─────────────────────────────────────┘
│                                       │
│ Embedded Admin URL (optonal)          │
│ ┌─────────────────────────────────────┐
│ │ [Dejar en blanco para API-only]     │
│ └─────────────────────────────────────┘
│                                       │
│ Redirects URLs (opcional)             │
│ ┌─────────────────────────────────────┐
│ │ [Para OAuth, no necesario]          │
│ └─────────────────────────────────────┘
│                                       │
└───────────────────────────────────────┘
```

#### 2️⃣ **Webhooks API Version**

```
┌─ Webhooks Configuration ──────────────┐
│                                       │
│ Webhooks API Version:                 │
│ ┌─────────────────────────────────────┐
│ │ 2026-01  ← Selecciona esta          │
│ │ 2025-10                             │
│ │ 2025-07                             │
│ │ (versiones más recientes)           │
│ └─────────────────────────────────────┘
│                                       │
└───────────────────────────────────────┘
```

#### 3️⃣ **Admin API Scopes (CRÍTICO)**

```
┌─ Access Scopes ───────────────────────┐
│ Necesarios para tu dashboard:         │
│                                       │
│ ☑ read_orders                         │
│   └─ Leer órdenes                    │
│                                       │
│ ☑ read_products                       │
│   └─ Leer catálogo de productos      │
│                                       │
│ ☑ read_customers                      │
│   └─ Leer datos de clientes           │
│                                       │
│ ☑ read_analytics                      │
│   └─ Leer métricas de tienda          │
│                                       │
│ ☐ read_inventory (optativo)           │
│   └─ Leer niveles de stock            │
│                                       │
│ ☐ read_fulfillments (optativo)        │
│   └─ Leer estado de envíos            │
│                                       │
└───────────────────────────────────────┘
```

**Configuración recomendada:**

```
read_orders, read_products, read_customers, read_analytics
```

---

## PASO 6: Liberar (Release) la Versión

```
┌─ VERSION SUMMARY ──┐
│                    │
│  [Release Version] │
│                    │
│  Verifica:         │
│  ✓ URLs OK         │
│  ✓ Webhooks Ver.   │
│  ✓ Scopes OK       │
│                    │
│       [Release]    │
│                    │
└────────────────────┘
```

Haz clic en **"Release"** para confirmar la versión.

---

## PASO 7: Instalar App en Tienda

```
┌─ Tu App > HOME ────────────────────────┐
│                                        │
│  Current Version: v1.0                │
│                                        │
│  Status: Ready to install              │
│                                        │
│  ┌──────────────────────────────────┐  │
│  │  [Install app]                   │  │
│  └──────────────────────────────────┘  │
│                                        │
│  Installs: 0/1                         │
│                                        │
└────────────────────────────────────────┘
```

1. En la pestaña **"Home"**, desplázate hacia abajo
2. Haz clic en **"Install app"**
3. Selecciona tu tienda (calzado-cosmos)
4. Haz clic en **"Install"**

---

## PASO 8: ⭐ OBTENER CREDENCIALES (CLAVE)

```
┌─ Tu App > SETTINGS ────────────────────┐
│                                        │
│  ADMIN API CREDENTIALS                │
│                                        │
│  Client ID:                            │
│  ┌────────────────────────────────────┐│
│  │ e7c8d9f1a2b3c4d5e6f7g8h9i0j1k2    ││
│  │                      [Copy]         ││
│  └────────────────────────────────────┘│
│                                        │
│  Client Secret:                        │
│  ┌────────────────────────────────────┐│
│  │ ••••••••••••••••••••••••••••••••   ││
│  │ (mostrado al crear)      [Show]    ││
│  │ si no lo copiaste aquí → [Reset]   ││
│  └────────────────────────────────────┘│
│                                        │
│  Scopes: read_orders, read_...        │
│                                        │
└────────────────────────────────────────┘
```

### ⚠️ INSTRUCCIONES CRÍTICAS:

1. Abre la pestaña **"Settings"** de tu app
2. Desplázate hasta **"Admin API credentials"**
3. **COPIA el Client ID** (es público, sin problema)

   ```
   SHOPIFY_CLIENT_ID=e7c8d9f1a2b3c4d5e6f7g8h9i0j1k2
   ```

4. **COPIA el Client Secret** (es secreto, guarda en .env)
   - Si no lo viste, haz clic en **"Show"**
   - Si lo olvidaste, haz clic en **"Reset"** para generar uno nuevo
   ```
   SHOPIFY_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

---

## PASO 9: Guardar Credenciales en .env

En tu proyecto Next.js, abre o crea el archivo `.env.local`:

```env
# .env.local (NUNCA comitear este archivo)

SHOPIFY_SHOP=calzado-cosmos
SHOPIFY_CLIENT_ID=e7c8d9f1a2b3c4d5e6f7g8h9i0j1k2
SHOPIFY_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## ✅ VERIFICAR QUE FUNCIONA

Desde tu terminal, ejecuta:

```bash
# 1. Verificar que las variables están presentes
npm run build

# 2. Si todo compiló sin errores, está bien configurado
```

Si ves errores como:

- `SHOPIFY_SHOP not configured` → Revisar .env.local
- `Invalid API key or access token` → Client ID/Secret incorrectos

---

## 📋 CHECKLIST FINAL

- [ ] App creada en Dev Dashboard
- [ ] Versión creada con scopes correctos
- [ ] App instalada en tienda
- [ ] Client ID copiado
- [ ] Client Secret copiado
- [ ] Ambos valores guardados en `.env.local`
- [ ] `.env.local` está en `.gitignore`
- [ ] Proyecto compila sin errores

---

## 🔗 Enlaces Útiles

- Dev Dashboard: https://dev.shopify.com/dashboard/
- Shopify Store Admin: https://admin.shopify.com/store/calzado-cosmos/
- GraphQL Explorer: https://shopify.dev/docs/api/admin-graphql
- Documentación Completa: `SHOPIFY_API_2026_SETUP.md`

---

**¿Necesitas ayuda?**

- Lee el archivo `SHOPIFY_API_2026_SETUP.md`
- Revisa `lib/shopify-auth.ts` para ver cómo usar los credentials
- Verifica que `SHOPIFY_SHOP` sea sin "https://" y sin ".myshopify.com"

---

**Última actualización:** 24 de Marzo de 2026
