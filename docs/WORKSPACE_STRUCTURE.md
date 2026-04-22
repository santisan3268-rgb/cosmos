# Estructura separada de proyectos y despliegue

## Contabilidad

```text
Contabilidad/
  app.py
  sql_horas_app.py
  conta_core/
    parser_utils.py
    sql_utils.py
    export_utils.py
  tests/
    test_parser_utils.py
    test_sql_utils.py
    test_export_utils.py
  scripts/
    run_quality_checks.ps1
    rotate_db_secrets.ps1
  deploy/
    Dockerfile
    .dockerignore
    README.md
  requirements.txt
  DEPLOYMENT.md
```

## Ecommerce

```text
Ecommerce/
  src/
  public/
  scripts/
    rotate_shopify_secrets.ps1
  .github/
    workflows/
      ci.yml
  deploy/
    Dockerfile
    .dockerignore
    README.md
  next.config.ts
  package.json
  package-lock.json
  tsconfig.json
```

## Preparacion para despliegue

1. Contabilidad: construir imagen con `deploy/Dockerfile` y pasar credenciales SQL por variables de entorno.
2. Ecommerce: construir imagen con `deploy/Dockerfile`, usa salida standalone de Next.js y variables de Shopify por entorno.
3. CI: Ecommerce ya tiene workflow de validacion continua en `.github/workflows/ci.yml`.
