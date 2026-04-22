# Deploy - Contabilidad

Esta carpeta contiene una base de despliegue separada para Contabilidad.

## Build local

```bash
docker build -f deploy/Dockerfile -t contabilidad-app .
```

## Run local

```bash
docker run --rm -p 8501:8501 \
  -e DB_SERVER=tu_servidor \
  -e DB_PORT=1433 \
  -e DB_NAME=tu_base \
  -e DB_USER=tu_usuario \
  -e DB_PASSWORD=tu_password \
  contabilidad-app
```

## Variables de entorno esperadas

- DB_SERVER
- DB_PORT
- DB_NAME
- DB_USER
- DB_PASSWORD
- DB_VALIDATE_HOST (opcional, por defecto true)

## Recomendaciones de despliegue

- No incluir archivos Excel de operación en la imagen.
- Inyectar secretos desde el proveedor (no desde archivos en git).
- Habilitar health checks sobre el puerto 8501.
