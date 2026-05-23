import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "Shaad IA"
APP_VERSION = "1.0.0"
APP_SLOGAN = "Transforma apuntes en conocimiento ✨"

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
APP_PASSWORD = os.getenv("APP_PASSWORD", "shaad2026")

MODELO_VISION = "meta-llama/llama-4-scout-17b-16e-instruct"
MODELO_TEXTO = "llama-3.3-70b-versatile"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORIAL_FILE = os.path.join(BASE_DIR, "historial.json")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

DEFAULT_IDIOMA = "castellano"
DEFAULT_NIVEL = "medio"
DEFAULT_CARPETA = os.path.expanduser("~\\Downloads")

MAX_TOKENS_VISION = 4000
MAX_TOKENS_TEXTO = 2000
MAX_CHARS_POR_TROZO = 2500
MAX_HISTORIAL = 20