import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f3f8f6",
          100: "#d8eae4",
          600: "#2f6f63",
          700: "#275a51",
          900: "#173631"
        }
      }
    }
  },
  plugins: []
};

export default config;
