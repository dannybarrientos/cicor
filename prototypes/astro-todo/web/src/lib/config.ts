export const MODULE_NAME: string =
  (typeof __MODULE_NAME__ !== "undefined" ? __MODULE_NAME__ : null) ??
  import.meta.env.PUBLIC_MODULE_NAME ??
  "App";

export const PRIMARY_COLOR: string =
  (typeof __PRIMARY_COLOR__ !== "undefined" ? __PRIMARY_COLOR__ : null) ??
  import.meta.env.PUBLIC_PRIMARY_COLOR ??
  "#6366f1";

export const PRIMARY_DARK: string =
  (typeof __PRIMARY_DARK__ !== "undefined" ? __PRIMARY_DARK__ : null) ??
  import.meta.env.PUBLIC_PRIMARY_DARK ??
  "#4f46e5";

export const API_URL: string =
  (typeof __API_URL__ !== "undefined" ? __API_URL__ : null) ??
  import.meta.env.PUBLIC_API_URL ??
  "http://localhost:8000";

export const PAGE_TITLE = `CICOR - Módulo ${MODULE_NAME}`;