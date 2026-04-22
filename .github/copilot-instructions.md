# FYC Calzado - Shopify Analytics Dashboard

## Project Overview

This is a professional, modern ecommerce analytics dashboard for **FYC Calzado** (Colombian footwear company). The application integrates with Shopify to fetch and visualize sales data, metrics, and business insights.

## Technology Stack

- **Framework**: Next.js 15 with App Router
- **UI Library**: React 19
- **Styling**: Tailwind CSS 4
- **Charts**: Recharts
- **Icons**: Lucide React (all SVG)
- **API Client**: Axios
- **Language**: TypeScript
- **Date Handling**: date-fns

## Project Structure

```
src/
├── app/                          # Next.js App Router
│   ├── globals.css              # Global styles with FYC color palette
│   ├── layout.tsx               # Root layout
│   └── page.tsx                 # Home page (Dashboard)
├── components/
│   ├── Dashboard/               # Main dashboard component
│   │   └── Dashboard.tsx        # Dashboard layout and logic
│   ├── Topbar/                  # Top navigation bar
│   │   ├── Topbar.tsx
│   │   └── FYCLogo.tsx          # SVG Logo component
│   ├── Sidebar/                 # Filter sidebar
│   │   └── Sidebar.tsx          # Filters, Shopify connection, grouping
│   ├── KPI/                     # Key Performance Indicators
│   │   └── KPICard.tsx          # Metric cards with trends
│   ├── Charts/                  # Data visualization
│   │   └── Charts.tsx           # Line, Bar, and Donut charts
│   └── Tables/                  # Data tables
│       └── DataTable.tsx        # Top products and recent orders
├── types/
│   └── shopify.ts               # TypeScript interfaces for Shopify data
└── lib/                         # Utilities and helpers (TO BE IMPLEMENTED)
    └── shopify.ts              # Shopify API integration (placeholder)
```

## Key Features

### 1. Dashboard Layout
- **Topbar**: FYC logo, title, user menu
- **Sidebar**: Collapsible filters and Shopify connection
- **Main Content**: KPIs, charts, and data tables

### 2. KPI Cards (4 Main Metrics)
- Total Sales (currency)
- Total Orders (number)
- Average Order Value (currency)
- New Customers (number)
- Trend indicators (% change vs previous period)

### 3. Charts
- **Sales Line Chart**: Sales trends over time
- **Orders Bar Chart**: Orders per period
- **Customers Donut Chart**: New vs returning customers
- **Payment Methods Distribution**

### 4. Data Tables
- Top 10 Products (name, units sold, revenue)
- Recent Orders (order #, customer, total, status, date)

### 5. Filters
- Date range (start/end)
- Product category
- Sales channel
- Order status
- Country/region
- Grouping (day/week/month)

### 6. Shopify Connection
- Store URL input
- Access Token input
- Connection management

## Color Palette

| Element | Color | Hex Code |
|---------|-------|----------|
| Primary (Dark Terracotta) | Main brand color | #8A2F1F |
| Secondary (Warm Brown) | Secondary brand | #7A4F32 |
| Accent (Light Terracotta) | Highlights | #9C4A38 |
| Background | Light neutral | #F7F5F3 |
| Cards | White | #FFFFFF |
| Borders | Light gray | #E4DDD7 |
| Text Primary | Dark gray | #2E2E2E |
| Text Secondary | Medium gray | #6B6B6B |

## Development Guidelines

### Code Style
- Use TypeScript for all components
- Prefer functional components with hooks
- Use `'use client'` for client-side components
- Maintain consistent naming conventions

### Component Guidelines
- All components are in `src/components`
- Organize by feature/section
- Export components from individual files
- Use TypeScript interfaces for props
- Keep components focused and reusable

### Styling
- Use Tailwind CSS classes directly in components
- Follow the FYC color palette (configured in tailwind.config.js)
- Use semantic color names (primary-700, text-secondary, etc.)
- Ensure responsive design (mobile-first approach)

### Icons
- Use only Lucide React (SVG-based)
- No PNG/JPG icons
- All icons are scalable and customizable

## Configuration Files

- **tailwind.config.js**: FYC color palette and custom theme
- **tsconfig.json**: TypeScript configuration with path aliases (@/*)
- **next.config.ts**: Next.js configuration
- **package.json**: Dependencies and scripts
- **.env.local**: Shopify API credentials (create from .env.example)

## Running the Project

```bash
# Development
npm run dev

# Production Build
npm run build
npm start

# Linting
npm run lint
```

## TODO - Not Yet Implemented

1. **Shopify API Integration** (`src/lib/shopify.ts`)
   - Implement GraphQL queries
   - Fetch real sales data
   - Handle authentication
   - Error handling and rate limiting

2. **Data Fetching**
   - Replace mock data with real API calls
   - Implement filtering on backend
   - Add pagination for large datasets
   - Cache strategies

3. **Authentication**
   - Admin login/logout
   - Session management
   - Protected routes

4. **Additional Features**
   - PDF/CSV export functionality
   - Period comparisons
   - Custom date ranges
   - Real-time order notifications
   - Customer segmentation

5. **Analytics**
   - User behavior tracking
   - Performance monitoring
   - Error logging

## Important Notes

- **Mock Data**: Currently using hardcoded mock data for demonstration
- **Environment Variables**: Create `.env.local` based on `.env.example`
- **Shopify Setup**: Requires Shopify store with Admin API access
- **Responsive Design**: Fully responsive, tested on mobile/tablet/desktop
- **Accessibility**: WCAG compliant components (to be enhanced)

## Deployment

Recommended platforms:
- **Vercel** (seamless Next.js integration)
- Netlify
- AWS Amplify
- DigitalOcean App Platform

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Shopify GraphQL Admin API](https://shopify.dev/docs/api/graphql-admin)
- [Recharts Documentation](https://recharts.org)
- [Lucide Icons](https://lucide.dev)

## Support & Maintenance

For questions or issues:
1. Check the README.md for setup instructions
2. Review the component documentation
3. Check Shopify API documentation for integration issues
4. Verify environment variables are correctly configured

---

**Last Updated**: March 2025
**Project Owner**: FYC Calzado
**Status**: Active Development - Mock Data Phase
