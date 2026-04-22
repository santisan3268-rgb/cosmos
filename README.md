# FYC Calzado - Dashboard de Shopify Analytics

## Estado actual (2026-03-25)

- Build de produccion validado con `npm run build`.
- Auditoria tecnica y riesgos: ver `docs/AUDITORIA_DESPLIEGUE_2026-03-25.md`.
- Procedimiento de despliegue paso a paso: ver `docs/RUNBOOK_DESPLIEGUE.md`.
- Nota: el lint aun reporta deuda tecnica pendiente (ver auditoria).

Dashboard profesional de análisis de ventas para FYC Calzado, construido con **React**, **Next.js** y **Tailwind CSS**. Conecta directamente a la API de Shopify para traer datos en tiempo real.

## 🎯 Características

- **Integración con Shopify API**: Conexión directa para obtener datos de ventas, órdenes y clientes
- **Dashboard responsivo**: Diseño moderno y limpio que se adapta a cualquier dispositivo
- **KPIs en tiempo real**: Visualización de métricas clave (ventas, órdenes, ticket promedio, clientes nuevos)
- **Gráficos interactivos**: Tendencias de ventas, análisis de órdenes, distribución de clientes
- **Filtros avanzados**: Por rango de fechas, categoría, canal, estado de pedido y región
- **Tablas de datos**: Productos más vendidos y órdenes recientes
- **Paleta de colores personalizada**: Identidad visual de FYC Calzado (terracota y marrón)
- **Iconos SVG**: Todos los iconos son vectoriales escalables

## 🛠️ Stack Tecnológico

- **Frontend**: React 19 + Next.js 15 (App Router)
- **Styling**: Tailwind CSS 4
- **Gráficos**: Recharts
- **Iconos**: Lucide React
- **API Client**: Axios
- **Fechas**: date-fns
- **Lenguaje**: TypeScript

## 📋 Requisitos Previos

- Node.js 18.17 o superior
- npm, yarn, pnpm o bun
- Acceso a Shopify Store y Access Token

## 🚀 Instalación y Setup

### 1. Obtener credenciales de Shopify

Para conectar el dashboard a tu tienda Shopify:

1. Ve a tu **tienda Shopify** → **Configuración**
2. En el sidebar, ve a **Aplicaciones y integraciones** → **Apps y sales channels**
3. En la esquina superior derecha, haz clic en **Crear una app**
4. Dale un nombre a tu app (ej: "FYC Dashboard")
5. Selecciona **Admin APIs** si quieres acceso administrativo
6. Genera un **Access Token**

**Importante**: Guarda tu Access Token en un lugar seguro. No lo compartas públicamente.

Los endpoints de la API serán:

```
https://[TU_TIENDA].myshopify.com/api/2024-01/graphql.json
```

### 2. Instalación

```bash
# Clonar o descargar el proyecto
cd ecommerce

# Instalar dependencias
npm install
```

### 3. Configurar variables de entorno

Crea un archivo `.env.local` en la raíz del proyecto:

```env
NEXT_PUBLIC_SHOPIFY_STORE_URL=tu-tienda.myshopify.com
NEXT_PUBLIC_SHOPIFY_ACCESS_TOKEN=tu-access-token-aqui
```

### 4. Ejecutar en desarrollo

```bash
npm run dev
```

Abre [http://localhost:3000](http://localhost:3000) en tu navegador para ver el dashboard.

### 5. Build para producción

```bash
npm run build
npm start
```

## 📊 Estructura del Proyecto

```
src/
├── app/
│   ├── globals.css              # Estilos globales
│   ├── layout.tsx               # Layout base
│   └── page.tsx                 # Página principal
├── components/
│   ├── Dashboard/               # Componente principal del dashboard
│   ├── Topbar/                  # Barra superior con logo y usuario
│   ├── Sidebar/                 # Sidebar con filtros
│   ├── KPI/                     # Tarjetas de métricas principales
│   ├── Charts/                  # Componentes de gráficos (línea, barras, dona)
│   └── Tables/                  # Tablas de datos (productos, órdenes)
├── types/
│   └── shopify.ts               # Definiciones TypeScript para datos de Shopify
└── lib/
    └── [...utils]               # Utilidades y funciones helper
```

## 🎨 Paleta de Colores

La aplicación utiliza la identidad visual de FYC Calzado:

- **Color Principal**: `#8A2F1F` (Terracota oscuro)
- **Color Secundario**: `#7A4F32` (Marrón cálido)
- **Color de Acento**: `#9C4A38` (Terracota claro)
- **Fondo General**: `#F7F5F3` (Gris claro neutro)
- **Tarjetas**: `#FFFFFF` (Blanco)
- **Texto Principal**: `#2E2E2E` (Gris oscuro)
- **Texto Secundario**: `#6B6B6B` (Gris medio)

## 📱 Secciones del Dashboard

### 1. **Topbar**

- Logo y nombre de la empresa
- Título: "FYC Calzado - Shopify Analytics"
- Icono de usuario/administrador

### 2. **Sidebar (Colapsable)**

- **Conexión Shopify**: Ingreso de credenciales
- **Filtros**:
  - Rango de fechas
  - Categoría de producto
  - Canal de venta
  - Estado del pedido
  - País/Región
- **Agrupación**: Por día, semana o mes

### 3. **KPIs Principales** (4 tarjetas)

- Ventas totales
- Número de órdenes
- Ticket promedio (AOV)
- Clientes nuevos

### 4. **Gráficos**

- **Tendencia de ventas**: Gráfico de línea mostrando ventas vs órdenes
- **Órdenes por período**: Gráfico de barras
- **Clientes nuevos vs recurrentes**: Gráfico de dona

### 5. **Métricas Adicionales**

- Abandono de carrito
- Tasa de devolución
- Tasa de conversión
- Métodos de pago con gráfico de distribución

### 6. **Tablas**

- **Top 10 Productos**: Nombre, unidades vendidas, ingresos
- **Órdenes Recientes**: ID, cliente, total, estado, fecha

## 🔄 Integración con Shopify API

El proyecto está preparado para conectarse a Shopify GraphQL API.

### Ejemplo de configuración:

```typescript
// En src/lib/shopify.ts (crear este archivo)
const SHOPIFY_ENDPOINT = `https://${store}.myshopify.com/api/2024-01/graphql.json`;

const headers = {
  "Content-Type": "application/json",
  "X-Shopify-Access-Token": accessToken,
};

// Queries de ejemplo para obtener datos
const SALES_QUERY = `
  query {
    orders(first: 100) {
      edges {
        node {
          id
          name
          totalPriceSet {
            shopMoney {
              amount
            }
          }
          createdAt
        }
      }
    }
  }
`;
```

## 🎯 Próximos Pasos

1. Implementar funciones reales de Shopify API en `src/lib/shopify.ts`
2. Conectar los datos mock con datos reales
3. Agregar autenticación de administrador
4. Implementar exportación de reportes (PDF/CSV)
5. Agregar comparativas de períodos
6. Notificaciones en tiempo real de órdenes

## 📝 Notas de Desarrollo

- Las métricas actuales son **datos de demostración (mock)**
- Necesitas implementar las llamadas a la API de Shopify en `src/lib/shopify.ts`
- Todos los iconos son **SVG vectoriales** (desde Lucide React)
- El diseño es **responsive** (funciona en mobile, tablet y desktop)
- Se usan **animaciones suaves** y **hover states** para mejor UX

## 🔐 Seguridad

⚠️ **IMPORTANTE**:

- Nunca hagas commit de archivos `.env.local` a git
- Usa variables de entorno para almacenar Access Tokens
- Considera usar OAuth 2.0 para producción
- Añade validación y sanitización de datos

## 📦 Deployment

### Vercel (Recomendado)

```bash
npm install -g vercel
vercel
```

### Otros servicios

- Netlify
- AWS Amplify
- DigitalOcean
- Heroku

## 📞 Soporte

Para más información sobre Shopify API:

- [Documentación de Shopify GraphQL](https://shopify.dev/docs/api/graphql-admin)
- [Shopify REST API](https://shopify.dev/docs/api/rest)

## 📄 Licencia

Este proyecto es propiedad de FYC Calzado.

---

**Construido con ❤️ para FYC Calzado**

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
