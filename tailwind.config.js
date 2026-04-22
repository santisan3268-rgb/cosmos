/** @type {import('tailwindcss').Config} */
const config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // FYC Calzado brand colors
        primary: {
          950: "#5a1f15",
          900: "#6b2319",
          800: "#7a2820",
          700: "#8A2F1F", // Main terracotta dark
          600: "#9c3620",
          500: "#b5431f",
          400: "#c75d3a",
          300: "#d67a54",
          200: "#e5977a",
          100: "#f0b5a0",
          50: "#fae8e0",
        },
        secondary: {
          900: "#5a4028",
          800: "#6a4a30",
          700: "#7A4F32", // Warm brown
          600: "#8b5a3c",
          500: "#9d6847",
          400: "#b07a5a",
          300: "#c28d70",
          200: "#d5a08a",
          100: "#e8bca8",
          50: "#f5e4d2",
        },
        accent: {
          500: "#9C4A38", // Terracotta light
          400: "#b05d4a",
          300: "#c5755f",
          200: "#e0a099",
          100: "#f0c5ba",
        },
        background: {
          primary: "#F7F5F3", // Light neutral gray
          secondary: "#FFFFFF",
          tertiary: "#f0ebe5",
        },
        border: {
          light: "#E4DDD7",
          DEFAULT: "#d9cfca",
          dark: "#c5b5a8",
        },
        text: {
          primary: "#2E2E2E",
          secondary: "#6B6B6B",
          tertiary: "#999999",
        },
      },
      backgroundColor: {
        card: "#FFFFFF",
      },
      textColor: {
        primary: "#2E2E2E",
        secondary: "#6B6B6B",
      },
      borderColor: {
        DEFAULT: "#E4DDD7",
      },
      boxShadow: {
        sm: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
        DEFAULT: "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
        md: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        lg: "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
      },
    },
  },
  plugins: [],
};

export default config;
