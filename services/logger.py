import os
import datetime
from config.settings import BASE_DIR

LOG_FILE = os.path.join(BASE_DIR, "shaad_logs.txt")

def log_info(mensaje):
    _escribir("INFO", mensaje)

def log_error(mensaje):
    _escribir("ERROR", mensaje)

def log_warning(mensaje):
    _escribir("WARNING", mensaje)

def _escribir(nivel, mensaje):
    try:
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        linea = f"[{timestamp}] [{nivel}] {mensaje}\n"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(linea)
    except:
        pass

def leer_logs(ultimas=50):
    try:
        if not os.path.exists(LOG_FILE):
            return "No hay logs todavía."
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lineas = f.readlines()
        return "".join(lineas[-ultimas:])
    except:
        return "Error leyendo logs."