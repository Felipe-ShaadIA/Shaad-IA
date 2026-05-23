import re
import time
from services.groq_client import get_client
from config.settings import MODELO_TEXTO, MAX_TOKENS_TEXTO, MAX_CHARS_POR_TROZO

def limpiar_salida(texto):
    texto = re.sub(r'\*\*([^*\n]+)\*\*:', r'\1:', texto)
    texto = re.sub(r'\*\*([^*\n]+)\*\*', r'\1', texto)
    return texto

def limpiar_entrada(texto):
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    texto = re.sub(r' {2,}', ' ', texto)
    lineas = [l for l in texto.split('\n') if len(l.strip()) > 2 or l.strip() == '']
    return '\n'.join(lineas).strip()

def get_lineas_por_nivel(nivel):
    if nivel == "corto":
        return "2-3"
    elif nivel == "largo":
        return "7-10"
    return "4-6"

def resumir_trozo(client, trozo, idioma, nivel, reintentos=3):
    lineas = get_lineas_por_nivel(nivel)
    trozo_limpio = limpiar_entrada(trozo)

    prompt = f"""Eres un experto en crear apuntes de estudio. Resume el siguiente texto.

IDIOMA: Escribe TODO en {idioma}. Nunca mezcles idiomas.

FORMATO OBLIGATORIO:
- Titulo del tema: # Numero. Titulo (traducido a {idioma})
- Introduccion general si existe: parrafo normal
- Cada apartado numerado: ### 1. Nombre: desarrollo completo
- Conceptos clave: **concepto**

REGLAS DE CALIDAD:
- Nivel de detalle {nivel}: cada apartado en {lineas} lineas
- Incluye TODA la informacion relevante: definiciones, ejemplos, clasificaciones
- NO omitas ningun apartado del texto original
- Si un apartado tiene subapartados incluyelos todos
- NO inventes informacion que no este en el texto
- NO pongas frases como "no se proporciona informacion"
- Reescribe con tus palabras no copies literalmente
- Los apartados deben estar completos y bien explicados

TEXTO:
{trozo_limpio}"""

    ultimo_error = None
    for intento in range(reintentos):
        try:
            respuesta = client.chat.completions.create(
                model=MODELO_TEXTO,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=MAX_TOKENS_TEXTO,
                timeout=90
            )
            return respuesta.choices[0].message.content.strip()
        except Exception as e:
            ultimo_error = e
            if intento < reintentos - 1:
                time.sleep(2 * (intento + 1))

    raise Exception(f"Error resumiendo tras {reintentos} intentos: {ultimo_error}")

def resumir(texto, idioma="castellano", nivel="medio", cancelar_flag=None, callback=None):
    client = get_client()
    texto_limpio = limpiar_entrada(texto)
    trozos = [texto_limpio[i:i+MAX_CHARS_POR_TROZO]
              for i in range(0, len(texto_limpio), MAX_CHARS_POR_TROZO)]
    resumenes = []

    for i, trozo in enumerate(trozos):
        if cancelar_flag and cancelar_flag():
            return ""
        if callback:
            callback(i + 1, len(trozos))
        resumen = resumir_trozo(client, trozo, idioma, nivel)
        resumenes.append(resumen)

    return limpiar_salida("\n\n".join(resumenes))

def extraer_titulo(texto):
    for linea in texto.split('\n'):
        linea = linea.strip()
        if linea.startswith('# '):
            t = linea[2:].strip()
            return re.sub(r'[\\/*?:"<>|]', '', t)[:50]
    return "resumen"