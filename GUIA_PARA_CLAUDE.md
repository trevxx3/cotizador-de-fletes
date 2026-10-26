# Guía del Cotizador de Envíos de Llantas (para trabajar con Claude)

## 1. ¿Qué hace esta página?

Es una herramienta para que los **vendedores** coticen rápido cuánto cuesta enviar llantas de una ciudad a otra.

- Se captura **Origen**, **Destino** y la **distancia en km** (se llena sola para las ciudades principales; se puede corregir a mano).
- Se elige **tipo de llanta** (Auto/Camioneta, Camión/Carga, Agrícola, OTR/Industrial), **cantidad**, **vehículo** (Camioneta, Rabón, Torton, Tráiler 53' o "Automático", que sugiere el vehículo según el peso) y **urgencia** (Normal / Express).
- Muestra un **desglose**: costo por km, cargo por llanta, recargo express, casetas, combustible, mínimo por envío, subtotal, IVA y **total en MXN**.
- Botones para **copiar la cotización como texto** (para WhatsApp o correo), **imprimir / guardar como PDF**, y un **historial** de las últimas 20 cotizaciones (se guarda en el mismo equipo).
- Botón **⚙ Configuración de tarifas** para cambiar precios sin tocar código (se guardan en ese navegador).

> ⚠️ **Importante:** todas las tarifas, pesos y capacidades que trae son **DE EJEMPLO**. Las distancias son **aproximadas**. No usar para cotizar a clientes hasta poner los números reales.

## 2. ¿Cómo se abre?

1. Descomprime el archivo `cotizador-llantas.zip`.
2. Haz **doble clic** en `index.html`. Se abre en Chrome, Edge, Safari o Firefox.
3. No necesita internet ni instalar nada. También funciona en celular/tableta si se sube a internet (ver punto 6‑f).

## 3. Estructura de los archivos

```
cotizador-llantas/
├── index.html            ← TODA la página (diseño + lógica) en un solo archivo
├── GUIA_PARA_CLAUDE.md   ← esta guía
├── tools/tiempos_cedis.py ← recalcula el "tiempo típico en CEDIS" desde el Excel de tiempos
└── captura.png           ← imagen de ejemplo de cómo se ve
```

Dentro de `index.html`, el código está dividido en secciones con títulos grandes:

| Sección | Qué contiene | ¿Se toca seguido? |
|---|---|---|
| `<style>` | Colores, tamaños, diseño de impresión | Solo para cambiar el look |
| **A: CATÁLOGOS** | Ciudades, tipos de llanta (peso de ejemplo), vehículos (capacidad de ejemplo) | A veces |
| **B: DISTANCIAS** | Tabla de km entre ciudades + función `obtenerDistanciaKm()` (aquí se conectaría Google Maps) | A veces |
| **C: TARIFAS** | `TARIFAS_EJEMPLO`: costo por km por vehículo, por llanta, mínimo, % express, % IVA, casetas, diésel | ✅ **Sí** |
| **D: CÁLCULO** | `calcularCotizacion(datos, tarifas)`: la fórmula del precio | ✅ **Sí** |
| E, F, G | Guardado, pantalla, copiar/imprimir, historial | Casi nunca |
| **H: TIEMPO EN CEDIS** | `TIEMPOS_CEDIS` (estadísticas agregadas) + `tiempoCedisPara(fecha)`. Solo informativo: **no cambia el precio** | Cuando se actualice el Excel de tiempos |

**Regla de oro:** para cambiar *cómo se cobra*, pídele a Claude que modifique **solo las secciones C y D**. La pantalla de configuración se arma sola a partir de las tarifas de la sección C.

### Cómo calcula hoy (ejemplo)

```
Costo base     = km × costo por km del vehículo
Cargo llantas  = cantidad × cargo por llanta según tipo
Express        = (base + llantas) × % express       (solo si es Express)
Casetas        = km × casetas por km                (hoy en 0 = no se cobra)
Combustible    = (km ÷ rendimiento) × precio diésel (hoy en 0 = no se cobra)
Subtotal       = suma de lo anterior (si es menor al mínimo, se sube al mínimo)
IVA            = subtotal × 16%
Total          = subtotal + IVA
```

## 4. Datos que conviene juntar antes de hablar con Claude

- [ ] **Costo por km** de cada vehículo (Camioneta, Rabón, Torton, Tráiler) — o si cobran por rangos de km.
- [ ] **Rendimiento de diésel** de cada vehículo (km por litro) y precio actual del diésel.
- [ ] **Casetas**: costo aproximado por ruta frecuente (o un promedio por km).
- [ ] **Capacidad real** de cada vehículo: cuántas llantas de cada tipo caben (o kg / m³).
- [ ] **Peso o tamaño real** de las llantas que más mueven.
- [ ] **Cargos fijos**: maniobra de carga/descarga, seguro, viáticos del chofer, regreso vacío.
- [ ] **Mínimo por envío** y **recargo Express**.
- [ ] **Margen de ganancia** (% que se suma al costo) y si hay descuentos por volumen o por cliente.
- [ ] **Zonas** (si cobran por zona: local, regional, nacional).
- [ ] Ciudades/rutas que más usan y sus **km reales** (Google Maps).
- [ ] Nombre de la empresa, logo, teléfono, condiciones (vigencia de la cotización, forma de pago).

## 5. Cómo trabajar con Claude (pasos)

1. Abre Claude (claude.ai) y empieza una conversación nueva.
2. **Adjunta el archivo `index.html`** (botón del clip 📎) o pega su contenido.
3. Copia el **Prompt maestro** (6‑a) y después el prompt de lo que quieres cambiar.
4. Claude te devolverá el archivo corregido: guárdalo como `index.html` (reemplazando el anterior; conserva una copia del viejo por si acaso).
5. Ábrelo con doble clic y prueba con una ruta conocida para revisar que el total cuadre.

> Tip: pide un cambio a la vez. Si algo sale mal, regresa a la copia anterior.

## 6. Prompts listos para copiar

### a) Prompt maestro (pégalo siempre al inicio)

```
Te adjunto index.html: es un cotizador de envíos de llantas para los vendedores de una
distribuidora en México. Es un solo archivo HTML con CSS y JavaScript dentro, sin
dependencias, que se abre con doble clic. Todo el texto debe quedar en español de México
y los precios en MXN.

La lógica de precios está aislada en dos secciones marcadas con banners:
- SECCIÓN C: TARIFAS_EJEMPLO (valores de tarifas; el modal "Configuración de tarifas"
  se construye automáticamente a partir de este objeto).
- SECCIÓN D: function calcularCotizacion(datos, tarifas), que regresa
  { conceptos:[{concepto, detalle, monto, pendiente?}], subtotal, iva, total,
    vehiculo, pesoTotalKg, alertas:[] }.

Reglas:
1. Modifica SOLO las secciones C y D, salvo que te pida otra cosa explícitamente.
2. No cambies la forma del objeto que regresa calcularCotizacion (la pantalla depende de él).
3. Cada tarifa nueva agrégala en TARIFAS_EJEMPLO.valores con {valor, etiqueta, unidad, grupo}.
4. Mantén el código comentado en español y sin librerías externas.
5. Al terminar, dame el archivo index.html COMPLETO y un ejemplo numérico de cómo
   queda la cotización Monterrey → CDMX (910 km) con 40 llantas de camión.
Si algo de mis reglas de cálculo no está claro, pregúntame antes de programar.
```

### b) "Así calculamos" — plantilla con tus tarifas reales (llena los espacios)

```
Así calculamos nuestros envíos. Actualiza TARIFAS y calcularCotizacion con estos datos
y cambia esEjemplo a false:

- Costo por km: Camioneta $____, Rabón $____, Torton $____, Tráiler 53' $____
- Cargo por llanta: Auto/Camioneta $____, Camión $____, Agrícola $____, OTR $____
- Mínimo por envío: $____ (antes de IVA)
- Recargo Express: ____ % (se aplica sobre: ____________)
- Casetas: ________ (promedio $____ por km / o monto fijo por ruta)
- Diésel: precio $____ por litro; rendimiento Camioneta __ km/L, Rabón __, Torton __, Tráiler __
- ¿El costo por km ya incluye el diésel? (sí / no): ____
- Cargos fijos (maniobra, seguro, viáticos): ____________
- Margen de ganancia: ____ % sobre el costo
- IVA: 16 % (¿hay clientes con frontera 8 %? ____)
- Capacidad por vehículo (llantas de camión): Camioneta __, Rabón __, Torton __, Tráiler __
- Peso aproximado por llanta: Auto __ kg, Camión __ kg, Agrícola __ kg, OTR __ kg
```

### c) Variantes de cálculo (usa la que aplique)

**Tarifa por rangos de km**
```
Cambia el costo base para que sea por rangos de distancia:
0–100 km: $____ fijo; 101–500 km: $____ por km; 501–1000 km: $____ por km;
más de 1000 km: $____ por km. Que los rangos se puedan editar en Configuración de tarifas.
```

**Por peso o volumen**
```
Quiero cobrar por peso/volumen en lugar de por llanta: $____ por kg (o por m³).
Usa el peso/volumen de cada tipo de llanta (Auto __ kg/__ m³, Camión __, Agrícola __, OTR __).
Si la carga no cabe en el vehículo elegido, calcula cuántos viajes hacen falta y cóbralos.
```

**Por tipo de vehículo (tarifa por viaje)**
```
Cobramos por viaje completo según vehículo y ruta, no por km. Tarifa por viaje:
Camioneta $____, Rabón $____, Torton $____, Tráiler $____ hasta ____ km; arriba de eso
$____ por km adicional. Sugiere automáticamente el vehículo según cuántas llantas caben
(capacidades: ____).
```

**Por zonas**
```
Cobramos por zonas desde Monterrey: Zona 1 (área metropolitana) $____; Zona 2 (Noreste:
Saltillo, Torreón, SLP...) $____; Zona 3 (Centro: CDMX, Querétaro, Guadalajara...) $____;
Zona 4 (resto del país) $____. Agrega un selector o detección de zona por ciudad destino.
```

**Mínimo por envío y descuentos**
```
Agrega: mínimo por envío de $____; descuento de ____ % a partir de ____ llantas;
y un campo "Descuento especial %" que el vendedor pueda capturar (máximo ____ %).
```

**Casetas y diésel reales**
```
Calcula el combustible como (km ÷ rendimiento del vehículo) × precio del diésel, con un
rendimiento distinto por vehículo (Camioneta __, Rabón __, Torton __, Tráiler __ km/L).
Para casetas usa esta tabla por ruta: Monterrey–CDMX $____, Monterrey–Guadalajara $____, ...
y si la ruta no está, usa $____ por km. Considera también el regreso vacío (sí/no: __).
```

### d) Distancias reales con Google Maps

```
Conecta la función obtenerDistanciaKm(origen, destino) (sección B) a la API Distance
Matrix de Google Maps (o a OpenRouteService si es más barato) para obtener los km reales
por carretera para camión. Mantén la tabla actual como respaldo si no hay internet o la
API falla. La API key debe estar en una constante al inicio del script con un comentario
claro. Explícame paso a paso cómo sacar la API key y cuánto cuesta.
```
> Nota: Google Maps pide tarjeta para activar la API (tiene crédito mensual gratis). OpenRouteService tiene plan gratuito. Una API key puesta en una página pública puede ser usada por otros: restríngela a tu dominio.

### e) Nombre de la empresa y logo

```
Pon el nombre de la empresa "__________" en el encabezado y en la cotización impresa.
Usa este logo (te lo adjunto) en lugar del círculo naranja, incrustado en el archivo para que
siga funcionando sin internet. Agrega al pie de la cotización impresa: teléfono ________,
correo ________, dirección ________ y la leyenda "Cotización válida por __ días".
Cambia los colores a los de la marca: principal ______, acento ______.
```

### f) Publicarla en internet / varios usuarios con login (más adelante)

**Publicarla (gratis, sin login):**
```
Quiero publicar esta página para que los vendedores la abran desde su celular. Explícame
paso a paso cómo subir index.html a Netlify (arrastrar y soltar) o a GitHub Pages.
```

**Multiusuario con login y tarifas compartidas:**
```
Quiero convertir este cotizador en una aplicación multiusuario: cada vendedor entra con su
usuario y contraseña, las tarifas las administra solo un administrador y son las mismas para
todos, y las cotizaciones se guardan en una base de datos para consultarlas después (por
vendedor, cliente y fecha). Propón la opción más sencilla y barata (por ejemplo Supabase o
Firebase + Netlify), reutilizando el diseño y la función calcularCotizacion actuales.
Explícame los pasos como a alguien que no es programador.
```

## 6-bis. Tiempo típico en CEDIS (sección H)

La cotización muestra un recuadro **"⏱ Tiempo típico en CEDIS"** (también sale en el texto
para WhatsApp y al imprimir). Sale del Excel de tiempos Cedis/Mayoreo (hoja **Tiempos**).

- **En la página solo hay estadísticas agregadas** (medianas, percentiles y conteos). **Nunca**
  se suben nombres de choferes, facturas, traspasos, observaciones ni filas del Excel.
  **El Excel NO se sube al repositorio** (el sitio es público).
- Cálculo (igual que la hoja Resumen): *Tiempo en CEDIS* = hora despacho − hora llegada a CEDIS;
  *Ciclo total* = hora despacho − hora del vale.
- Limpieza: se descartan tiempos en CEDIS menores a 1 min (llegada y despacho capturados al
  mismo tiempo) o mayores a 240 min (olvidos de cierre), y ciclos < 1 min o > 480 min.
- "~X min" = **mediana**; "normalmente entre A y B" = percentiles 25 y 75 (la mitad de los vales).
- Se adapta a la **hora** en que se hace la cotización: mañana (antes de 12), mediodía (12–15), tarde
  (desde 15). Por **cantidad de llantas** no hubo diferencia real, por eso no se usa.
- El objeto también trae `pctDentroMeta` (% de vales ≤ 20 min) y `comparacionExcel` (cifras sin la
  limpieza extra, como las calcula la hoja Resumen); no se muestran al cliente.

**Para actualizarlo** con un Excel nuevo (en la carpeta del proyecto):

```
python3 tools/tiempos_cedis.py "C:/ruta/al/Excel de tiempos.xlsx" --reemplazar index.html
```

(Requiere `pip install openpyxl`.) Después revisa la página y súbela. Prompt para Claude:
"Actualiza la constante TIEMPOS_CEDIS (sección H) con estos números / cambia el texto del recuadro
de tiempo en CEDIS. No toques las secciones C y D."

## 7. Limitaciones actuales (para saber)

- Tarifas, pesos y capacidades son **de ejemplo**.
- Distancias **aproximadas**; si la ruta no está en la tabla se **estima** (línea recta × 1.3) y la página lo avisa. Direcciones exactas no se calculan: escribe los km a mano.
- Las tarifas editadas y el historial se guardan **solo en el navegador de ese equipo** (si se borra el historial del navegador, se pierden; cada vendedor tiene los suyos).
- No hay login ni base de datos todavía (ver 6‑f).
- El tiempo en CEDIS es una **referencia histórica** (no un compromiso) y depende de la calidad de
  captura del Excel (hubo bastantes registros con horas mal capturadas, que se descartan).
