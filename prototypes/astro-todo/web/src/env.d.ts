/// <reference types="astro/client" />

interface ImportMetaEnv {
  readonly PUBLIC_MODULE_NAME: string;
  readonly PUBLIC_PRIMARY_COLOR: string;
  readonly PUBLIC_PRIMARY_DARK: string;
  readonly PUBLIC_API_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare const __MODULE_NAME__: string;
declare const __PRIMARY_COLOR__: string;
declare const __PRIMARY_DARK__: string;
declare const __API_URL__: string;
