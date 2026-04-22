# Auditoria tecnica y de despliegue

Fecha: 2026-03-25
Proyecto: FYC Calzado Shopify Analytics Dashboard

## Resumen ejecutivo

- Estado de build de produccion: APROBADO.
- Estado de lint: RECHAZADO (23 errores, 9 warnings).
- Estado de integracion ShopifyQL oficial: APROBADO con fallback.
- Riesgo global para despliegue: MEDIO.

## Evidencia de validacion

- `npm run build`: exitoso.
- `npm run lint`: falla con 32 hallazgos (23 errores, 9 warnings).

## Hallazgos (ordenados por severidad)

### Critico

1. React immutability en render

- Archivo: `src/components/Dashboard/Dashboard.tsx`
- Linea reportada: 471
- Hallazgo: reasignacion de `cumulativeTarget` dentro de flujo de render.
- Riesgo: comportamiento inconsistente en renders futuros.
- Recomendacion: reemplazar acumulacion mutable por `reduce` o acumulado inmutable por indice.

### Alto

1. Uso extensivo de `any` en capa de datos Shopify

- Archivos principales:
  - `src/lib/shopify.ts`
  - `src/lib/hooks.ts`
  - `lib/shopify-auth.ts`
- Hallazgo: `@typescript-eslint/no-explicit-any` en multiples puntos.
- Riesgo: perdida de seguridad de tipos en datos financieros y de ordenes.
- Recomendacion: tipar respuestas GraphQL por query (interfaces dedicadas) y eliminar `any` progresivamente por dominio.

### Medio

1. Variables y simbolos no usados

- Archivos principales:
  - `src/components/Dashboard/Dashboard.tsx`
  - `src/features/dashboard/hooks/useDashboard.ts`
  - `src/lib/hooks.ts`
  - `src/lib/shopify.ts`
- Riesgo: deuda tecnica y menor mantenibilidad.
- Recomendacion: limpieza y simplificacion en una pasada de refactor.

2. Export anonimo en configuracion Tailwind

- Archivo: `tailwind.config.js`
- Hallazgo: warning `import/no-anonymous-default-export`.
- Riesgo: bajo, pero afecta estandar de lint.
- Recomendacion: exportar mediante constante nombrada.

## Hallazgos resueltos en esta sesion

1. Build bloqueado por typing de tooltip (Recharts)

- Resuelto en: `src/components/Charts/Charts.tsx`
- Resultado: tipado compatible y build continuo.

2. Build bloqueado por variante invalida de Badge

- Resuelto en: `src/components/Dashboard/Dashboard.tsx`
- Cambio: `variant="default"` a `variant="neutral"`.

3. Build bloqueado por tipo de estado en ordenes recientes

- Resuelto en: `src/components/Tables/DataTable.tsx`
- Cambio: soporte de `canceled` y `cancelled`.

4. Build bloqueado por inferencia de tipos en variables GraphQL

- Resuelto en: `src/lib/shopify.ts`
- Cambio: anotaciones explicitas para `variables`.

5. Build bloqueado por llamada con firma invalida a `getCustomers`

- Resuelto en: `src/lib/hooks.ts`
- Cambio: llamado actualizado a `getCustomers()`.

## Estado de paridad Shopify

- `shopifyqlQuery` funcional con dataset `FROM sales`.
- Columna de envio valida: `shipping_charges`.
- Parser adaptado a `tableData.rows` (sin `rowData` en este schema).
- Fallback local permanece activo cuando ShopifyQL no aplica (filtros avanzados o error remoto).

## Recomendacion de aprobacion para despliegue

- Aprobado condicional para despliegue controlado, con estas condiciones:
  1. Mantener monitoreo post-deploy de KPIs de ventas.
  2. Abrir task de remediacion de lint como prioridad alta.
  3. Validar en entorno productivo el mismo rango de fechas contra Shopify Admin.

## Backlog de remediacion post-deploy (priorizado)

1. Corregir `react-hooks/immutability` en Dashboard (critico de lint).
2. Eliminar `any` en capa Shopify y hooks.
3. Limpiar variables no usadas.
4. Normalizar configuracion Tailwind para lint limpio.
