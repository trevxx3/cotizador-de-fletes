#!/usr/bin/env python3
"""
Recalcula los AGREGADOS de "tiempo típico en CEDIS" a partir del Excel de tiempos
(hoja "Tiempos") y los imprime como JSON listo para pegar en index.html
(constante TIEMPOS_CEDIS).

Uso:   python3 tools/tiempos_cedis.py RUTA/AL/ARCHIVO.xlsx  > tiempos.json
       python3 tools/tiempos_cedis.py RUTA.xlsx --reemplazar index.html   (actualiza la constante)

IMPORTANTE: el Excel NO se sube al repositorio (tiene nombres de choferes, facturas
y notas internas). Este script solo publica estadísticas agregadas (medianas,
percentiles, conteos). Nunca exporta filas, nombres, facturas ni observaciones.

Reglas (iguales a la hoja "Resumen" del Excel):
  Tiempo en CEDIS  (col. M) = Hora despacho (L) - Hora llegada a CEDIS (H)
  Tiempo de ciclo  (col. N) = Hora despacho (L) - Hora del vale (B)
  1) Igual que el Excel: se excluyen tiempos vacíos, negativos o >= 24 h.
  2) Limpieza extra para el "tiempo típico" que se muestra en la página:
     - En CEDIS: se descartan < 1 min (llegada y despacho capturados al mismo
       tiempo, no es una atención real) y > 240 min (olvidos de cierre).
     - Ciclo total: se descartan < 1 min y > 480 min.
     Los valores "estilo Excel" (sin limpieza extra) se guardan en "comparacionExcel".
  Meta: <= 20 min en CEDIS (celda Resumen!C6).
"""
import sys, json, re, datetime as dt, statistics
import openpyxl

EXCEL_EPOCH = dt.datetime(1899, 12, 30)

def serial(v):
    """Convierte un valor de celda al número de Excel (días)."""
    if v is None or v == "":
        return None
    if isinstance(v, dt.datetime):
        return (v - EXCEL_EPOCH).total_seconds() / 86400
    if isinstance(v, dt.date):
        return (dt.datetime(v.year, v.month, v.day) - EXCEL_EPOCH).days
    if isinstance(v, dt.time):
        return (v.hour * 3600 + v.minute * 60 + v.second + v.microsecond / 1e6) / 86400
    if isinstance(v, dt.timedelta):
        return v.total_seconds() / 86400
    if isinstance(v, (int, float)):
        return float(v)
    return None

def celda_tiempo(fila, col_valor, a, b):
    """Si la celda es fórmula (=IF(x="","",a-b)) la evalúa como Excel; si es valor, lo usa."""
    v = fila[col_valor]
    if isinstance(v, str) and v.startswith("="):
        x, y = serial(fila[a]), serial(fila[b])
        if fila[a] in (None, ""):
            return None
        if y is None:
            y = 0.0
        return x - y
    return serial(v)

def pct(xs, p):
    """Percentil con interpolación lineal (igual que PERCENTILE.INC / AGGREGATE 16)."""
    xs = sorted(xs)
    if not xs:
        return None
    k = (len(xs) - 1) * p
    f = int(k); c = min(f + 1, len(xs) - 1)
    return xs[f] + (xs[c] - xs[f]) * (k - f)

def resumen(mins):
    if not mins:
        return None
    return {
        "n": len(mins),
        "mediana": round(pct(mins, .5)),
        "p25": round(pct(mins, .25)),
        "p75": round(pct(mins, .75)),
        "p80": round(pct(mins, .80)),
        "promedio": round(sum(mins) / len(mins)),
    }

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    wb = openpyxl.load_workbook(sys.argv[1])
    ws = wb["Tiempos"]
    META = 20
    try:
        META = float(wb["Resumen"]["C6"].value or 20)
    except Exception:
        pass

    # Índices de columna (0 = A)
    A, B, E, H, L, M, N = 0, 1, 4, 7, 11, 12, 13
    filas = []
    for r in ws.iter_rows(min_row=3, values_only=True):
        if r[A] is None:
            continue
        filas.append(r)

    fechas = [r[A] for r in filas if isinstance(r[A], dt.datetime)]
    cedis, ciclo = [], []
    por_franja = {"manana": [], "mediodia": [], "tarde": []}
    por_llantas = {"1-4": [], "5-8": [], "9+": []}
    excluidos = 0
    excel_cedis, excel_ciclo = [], []
    CEDIS_MIN, CEDIS_MAX, CICLO_MIN, CICLO_MAX = 1, 240, 1, 480
    for r in filas:
        m = celda_tiempo(r, M, L, H)
        n = celda_tiempo(r, N, L, B)
        if n is not None and 0 < n < 1:
            excel_ciclo.append(n * 1440)
            if CICLO_MIN <= n * 1440 <= CICLO_MAX:
                ciclo.append(n * 1440)
        if m is None:
            continue
        if 0 < m < 1:
            excel_cedis.append(m * 1440)
        mins = m * 1440
        if not (CEDIS_MIN <= mins <= CEDIS_MAX):
            excluidos += 1
            continue
        cedis.append(mins)
        hb = serial(r[B])
        if hb is not None:
            h = (hb % 1) * 24
            franja = "manana" if h < 12 else ("mediodia" if h < 15 else "tarde")
            por_franja[franja].append(mins)
        q = r[E]
        if isinstance(q, (int, float)) and q > 0:
            por_llantas["1-4" if q <= 4 else ("5-8" if q <= 8 else "9+")].append(mins)

    dentro = sum(1 for x in cedis if x <= META)
    out = {
        "fuente": "Excel de tiempos Cedis/Mayoreo, hoja 'Tiempos' (solo estadísticas agregadas)",
        "periodo": {"del": min(fechas).date().isoformat(), "al": max(fechas).date().isoformat()},
        "valesRegistrados": len(filas),
        "metaMin": META,
        "pctDentroMeta": round(100 * dentro / len(cedis)) if cedis else None,
        "excluidosPorError": excluidos,  # vales con tiempo en CEDIS fuera de 1-240 min
        "cedis": resumen(cedis),
        "ciclo": resumen(ciclo),
        "porFranja": {k: resumen(v) for k, v in por_franja.items()},
        "porLlantas": {k: resumen(v) for k, v in por_llantas.items()},
        "limpieza": "En CEDIS solo 1-240 min; ciclo solo 1-480 min (se descartan errores de captura)",
        "comparacionExcel": {
            "cedis": resumen(excel_cedis),
            "ciclo": resumen(excel_ciclo),
            "pctDentroMeta": round(100 * sum(1 for x in excel_cedis if x <= META) / len(excel_cedis)) if excel_cedis else None,
        },
    }
    txt = json.dumps(out, ensure_ascii=False, indent=2)
    if len(sys.argv) >= 4 and sys.argv[2] == "--reemplazar":
        ruta = sys.argv[3]
        html = open(ruta, encoding="utf-8").read()
        nuevo, k = re.subn(r"const TIEMPOS_CEDIS = \{.*?\};",
                           "const TIEMPOS_CEDIS = " + txt + ";", html, flags=re.S)
        if k != 1:
            sys.exit("No encontré 'const TIEMPOS_CEDIS = {...};' en " + ruta)
        open(ruta, "w", encoding="utf-8").write(nuevo)
        print("Actualizado", ruta)
    print(txt)

if __name__ == "__main__":
    main()
