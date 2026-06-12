# 🎨 CICOR ERP — Especificación de Colores y Diseño

> Guía visual completa del sistema de diseño de CICOR ERP: paleta corporativa, colores por módulo, uso en componentes, configuración de Tailwind CSS y ejemplos de aplicación.

---

## Índice

- [Filosofía de Diseño](#filosofía-de-diseño)
- [Paleta Corporativa CICOR](#paleta-corporativa-cicor)
- [Colores por Módulo](#colores-por-módulo)
- [Configuración Tailwind CSS](#configuración-tailwind-css)
- [Sistema de Componentes](#sistema-de-componentes)
- [Uso de Color por Componente](#uso-de-color-por-componente)
- [Tipografía](#tipografía)
- [Espaciado y Layout](#espaciado-y-layout)
- [Referencia Rápida](#referencia-rápida)

---

## Filosofía de Diseño

CICOR ERP utiliza un sistema de diseño **dual**:

1. **Identidad corporativa** — colores azules para la estructura global (navbar, headers, botones primarios)
2. **Identidad modular** — cada uno de los 5 módulos tiene un color propio que lo identifica de forma consistente en toda la UI: badges, bordes, botones de acción, iconos y fondos de sección

Esta separación permite que el usuario sepa instantáneamente en qué módulo se encuentra, sin necesidad de leer el título de la página.

---

## Paleta Corporativa CICOR

| Token            | Hex       | Uso principal                                  | Vista previa      |
|:-----------------|:----------|:-----------------------------------------------|:------------------|
| `cicor-primary`  | `#1E40AF` | Navbar, headers de página, botones primarios   | 🟦 Azul corporativo |
| `cicor-light`    | `#DBEAFE` | Fondos de sección, backgrounds suaves          | 🩵 Azul claro       |
| `cicor-dark`     | `#0C1E4D` | Footer, textos de alto contraste, hover navbar | 🔵 Azul oscuro      |

### Escala completa de azules corporativos

Basada en la escala Tailwind `blue`, con los tokens personalizados mapeados a:

| Token           | Equivalente Tailwind | Hex       |
|:----------------|:---------------------|:----------|
| `cicor-dark`    | `blue-950`           | `#0C1E4D` |
| `cicor-primary` | `blue-800`           | `#1E40AF` |
| —               | `blue-700`           | `#1D4ED8` |
| —               | `blue-600`           | `#2563EB` |
| —               | `blue-500`           | `#3B82F6` |
| —               | `blue-200`           | `#BFDBFE` |
| `cicor-light`   | `blue-100`           | `#DBEAFE` |
| —               | `blue-50`            | `#EFF6FF` |

---

## Colores por Módulo

Cada módulo tiene asignado un **color primario** para su identificación visual, más variantes claras (background de tarjetas) y oscuras (hover, texto en badges).

### 🟢 Módulo Comercial — Verde Esmeralda

| Variante       | Hex       | Clase Tailwind       | Uso                                   |
|:---------------|:----------|:---------------------|:--------------------------------------|
| **Primario**   | `#10B981` | `emerald-500`        | Botones, badges, bordes activos       |
| Oscuro (hover) | `#059669` | `emerald-600`        | Hover de botones, iconos en texto     |
| Claro (bg)     | `#D1FAE5` | `emerald-100`        | Background de tarjetas, header módulo |
| Muy claro      | `#ECFDF5` | `emerald-50`         | Background de fila activa en tabla    |
| Texto sobre bg | `#065F46` | `emerald-800`        | Texto en badges, labels               |

```css
/* Ejemplo de uso en tarjeta de módulo Comercial */
.card-commercial {
  background-color: #ECFDF5;   /* emerald-50 */
  border-left: 4px solid #10B981; /* emerald-500 */
}

.badge-commercial {
  background-color: #D1FAE5;   /* emerald-100 */
  color: #065F46;              /* emerald-800 */
}

.btn-commercial {
  background-color: #10B981;   /* emerald-500 */
  color: white;
}
.btn-commercial:hover {
  background-color: #059669;   /* emerald-600 */
}
```

---

### 🔵 Módulo Inventario — Azul

| Variante       | Hex       | Clase Tailwind  | Uso                                   |
|:---------------|:----------|:----------------|:--------------------------------------|
| **Primario**   | `#3B82F6` | `blue-500`      | Botones, badges, bordes activos       |
| Oscuro (hover) | `#2563EB` | `blue-600`      | Hover de botones                      |
| Claro (bg)     | `#DBEAFE` | `blue-100`      | Background de tarjetas                |
| Muy claro      | `#EFF6FF` | `blue-50`       | Background de fila activa en tabla    |
| Texto sobre bg | `#1E40AF` | `blue-800`      | Texto en badges (coincide con `cicor-primary`) |

> **Nota:** El azul de Inventario (`blue-500`) es deliberadamente diferente al azul corporativo (`blue-800`). El corporativo es más oscuro y se usa para navegación global; el de Inventario es más brillante y se usa solo dentro del módulo.

---

### 🔴 Módulo Contabilidad — Rojo

| Variante       | Hex       | Clase Tailwind | Uso                                   |
|:---------------|:----------|:---------------|:--------------------------------------|
| **Primario**   | `#EF4444` | `red-500`      | Botones, badges, bordes activos       |
| Oscuro (hover) | `#DC2626` | `red-600`      | Hover de botones                      |
| Claro (bg)     | `#FEE2E2` | `red-100`      | Background de tarjetas                |
| Muy claro      | `#FEF2F2` | `red-50`       | Background de fila activa             |
| Texto sobre bg | `#991B1B` | `red-800`      | Texto en badges                       |

> El rojo de Contabilidad no debe confundirse con mensajes de error (que usan `red-600` + ícono ⚠️). Los contextos de módulo usan siempre el fondo claro (`red-50`) para evitar alarmar al usuario.

---

### 🟠 Módulo Operaciones — Naranja

| Variante       | Hex       | Clase Tailwind  | Uso                                   |
|:---------------|:----------|:----------------|:--------------------------------------|
| **Primario**   | `#F97316` | `orange-500`    | Botones, badges, bordes activos       |
| Oscuro (hover) | `#EA580C` | `orange-600`    | Hover de botones                      |
| Claro (bg)     | `#FFEDD5` | `orange-100`    | Background de tarjetas                |
| Muy claro      | `#FFF7ED` | `orange-50`     | Background de fila activa             |
| Texto sobre bg | `#9A3412` | `orange-800`    | Texto en badges                       |

---

### 🟣 Módulo RRHH — Púrpura

| Variante       | Hex       | Clase Tailwind   | Uso                                   |
|:---------------|:----------|:-----------------|:--------------------------------------|
| **Primario**   | `#A855F7` | `purple-500`     | Botones, badges, bordes activos       |
| Oscuro (hover) | `#9333EA` | `purple-600`     | Hover de botones                      |
| Claro (bg)     | `#F3E8FF` | `purple-100`     | Background de tarjetas                |
| Muy claro      | `#FAF5FF` | `purple-50`      | Background de fila activa             |
| Texto sobre bg | `#6B21A8` | `purple-800`     | Texto en badges                       |

---

## Configuración Tailwind CSS

Agrega esta configuración en `frontend/tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // ── Identidad Corporativa CICOR ─────────────────────────
        cicor: {
          primary: '#1E40AF',   // Azul corporativo (navbar, botones primarios)
          light:   '#DBEAFE',   // Azul claro (backgrounds suaves)
          dark:    '#0C1E4D',   // Azul oscuro (footer, hover navbar)
        },
        // ── Colores por Módulo ───────────────────────────────────
        commercial: {
          DEFAULT: '#10B981',   // emerald-500
          hover:   '#059669',   // emerald-600
          light:   '#D1FAE5',   // emerald-100
          bg:      '#ECFDF5',   // emerald-50
          text:    '#065F46',   // emerald-800
        },
        inventory: {
          DEFAULT: '#3B82F6',   // blue-500
          hover:   '#2563EB',   // blue-600
          light:   '#DBEAFE',   // blue-100
          bg:      '#EFF6FF',   // blue-50
          text:    '#1E40AF',   // blue-800
        },
        accounting: {
          DEFAULT: '#EF4444',   // red-500
          hover:   '#DC2626',   // red-600
          light:   '#FEE2E2',   // red-100
          bg:      '#FEF2F2',   // red-50
          text:    '#991B1B',   // red-800
        },
        operations: {
          DEFAULT: '#F97316',   // orange-500
          hover:   '#EA580C',   // orange-600
          light:   '#FFEDD5',   // orange-100
          bg:      '#FFF7ED',   // orange-50
          text:    '#9A3412',   // orange-800
        },
        hr: {
          DEFAULT: '#A855F7',   // purple-500
          hover:   '#9333EA',   // purple-600
          light:   '#F3E8FF',   // purple-100
          bg:      '#FAF5FF',   // purple-50
          text:    '#6B21A8',   // purple-800
        },
      },
    },
  },
  plugins: [],
}
```

### Clases Tailwind generadas por la config

Con esta configuración puedes usar en JSX:

```jsx
// Botón del módulo Comercial
<button className="bg-commercial hover:bg-commercial-hover text-white px-4 py-2 rounded">
  Crear Venta
</button>

// Badge de estado
<span className="bg-commercial-light text-commercial-text px-2 py-1 rounded-full text-sm">
  CONFIRMED
</span>

// Tarjeta con borde izquierdo de color
<div className="bg-commercial-bg border-l-4 border-commercial p-4 rounded-r-lg">
  Contenido del módulo
</div>
```

---

## Sistema de Componentes

### Navbar

```
┌─────────────────────────────────────────────────────────┐
│  🏛 CICOR ERP          [C] [I] [C] [O] [R]  👤 Admin   │
└─────────────────────────────────────────────────────────┘
  bg: cicor-dark (#0C1E4D)
  text: white
  hover links: cicor-light (#DBEAFE) sobre cicor-dark
  logo + nombre: white
  módulo activo: subrayado con el color del módulo activo
```

**Identificadores visuales en la Navbar:**

| Módulo       | Letra | Color de badge  | Hex       |
|:-------------|:-----:|:----------------|:----------|
| Comercial    | `C`   | Verde           | `#10B981` |
| Inventario   | `I`   | Azul            | `#3B82F6` |
| Contabilidad | `C`   | Rojo            | `#EF4444` |
| Operaciones  | `O`   | Naranja         | `#F97316` |
| RRHH         | `R`   | Púrpura         | `#A855F7` |

---

### Dashboard (página principal)

```
┌─────────────────────────────────────────────────────────────────┐
│                     CICOR ERP Dashboard                          │
│              bg: cicor-light (#DBEAFE)                          │
├──────────┬──────────┬──────────┬──────────┬───────────────────┤
│ [C]      │ [I]      │ [C]      │ [O]      │ [R]               │
│Comercial │Inventario│Contabili.│Operac.   │ RRHH              │
│bg:#ECFDF5│bg:#EFF6FF│bg:#FEF2F2│bg:#FFF7ED│ bg:#FAF5FF        │
│border:🟢 │border:🔵 │border:🔴 │border:🟠 │ border:🟣         │
└──────────┴──────────┴──────────┴──────────┴───────────────────┘
```

Cada tarjeta del Dashboard:
- Fondo: `<módulo>-bg` (la variante más clara)
- Borde izquierdo (4px): `<módulo>-DEFAULT`
- Icono: color `<módulo>-DEFAULT`
- Título: `<módulo>-text`
- Contador / stat principal: text-2xl font-bold `<módulo>-DEFAULT`

---

### Botones

**Jerarquía de botones por módulo:**

```jsx
// Primario (acción principal: "Crear", "Guardar")
<button className="bg-{module} hover:bg-{module}-hover text-white 
                   font-medium px-4 py-2 rounded-lg transition-colors">

// Secundario (acción secundaria: "Editar", "Ver detalle")
<button className="bg-{module}-light hover:bg-{module} hover:text-white 
                   text-{module}-text font-medium px-4 py-2 rounded-lg transition-colors">

// Peligro (solo para "Eliminar") — siempre rojo, sin importar el módulo
<button className="bg-red-500 hover:bg-red-600 text-white 
                   font-medium px-4 py-2 rounded-lg transition-colors">

// Cancelar / Neutro
<button className="bg-gray-100 hover:bg-gray-200 text-gray-700 
                   font-medium px-4 py-2 rounded-lg transition-colors">
```

---

### Badges de Estado

Los badges de estado usan colores **semánticos fijos**, independientes del módulo:

| Estado                  | Bg           | Texto        | Hex bg    | Hex texto |
|:------------------------|:-------------|:-------------|:----------|:----------|
| `CONFIRMED` / `ACTIVE` / `POSTED` | `green-100`  | `green-800`  | `#DCFCE7` | `#166534` |
| `PENDING` / `PLANNING` / `DRAFT`  | `yellow-100` | `yellow-800` | `#FEF9C3` | `#854D0E` |
| `IN_PROGRESS`           | `blue-100`   | `blue-800`   | `#DBEAFE` | `#1E40AF` |
| `CANCELLED` / `INACTIVE`/ `REVERSED` | `red-100` | `red-800` | `#FEE2E2` | `#991B1B` |
| `ON_HOLD` / `ON_LEAVE`  | `gray-100`   | `gray-700`   | `#F3F4F6` | `#374151` |
| `PENDING_INVENTORY`     | `orange-100` | `orange-800` | `#FFEDD5` | `#9A3412` |
| `COMPLETED`             | `emerald-100`| `emerald-800`| `#D1FAE5` | `#065F46` |

```jsx
// Ejemplo de badge dinámico
const STATUS_STYLES = {
  CONFIRMED:          'bg-green-100   text-green-800',
  ACTIVE:             'bg-green-100   text-green-800',
  POSTED:             'bg-green-100   text-green-800',
  PENDING:            'bg-yellow-100  text-yellow-800',
  PLANNING:           'bg-yellow-100  text-yellow-800',
  DRAFT:              'bg-yellow-100  text-yellow-800',
  IN_PROGRESS:        'bg-blue-100    text-blue-800',
  CANCELLED:          'bg-red-100     text-red-800',
  INACTIVE:           'bg-red-100     text-red-800',
  REVERSED:           'bg-red-100     text-red-800',
  ON_HOLD:            'bg-gray-100    text-gray-700',
  ON_LEAVE:           'bg-gray-100    text-gray-700',
  PENDING_INVENTORY:  'bg-orange-100  text-orange-800',
  COMPLETED:          'bg-emerald-100 text-emerald-800',
};

const StatusBadge = ({ status }) => (
  <span className={`${STATUS_STYLES[status] || 'bg-gray-100 text-gray-700'} 
                    px-2 py-1 rounded-full text-xs font-medium`}>
    {status}
  </span>
);
```

---

### Modal (crear / editar)

```
┌────────────────────────────────────────┐
│  ✕  Crear Nueva Venta        [border-t: módulo-color]
├────────────────────────────────────────┤
│                                         │
│  Producto: [_______________________]   │
│  Cantidad: [_______________________]   │
│  Precio U.: [______________________]   │
│  Cliente:  [_______________________]   │
│                                         │
│          [Cancelar]  [Guardar →]       │
│             gray      módulo-color     │
└────────────────────────────────────────┘
```

- Header: `bg-white` con borde superior `border-t-4 border-{module}`
- Botón guardar: `bg-{module} hover:bg-{module}-hover text-white`
- Inputs en foco: `focus:ring-2 focus:ring-{module} focus:border-{module}`

---

### Tablas de datos

```jsx
// Cabecera de tabla con acento del módulo
<thead className="bg-{module}-light">
  <tr>
    <th className="text-{module}-text font-semibold px-4 py-3">ID</th>
    ...
  </tr>
</thead>

// Fila hover
<tr className="hover:bg-{module}-bg transition-colors">

// Fila seleccionada
<tr className="bg-{module}-bg border-l-2 border-{module}">
```

---

## Tipografía

| Elemento                  | Clase Tailwind                          |
|:--------------------------|:----------------------------------------|
| Título de página          | `text-2xl font-bold text-gray-900`      |
| Título de módulo          | `text-xl font-semibold text-{mod}-text` |
| Subtítulo / sección       | `text-lg font-medium text-gray-700`     |
| Texto cuerpo              | `text-sm text-gray-600`                 |
| Etiquetas de campo        | `text-sm font-medium text-gray-700`     |
| Placeholders              | `text-sm text-gray-400`                 |
| Texto en navbar           | `text-sm font-medium text-white`        |
| Número destacado (stat)   | `text-3xl font-bold text-{module}`      |

**Familia tipográfica:** System font stack (Tailwind default) — `font-sans`

---

## Espaciado y Layout

| Elemento                  | Valor Tailwind       |
|:--------------------------|:---------------------|
| Padding de página         | `px-6 py-8`          |
| Padding de tarjeta        | `p-6`                |
| Gap entre tarjetas        | `gap-6`              |
| Grid dashboard (4 cols)   | `grid-cols-1 md:grid-cols-2 lg:grid-cols-4` |
| Ancho máximo de contenido | `max-w-7xl mx-auto`  |
| Border radius tarjetas    | `rounded-xl`         |
| Border radius botones     | `rounded-lg`         |
| Border radius badges      | `rounded-full`       |
| Sombra de tarjetas        | `shadow-sm`          |
| Sombra de modal           | `shadow-xl`          |

---

## Referencia Rápida

| Módulo       | Color principal | Hex       | Clase Tailwind base |
|:-------------|:----------------|:----------|:--------------------|
| **Corporativo** | Azul oscuro  | `#1E40AF` | `bg-cicor-primary`  |
| Comercial    | Verde esmeralda | `#10B981` | `bg-commercial`     |
| Inventario   | Azul            | `#3B82F6` | `bg-inventory`      |
| Contabilidad | Rojo            | `#EF4444` | `bg-accounting`     |
| Operaciones  | Naranja         | `#F97316` | `bg-operations`     |
| RRHH         | Púrpura         | `#A855F7` | `bg-hr`             |

### Vista de colores primarios

```
█ #1E40AF  CICOR Corporate (Azul)
█ #10B981  Comercial (Verde Esmeralda)
█ #3B82F6  Inventario (Azul)
█ #EF4444  Contabilidad (Rojo)
█ #F97316  Operaciones (Naranja)
█ #A855F7  RRHH (Púrpura)
```

> Para accesibilidad, todos los colores de texto sobre fondo claro cumplen ratio de contraste WCAG AA (≥ 4.5:1). Verificar siempre con [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/) al crear nuevas combinaciones.
