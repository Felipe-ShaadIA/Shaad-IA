import base64
import os
from io import BytesIO
from PIL import Image
from services.groq_client import get_client
from config.settings import MODELO_VISION, MAX_TOKENS_VISION

MAX_SIZE = (1600, 1600)
MAX_KB = 800

def comprimir_imagen(ruta_imagen):
    img = Image.open(ruta_imagen).convert("RGB")
    img.thumbnail(MAX_SIZE, Image.LANCZOS)
    buffer = BytesIO()
    calidad = 85
    while True:
        buffer.seek(0)
        buffer.truncate()
        img.save(buffer, format="JPEG", quality=calidad)
        if buffer.tell() < MAX_KB * 1024 or calidad <= 40:
            break
        calidad -= 10
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")

def transcribir_imagen(ruta_imagen, reintentos=3):
    client = get_client()
    ultimo_error = None

    for intento in range(reintentos):
        try:
            imagen_base64 = comprimir_imagen(ruta_imagen)
            respuesta = client.chat.completions.create(
                model=MODELO_VISION,
                messages=[{"role": "user", "content": [
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/jpeg;base64,{imagen_base64}"}},
                    {"type": "text", "text": """Transcribe TODO el texto de esta imagen con maxima precision.
Es una pagina de apuntes o libro de texto.
IMPORTANTE:
- Copia EXACTAMENTE lo que ves, sin omitir nada
- Mantén los numeros de apartados tal como aparecen (1. 2. 3. etc)
- Mantén los titulos tal como aparecen
- Separa cada parrafo con una linea en blanco
- NO interpretes ni resumas, solo transcribe"""}
                ]}],
                max_tokens=MAX_TOKENS_VISION,
                timeout=60
            )
            return respuesta.choices[0].message.content

        except Exception as e:
            ultimo_error = e
            if intento < reintentos - 1:
                import time
                time.sleep(2 * (intento + 1))

    raise Exception(f"Error tras {reintentos} intentos: {ultimo_error}")

def transcribir_varias(rutas, callback=None):
    resultados = []
    for i, ruta in enumerate(rutas):
        texto = transcribir_imagen(ruta)
        resultados.append(texto)
        if callback:
            callback(i + 1, len(rutas), texto)
    return resultados