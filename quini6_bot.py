"""
Bot de control de Quini 6.
Scrapea el último sorteo desde quini-6-resultados.com.ar,
compara contra las jugadas hardcodeadas y avisa por Telegram.
"""

import os
import re
import sys
import requests

URL_RESULTADOS = "https://www.quini-6-resultados.com.ar/"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# ---------------------------------------------------------------------------
# Jugadas hardcodeadas
# ---------------------------------------------------------------------------
JUGADAS = {
    "Jugada 1": [7, 9, 15, 32, 36, 40],
    "Jugada 2": [8, 14, 21, 27, 32, 35],
}

# Modalidades que se juegan. Cada una se controla contra el mismo conjunto
# de números de cada jugada (Tradicional / La Segunda / Revancha / Siempre Sale
# usan la misma boleta, cada una con su propio sorteo de 6 números).
MODALIDADES = ["Tradicional", "La Segunda", "Revancha", "Siempre Sale"]


def obtener_resultados():
    """
    Descarga la home de quini-6-resultados.com.ar y extrae:
    - fecha y número del último sorteo
    - los 6 números de cada una de las 4 modalidades
    Devuelve un dict: {"fecha": str, "nro_sorteo": str, "Tradicional": [..], ...}
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    session = requests.Session()
    resp = session.get(URL_RESULTADOS, headers=headers, timeout=20)
    resp.raise_for_status()
    texto = resp.text

    # Fecha y número de sorteo, ej: "Sorteo del dia 02/09/2026 Nro. Sorteo: 3405"
    m_sorteo = re.search(
        r"Sorteo del d[ií]a\s*(\d{2}/\d{2}/\d{4}).*?Nro\.?\s*Sorteo:?\s*(\d+)",
        texto,
        re.IGNORECASE | re.DOTALL,
    )
    if not m_sorteo:
        raise RuntimeError("No se pudo encontrar la fecha/número de sorteo en la página")

    fecha = m_sorteo.group(1)
    nro_sorteo = m_sorteo.group(2)

    # A partir de la posición del bloque de sorteo, buscamos las 4 tandas de
    # 6 números de dos dígitos separados por guiones, en orden:
    # TRADICIONAL, LA SEGUNDA, REVANCHA, SIEMPRE SALE
    bloque = texto[m_sorteo.start():]
    patron_numeros = re.compile(r"(\d{2}(?:\s*-\s*\d{2}){5})")
    encontrados = patron_numeros.findall(bloque)

    if len(encontrados) < 4:
        raise RuntimeError(
            f"Se esperaban 4 grupos de números y se encontraron {len(encontrados)}"
        )

    resultado = {"fecha": fecha, "nro_sorteo": nro_sorteo}
    for modalidad, grupo in zip(MODALIDADES, encontrados[:4]):
        numeros = [int(n) for n in re.findall(r"\d{2}", grupo)]
        resultado[modalidad] = numeros

    return resultado


def calcular_aciertos(jugada, numeros_sorteo):
    """Devuelve la lista de números acertados entre una jugada y un sorteo."""
    return sorted(set(jugada) & set(numeros_sorteo))


def calcular_pozo_extra(jugada, resultados):
    """
    El Pozo Extra se gana con 6 aciertos contando los tres primeros sorteos
    (Tradicional + La Segunda + Revancha), contando los números repetidos
    una sola vez.
    """
    combinado = set(resultados["Tradicional"]) | set(resultados["La Segunda"]) | set(resultados["Revancha"])
    return calcular_aciertos(jugada, combinado)


def formatear_mensaje(resultados):
    lineas = []
    lineas.append(f"🎰 <b>Quini 6 - Sorteo {resultados['nro_sorteo']}</b> ({resultados['fecha']})")
    lineas.append("")

    hubo_algun_acierto = False

    for nombre_jugada, numeros_jugada in JUGADAS.items():
        lineas.append(f"<b>{nombre_jugada}:</b> {' - '.join(f'{n:02d}' for n in numeros_jugada)}")

        for modalidad in MODALIDADES:
            aciertos = calcular_aciertos(numeros_jugada, resultados[modalidad])
            if aciertos:
                hubo_algun_acierto = True
                aciertos_str = ", ".join(f"{n:02d}" for n in aciertos)
                lineas.append(f"  ✅ {modalidad}: {len(aciertos)} aciertos ({aciertos_str})")
            else:
                lineas.append(f"  ➖ {modalidad}: sin aciertos")

        aciertos_extra = calcular_pozo_extra(numeros_jugada, resultados)
        if aciertos_extra:
            hubo_algun_acierto = True
            aciertos_str = ", ".join(f"{n:02d}" for n in aciertos_extra)
            lineas.append(f"  ✅ Pozo Extra: {len(aciertos_extra)} aciertos ({aciertos_str})")
        else:
            lineas.append("  ➖ Pozo Extra: sin aciertos")

        lineas.append("")

    if not hubo_algun_acierto:
        lineas.append("😕 No hubo aciertos en ninguna jugada ni modalidad.")

    return "\n".join(lineas)


def enviar_telegram(mensaje):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise RuntimeError("Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID en las variables de entorno")

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    resp = requests.post(
        url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": mensaje,
            "parse_mode": "HTML",
        },
        timeout=20,
    )
    resp.raise_for_status()


def main():
    try:
        resultados = obtener_resultados()
    except Exception as e:
        print(f"Error obteniendo resultados: {e}", file=sys.stderr)
        # Avisamos por Telegram si algo se rompió, para no quedarnos en silencio
        try:
            enviar_telegram(f"⚠️ Error al controlar el Quini 6: {e}")
        except Exception:
            pass
        sys.exit(1)

    mensaje = formatear_mensaje(resultados)
    print(mensaje)
    enviar_telegram(mensaje)


if __name__ == "__main__":
    main()
