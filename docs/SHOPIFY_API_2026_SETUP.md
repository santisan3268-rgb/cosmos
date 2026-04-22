# Crear Custom App en Shopify 2026 - Guía Actualizada

## ⚠️ CAMBIO IMPORTANTE (Enero 2026)

**A partir del 1 de enero de 2026, Shopify cambió completamente el flujo para crear custom apps.**

- ❌ **YA NO SE PUEDEN crear nuevas "legacy custom apps"** (las que generaban tokens `shpat_...`)
- ✅ **Las custom apps ANTIGUAS (creadas antes del 1 de enero 2026) siguen funcionando**
- ✅ **El nuevo flujo es a través del DEV DASHBOARD**

---

## Opción 1: NUEVO FLUJO (Recomendado para 2026+)

### Crear Custom App en Dev Dashboard

**Ubicación:** https://dev.shopify.com/dashboard

#### Paso 1: Acceder al Dev Dashboard

Tienes 2 formas:

**Opción A - Desde tu admin de Shopify:**

1. Inicia sesión en `admin.shopify.com/store/[tu-store]/`
2. Haz clic en tu nombre de tienda (arriba a la derecha)
3. Selecciona **"Dev Dashboard"**

**Opción B - Acceso directo:**

- Ve a https://dev.shopify.com/dashboard/

#### Paso 2: Crear la App

1. En el panel izquierdo, asegúrate de estar en **"Apps"**
2. Haz clic en **"Create app"** (arriba a la derecha)
3. Selecciona **"Start from Dev Dashboard"**
4. Nombra tu app (ej: "FYC Calzado Analytics")
5. Haz clic en **"Create"**

#### Paso 3: Crear una Versión

La app necesita al menos una versión antes de instalarla:

1. Ve a la pestaña **"Versions"** de tu app
2. Completa los campos:
   - **App URL**: Si tu app no está embebida en el admin de Shopify (como un dashboard Next.js):
     ```
     https://shopify.dev/apps/default-app-home
     ```
   - **Webhooks API Version**: Selecciona la más reciente (ej: `2026-01`)
   - **Access Scopes**: Selecciona los permisos que necesitas

#### Paso 4: Configurar Permisos (Scopes)

Para un dashboard de analytics, necesitarás estos permisos mínimo:

| Permiso             | Necesario para         | Formato        |
| ------------------- | ---------------------- | -------------- |
| `read_orders`       | Leer órdenes           | ✅ Sí          |
| `read_products`     | Leer productos         | ✅ Sí          |
| `read_customers`    | Leer datos de clientes | ✅ Sí          |
| `read_orders`       | Datos de órdenes       | ✅ Sí          |
| `read_analytics`    | Métricas de tienda     | ✅ Recomendado |
| `read_inventory`    | Niveles de inventario  | Opcional       |
| `read_fulfillments` | Estados de envío       | Opcional       |

**Ejemplo en formato TOML (si usas Shopify CLI):**

```toml
scopes = "write_orders,read_orders,read_customers,read_products,read_analytics"
```

#### Paso 5: Liberar la Versión

1. Haz clic en **"Release"**
2. Escribe opcionalmente un nombre y descripción de la versión
3. Haz clic en **"Release"** nuevamente

#### Paso 6: Instalar la App

1. Desde tu app en el Dev Dashboard, haz clic en **"Home"**
2. Desplázate hacia abajo y haz clic en **"Install app"**
3. Selecciona o crea la tienda donde instalarla
4. Haz clic en **"Install"**

#### Paso 7: Obtener Credenciales (Client ID y Secret)

**Aquí está la diferencia clave con las legacy apps:**

- ❌ NO hay un token visible llamado `shpat_...`
- ✅ Recibirás **Client ID** y **Client Secret** en lugar de un token directo

Pasos:

1. En tu app del Dev Dashboard, haz clic en **"Settings"**
2. En la sección de seguridad, verás:
   - **Client ID** (copiar)
   - **Client Secret** (copiar y guardar en `.env`)

---

## Opción 2: FLUJO HEREDADO (Solo si tienes apps antiguas)

Si habías creado custom apps ANTES del 1 de enero de 2026, aún puedes gestionarlas:

**Ubicación:** `admin.shopify.com/store/[tu-store]/settings/apps/development`

En esa página verás:

- Tus apps heredadas existentes
- Un aviso diciendo "A partir del 1 de enero de 2026, ya no podrás crear nuevas apps personalizadas heredadas"
- Las apps existentes siguen funcionando y pueden gestionarse

---

## Paso 8: Generar Access Token Programáticamente

**IMPORTANTE:** Con el nuevo flujo del Dev Dashboard, los tokens NO se generan en la interfaz. Tu código debe generarlos usando **Client Credentials Grant**.

### Flujo de Autenticación: Client Credentials Grant

#### 8.1 - Crear archivo `.env`

```env
SHOPIFY_SHOP=tu-tienda
SHOPIFY_CLIENT_ID=tu-client-id-aqui
SHOPIFY_CLIENT_SECRET=tu-client-secret-aqui
```

#### 8.2 - Código para obtener Access Token (Node.js/JavaScript)

```javascript
import { URLSearchParams } from "url";

const SHOP = process.env.SHOPIFY_SHOP;
const CLIENT_ID = process.env.SHOPIFY_CLIENT_ID;
const CLIENT_SECRET = process.env.SHOPIFY_CLIENT_SECRET;

let token = null;
let tokenExpiresAt = 0;

async function getAccessToken() {
  // Reutilizar token si aún es válido
  if (token && Date.now() < tokenExpiresAt - 60_000) {
    return token;
  }

  const response = await fetch(
    `https://${SHOP}.myshopify.com/admin/oauth/access_token`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        grant_type: "client_credentials",
        client_id: CLIENT_ID,
        client_secret: CLIENT_SECRET,
        scope: "read_orders,read_products,read_customers",
      }).toString(),
    },
  );

  if (!response.ok) {
    throw new Error(`Error: ${response.statusText}`);
  }

  const data = await response.json();

  token = data.access_token;
  // Los tokens expiran en 24 horas (86400 segundos)
  tokenExpiresAt = Date.now() + data.expires_in * 1000;

  console.log(`✅ Token obtenido, expira en: ${new Date(tokenExpiresAt)}`);
  return token;
}

export { getAccessToken };
```

#### 8.3 - Usar el Token para Queries GraphQL

```javascript
async function queryShopifyAPI(query, variables = {}) {
  const accessToken = await getAccessToken();

  const response = await fetch(
    `https://${SHOP}.myshopify.com/admin/api/2026-01/graphql.json`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": accessToken,
      },
      body: JSON.stringify({
        query,
        variables,
      }),
    },
  );

  const data = await response.json();

  if (data.errors) {
    console.error("GraphQL Errors:", data.errors);
    throw new Error(data.errors[0].message);
  }

  return data.data;
}

// Ejemplo: obtener productos
const productsQuery = `
  query {
    products(first: 10) {
      edges {
        node {
          id
          title
          handle
        }
      }
    }
  }
`;

const products = await queryShopifyAPI(productsQuery);
console.log(products);
```

---

## Resumen de Diferencias: Antes vs. Después (2026)

| Aspecto                          | Legacy Custom Apps (❌ Deprecadas)                | Dev Dashboard Apps (✅ Nueva)                     |
| -------------------------------- | ------------------------------------------------- | ------------------------------------------------- |
| **Ubicación**                    | Admin → Settings → Apps & channels → Develop apps | dev.shopify.com/dashboard                         |
| **Token Format**                 | `shpat_...` (visible en UI)                       | Client ID + Secret (generan tokens dinámicamente) |
| **Vigencia Token**               | No expiraban                                      | 24 horas (auto-renovable)                         |
| **Creación**                     | En el admin de Shopify                            | En Dev Dashboard                                  |
| **Nuevas apps desde 1 Ene 2026** | ❌ No permitidas                                  | ✅ Única opción                                   |
| **Apps antiguas**                | ✅ Siguen funcionando                             | N/A                                               |

---

## Permisos Necesarios por Función

Para **FYC Calzado Analytics Dashboard**:

```
read_orders        - Leer órdenes ✅ CRÍTICO
read_customers     - Leer clientes ✅ CRÍTICO
read_products      - Leer catálogo ✅ CRÍTICO
read_analytics     - KPIs y métricas ✅ RECOMENDADO
read_inventory     - Stock por ubicación (Opcional)
read_fulfillments  - Estado de envíos (Opcional)
```

---

## Troubleshooting

### Error: "app_not_installed"

**Causa:** La app no está instalada en la tienda
**Solución:** Repite Paso 6 (Install the app)

### Error: "shop_not_permitted"

**Causa:** Los credentials están mal configurados
**Solución:**

1. Verifica Client ID y Secret en Settings
2. Asegúrate de que el SHOPIFY_SHOP es correcto (sin `https://`, solo `tu-tienda`)

### Token expira constantemente

**Causa:** Es normal, los tokens duran 24 horas
**Solución:** El código debe manejar renovación automática (ver Paso 8.2)

### "Invalid API key or access token"

**Causa:** Token expirado o inválido
**Solución:** El código de Paso 8.2 maneja esto automáticamente

---

## Recursos Oficiales

- 📚 [Shopify Dev Dashboard Docs](https://shopify.dev/docs/apps/build/dev-dashboard)
- 📚 [Crear Apps en Dev Dashboard](https://shopify.dev/docs/apps/build/dev-dashboard/create-apps-using-dev-dashboard)
- 📚 [Client Credentials Grant](https://shopify.dev/docs/apps/build/authentication-authorization/access-tokens/client-credentials-grant)
- 📚 [GraphQL Admin API Reference](https://shopify.dev/docs/api/admin-graphql)
- 📚 [Access Scopes](https://shopify.dev/docs/api/usage/access-scopes)

---

## Próximos Pasos para FYC Calzado

1. ✅ Crear app en Dev Dashboard
2. ✅ Configurar permisos (read_orders, read_products, read_customers, read_analytics)
3. ✅ Instalar app
4. ✅ Obtener Client ID y Secret
5. ✅ Implementar client credentials grant en Next.js
6. ✅ Conectar queries GraphQL al dashboard
7. ✅ Reemplazar mock data con datos reales

---

**Última actualización:** 24 de Marzo de 2026
**Estado:** Investigación completada y documentada
