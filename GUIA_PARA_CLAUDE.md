# Guía del Cotizador de Fletes · Mayoreo (para trabajar con Claude)

## 1. ¿Qué hace esta página?

Es la versión web de la hoja **"Cotizador"** del Excel *COTIZADOR DE FLETES · MAYOREO*,
más un **margen** para dar **precio de venta al cliente**. Flujo:

1. Se elige el **destino** (lista del Excel: 5 zonas locales de Monterrey y 45 destinos nacionales).
2. Se captura **cuántas llantas de cada tipo** (Chica, Mediana, Grande, Extra Grande, Camión).
   La página muestra kg y la **ocupación** de Nissan, Camión 3.5 y Tráiler en vivo.
3. Calcula el **costo interno** de Paquetería, Fletera, Nissan NP300, Camión 3.5 y Tráiler propio
   y **recomienda la de menor costo**.
4. Muestra al vendedor la **cotización para el cliente** de la opción recomendada: **Subtotal, IVA 16% y Total**
   (y precio por llanta). Con el selector **"Forma de envío"** se puede elegir otra opción.
5. Los costos internos, el margen, la utilidad y el desglose (km, sueldo del chofer, comidas…) están en
   **"🔒 Detalle interno (solo vendedor)"**, que aparece **cerrado** por defecto.
- **Copiar texto** (WhatsApp/correo) e **Imprimir / PDF** muestran **solo** lo del cliente: destino, llantas,
  forma de envío, subtotal, IVA, total y vigencia. **Nunca** costos ni margen.
- **Historial** (últimas 20, en ese equipo) y **⚙ Tarifas y margen** (cambios solo en ese navegador).

> ⚠️ El archivo contiene los **costos internos** y el **margen** (ver sección 7): no publicarlo en un sitio público.

## 2. ¿Cómo se abre?

Doble clic en `index.html` (Chrome, Edge, Safari o Firefox). No necesita internet ni servidor:
los datos del Excel están **dentro** del archivo.

## 3. Estructura

```
cotizador-llantas/
├── index.html              ← toda la página (diseño + datos + lógica)
├── tools/excel_a_json.py   ← lee el Excel y actualiza los datos dentro de index.html
├── GUIA_PARA_CLAUDE.md     ← esta guía
└── captura.png             ← imagen de ejemplo
```

| Sección en `index.html` | Qué contiene | ¿Se toca? |
|---|---|---|
| `<style>` | Colores (azul marino / naranja), impresión, celular | Solo para el look |
| **C: DATOS DEL EXCEL** | `DATOS_EXCEL` (parámetros, tipos de llanta, destinos). **No editar a mano**: se regenera con el script | Al actualizar el Excel |
| **D: CÁLCULO** | `calcularCotizacion()` y `costoViajePropio()`: el costo interno, igual al Excel | ✅ Para cambiar la lógica |
| **D2: PRECIO DE VENTA** | `MARGEN_BASE` (margen general, por forma de envío, precio mínimo, vigencia) y `precioVenta()` | ✅ **Aquí se pone el margen** |
| E, F, G | Configuración guardada, pantalla, copiar/imprimir, historial | Casi nunca |

## 4. Cómo calcula (igual que el Excel)

De la hoja **Tarifas** (por destino):
```
Km redondo            = km sencillo × 2
Costo viaje Nissan    = km redondo × $7/km  + comidas $600 + permiso $500
                        + sueldo diario chofer (24,000/4/7 = $857.14) + tiempo extra $800 + casetas
Costo viaje Cam. 3.5  = igual, con $4/km
Costo viaje Tráiler   = igual, con $/km del tráiler (VACÍO en el Excel → "Sin tarifa")
Fletera               = tarifa SIN IVA          (solo 8 destinos tienen tarifa)
```
De la hoja **Cotizador**:
```
Paquetería  = Σ cantidad × $/llanta ($58 llantas de auto, $116 camión)
Ocupación   = Σ cantidad ÷ capacidad del tipo   (Nissan 80, Camión 3.5 200, Tráiler 450–1,800)
Unidades propias: máximo 1 viaje; si la ocupación pasa de 100% → "No cabe"
Fletera     = tarifa sin IVA × viajes de tráiler (mínimo 1)   ← ver pregunta abierta 1
Recomendada = la opción con MENOR COSTO interno (todo sin IVA)
```
Precio de venta (sección D2), para cada opción:
```
Subtotal = costo interno (sin IVA) × (1 + margen%)
             margen% = margen de esa forma de envío si está capturado; si no, el margen general
Si hay precio mínimo y el subtotal queda abajo → subtotal = precio mínimo (antes de IVA)
IVA      = subtotal × 16%
Total    = subtotal + IVA
```
**Criterio de IVA:** todos los costos se comparan **sin IVA** (también la fletera, que antes se tomaba con IVA),
se aplica el margen y **al final** se suma el IVA al precio del cliente. Así ninguna opción "carga" IVA dos veces.

**Margen pendiente:** en `MARGEN_BASE` el margen general está en `null` → la página usa **0%** y muestra en rojo
**"⚠ Margen pendiente de definir"**. Si se marca *"El margen es un valor de PRUEBA"* sale un aviso naranja.
Ninguno de los dos avisos aparece en el texto copiado ni en la impresión (el vendedor recibe otro aviso al copiar).

Ejemplo (Allende, 80 llantas Chica, margen de prueba 20%): Paquetería costo $4,640 → subtotal $5,568 →
IVA $890.88 → **total $6,458.88** ($80.74 por llanta).
Zonas locales (Monterrey) no tienen km ni fletera en el Excel → solo Paquetería.

## 5. Cómo definir el margen

- **Para todos** (recomendado): en `index.html`, sección D2, cambiar `MARGEN_BASE`, p. ej.
  `margenGeneral: 18,` y, si se quiere, `margenPorModo: { paqueteria: 25, fletera: 12, … }`,
  `precioMinimo: 1500,` `vigenciaDias: 7`. Volver a compartir el archivo.
- **Solo en un equipo:** botón **⚙ Tarifas y margen** → "Margen y precio de venta".
  Se guarda en ese navegador ("Restaurar" regresa a lo del archivo).

## 6. Cómo actualizar los datos cuando cambie el Excel

En la carpeta del proyecto (requiere Python y `pip install openpyxl`):
```
python3 tools/excel_a_json.py "C:/ruta/COTIZADOR DE FLETES.xlsx" --reemplazar index.html
```
Lee la hoja **Tarifas**: D5:D12 (parámetros), B15:G19 (tipos de llanta) y B23 hacia abajo (destinos).
Si agregas destinos al final de la tabla, entran solos. **Nunca subas el Excel al repositorio.**

## 7. Prompts para Claude

**Prompt maestro:**
```
Te paso index.html del Cotizador de Fletes (un solo archivo HTML/JS). Los datos están en la
constante DATOS_EXCEL (sección C, generada por tools/excel_a_json.py), el costo interno en la
sección D (calcularCotizacion) y el margen/precio de venta en la sección D2 (MARGEN_BASE,
precioVenta). El texto copiado y la impresión NUNCA deben mostrar costos ni margen.
Haz SOLO este cambio: [...]. No cambies el diseño. Devuélveme el archivo completo y dime cómo probarlo.
```
Ejemplos: "Pon el margen general en 18% y en fletera 10%" · "Recomienda la opción más barata para el cliente (precio con margen) en lugar del menor costo" ·
"La fletera debe usar la tarifa sin IVA" · "Permite hasta 2 viajes de Camión 3.5" ·
"Usa las capacidades de la hoja Capacidades (por tamaño) en lugar de 80/200".

## 8. Publicación y datos sensibles

Todo el cálculo corre **en el navegador**: aunque el detalle interno esté cerrado y no se imprima,
**cualquiera que abra el código de la página** (clic derecho → "Ver código fuente") ve los costos internos
(costo por km, sueldo del chofer, tarifas de fletera y paquetería) y el margen. Ocultar la sección
solo evita que se vea por accidente; **no es seguridad**. Opciones reales:
1. **Compartir el archivo solo con vendedores** (WhatsApp/Drive, doble clic). Al cliente solo se le manda
   el texto copiado o el PDF. Sin costo y lo más simple.
2. **Hosting con contraseña / control de acceso** (p. ej. Cloudflare Pages + Cloudflare Access,
   o Netlify con protección por contraseña): solo entra quien tenga acceso; el código sigue visible para ellos.
3. **Un backend pequeño** (servidor o función en la nube) que guarde costos y margen y devuelva solo
   el precio de venta: la única forma de que ni los vendedores vean los costos. Requiere desarrollo y mantenimiento.

**No publicar esta versión en el repositorio/sitio público actual.**

## 9. Preguntas abiertas / limitaciones

1. **Fletera:** en el Excel la celda Cotizador!D20 devuelve **0** cuando hay tarifa (fórmula incompleta),
   y entonces la fletera "gana" con $0. Aquí se usa **tarifa sin IVA × viajes de tráiler** (el IVA se suma al final). ¿Correcto?
2. **Tráiler propio:** no tiene costo por km (Tarifas!D7 vacío) → siempre "Sin tarifa".
3. **Casetas:** columna vacía para todos los destinos → se toman $0.
4. **Capacidades:** la hoja Tarifas usa 80/200 para todos los tamaños, pero la hoja Capacidades tiene cifras
   distintas por tamaño (p. ej. Nissan caja abierta: chica 130; Camión 3.5: chica 650). La página usa las de **Tarifas** (como el Excel).
5. **Paquetería** $58 / $116 por llanta: se tomaron como **sin IVA**. ¿Es así?
5b. **Margen:** % general y, si aplica, por forma de envío; ¿precio mínimo? ¿vigencia (hoy 7 días)?
5c. **Recomendación:** hoy es la de menor **costo**; con márgenes distintos por forma de envío podría no ser la más barata para el cliente.
6. Kg por llanta: 9 kg para todos los tamaños de auto (Chica a Extra Grande) y 50 kg camión.
7. Hojas no usadas por el cotizador: Pedido (bitácora de pedidos), Concentrado y Hoja 1 (versiones anteriores),
   Zonas (catálogo), Gestion de Unidades y Tipos llanta (ocultas, referencia).
