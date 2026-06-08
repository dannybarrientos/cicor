// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite'

import preact from '@astrojs/preact';

// https://astro.build/config
export default defineConfig({
  vite: {
    plugins: [tailwindcss()],
    define: {
      // Expose env vars to client-side code at build time
      __MODULE_NAME__: JSON.stringify(process.env.PUBLIC_MODULE_NAME ?? "App"),
      __PRIMARY_COLOR__: JSON.stringify(process.env.PUBLIC_PRIMARY_COLOR ?? "#6366f1"),
      __PRIMARY_DARK__: JSON.stringify(process.env.PUBLIC_PRIMARY_DARK ?? "#4f46e5"),
      __API_URL__: JSON.stringify(process.env.PUBLIC_API_URL ?? "http://localhost:8000"),
    },
  },
  integrations: [preact()]
});