# Runbook de despliegue

## 1. Pre-requisitos

- Node.js 20+ recomendado.
- Proyecto instalado con `npm ci`.
- Variables de entorno configuradas.

## 2. Variables de entorno

Configurar en el proveedor (Vercel u otro):

- `SHOPIFY_STORE_URL` o `SHOPIFY_SHOP`
- `SHOPIFY_CLIENT_ID`
- `SHOPIFY_CLIENT_SECRET`
- `SHOPIFY_SCOPES` (opcional)
- `SHOPIFY_DEBUG` (opcional)

Compatibilidad legacy opcional:

- `SHOPIFY_ACCESS_TOKEN` (solo si no se usa client credentials).

Scopes recomendados para este dashboard:

- `read_orders`
- `read_products`
- `read_customers`
- `read_analytics`
- `read_reports`

## 3. Validaciones locales obligatorias

1. Instalar dependencias:

```bash
npm ci
```

2. Build de produccion:

```bash
npm run build
```

3. Lint (puede fallar actualmente por deuda tecnica conocida):

```bash
npm run lint
```

## 4. Procedimiento de despliegue (Vercel)

1. Conectar repositorio a Vercel.
2. Definir variables de entorno del punto 2.
3. Configurar comando de build: `npm run build`.
4. Configurar comando de inicio: `npm run start`.
5. Desplegar.

## 5. Smoke tests post-deploy

1. Cargar home dashboard y validar render sin errores.
2. Probar endpoint de proxy Shopify:

```bash
curl -X POST https://<tu-dominio>/api/shopify \
  -H "Content-Type: application/json" \
  -d '{"query":"query { shop { name } }"}'
```

3. Validar KPI "Ventas totales" para un rango conocido vs Shopify Admin.
4. Validar que no aparezca `#NaN` en ordenes recientes.
5. Validar filtros por fecha y canal.

## 6. Rollback

Si el dashboard falla tras deploy:

1. Revertir a la version anterior estable en Vercel.
2. Verificar variables de entorno y scopes de la app Shopify.
3. Revisar logs de funcion en `/api/shopify`.
4. Reintentar deploy una vez corregido el incidente.

## 7. Criterios de salida

- Build verde en CI/CD.
- Endpoint `/api/shopify` respondiendo.
- KPIs principales coherentes con Shopify Admin para rango de control.
- Sin errores bloqueantes en navegador.
