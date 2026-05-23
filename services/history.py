import json
import os
from config.settings import HISTORIAL_FILE, MAX_HISTORIAL

def cargar_historial():
    if os.path.exists(HISTORIAL_FILE):
        try:
            with open(HISTORIAL_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def guardar_historial(historial):
    try:
        with open(HISTORIAL_FILE, 'w', encoding='utf-8') as f:
            json.dump(historial[-MAX_HISTORIAL:], f, ensure_ascii=False, indent=2)
    except:
        pass

def añadir_entrada(historial, titulo, ruta, num_fotos):
    import datetime
    historial.append({
        'titulo': titulo,
        'fecha': datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
        'ruta': ruta,
        'fotos': num_fotos
    })
    return historial