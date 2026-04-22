# Deploy - Ecommerce

Esta carpeta contiene una base de despliegue separada para Ecommerce.

## Requisito previo

El proyecto usa salida standalone de Next.js para despliegue en contenedor.

## Build local

```bash
docker build -f deploy/Dockerfile -t ecommerce-app .
```

## Run local

```bash
docker run --rm -p 3000:3000 \
  -e NODE_ENV=production \
  -e NEXT_PUBLIC_SHOPIFY_STORE_DOMAIN=tu-dominio \
  -e SHOPIFY_STOREFRONT_ACCESS_TOKEN=tu-token \
  ecommerce-app
```

## Variables de entorno mínimas

- NEXT_PUBLIC_SHOPIFY_STORE_DOMAIN
- SHOPIFY_STOREFRONT_ACCESS_TOKEN

## Recomendaciones de despliegue

- Mantener `.env.local` fuera de git.
- Inyectar secretos desde el entorno del proveedor.
- Configurar health check sobre `/` en puerto 3000.
