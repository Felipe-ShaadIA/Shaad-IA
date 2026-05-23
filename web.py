import streamlit as st
import anthropic
import base64
import os
import io
import datetime
import requests
import tempfile
from PIL import Image
from docx import Document
from docx.shared import Pt, RGBColor
import re

try:
    import fitz
    PDF_DISPONIBLE = True
except ImportError:
    PDF_DISPONIBLE = False

st.set_page_config(
    page_title="Shaad IA · Apuntes Inteligentes",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="collapsed",
)

FEEDBACK_URL = "https://script.google.com/macros/s/AKfycbzwMjJAxwTqDmwMToomyDf_JIsg3hhmN5l902gp3yKiWSdTSpGuaH6fv-KRtblM9H6IVg/exec"

def get_secret(key, default=""):
    try:
        return st.secrets.get(key, default)
    except:
        return os.environ.get(key, default)

def get_api_key():
    return get_secret("ANTHROPIC_API_KEY")

def get_app_password():
    return get_secret("APP_PASSWORD", "shaad2026")

def get_tema():
    return st.session_state.get("tema", "oscuro")

def get_idioma_app():
    return st.session_state.get("idioma_app", "es")

TEXTOS = {
    "es": {
        "badge": "✦ IA para estudiantes",
        "slogan": "Transforma apuntes en conocimiento",
        "tab1": "✦ Transcriptor",
        "tab2": "🕐 Historial",
        "tab3": "⚙️ Ajustes",
        "tab4": "❓ Ayuda",
        "idioma": "🌐 Idioma",
        "nivel": "📊 Nivel",
        "tablas": "📋 Tablas/esquemas",
        "contexto_ph": "Ej: Historia, tema 4 — neocolonialismo…",
        "uploader": "📎 Arrastra aquí tus fotos o PDFs",
        "btn_transformar": "✦  Transformar apuntes",
        "descarga_txt": "⬇ Descargar .txt",
        "descarga_docx": "⬇ Descargar .docx",
        "sin_resumenes": "No hay resúmenes todavía. ¡Genera el primero!",
        "ajustes_titulo": "⚙️ Configuración avanzada",
        "modelo_label": "Modelo de Claude",
        "tema_label": "🎨 Tema visual",
        "idioma_app_label": "🌍 Idioma de la app",
        "guardar": "✦ Guardar ajustes",
        "ajustes_guardados": "✓ Ajustes guardados.",
        "ayuda_titulo": "❓ Cómo usar Shaad IA",
        "nombre_ph": "Tu nombre o alias para el feedback…",
        "opinion_ph": "¿Qué mejorarías? ¿Qué te gusta? ¿Qué falla?",
        "enviar_fb": "✦ Enviar feedback",
        "fb_ok": "✓ ¡Gracias por tu feedback!",
        "fb_error": "❌ Error al enviar. Inténtalo de nuevo.",
        "fb_vacio": "⚠️ Escribe tu opinión antes de enviar.",
        "footer": "Hecho con <span>♥</span> para estudiantes como tú &nbsp;·&nbsp; <strong>Shaad IA</strong> © 2026",
        "login_badge": "✦ Versión beta privada",
        "login_desc": "Versión beta privada. Introduce la contraseña para acceder.",
        "contrasena": "Contraseña",
        "contrasena_ph": "Introduce la contraseña...",
        "entrar": "✦  Entrar",
        "contrasena_error": "Contraseña incorrecta.",
        "aviso_foto": "⚠️ Sube al menos una foto o PDF.",
        "preparando": "Preparando…",
        "analizando": "Analizando imágenes…",
        "generando": "Generando resumen…",
        "listo": "✓ Listo",
    },
    "en": {
        "badge": "✦ AI for students",
        "slogan": "Transform notes into knowledge",
        "tab1": "✦ Transcriptor",
        "tab2": "🕐 History",
        "tab3": "⚙️ Settings",
        "tab4": "❓ Help",
        "idioma": "🌐 Language",
        "nivel": "📊 Level",
        "tablas": "📋 Tables/diagrams",
        "contexto_ph": "E.g.: History, topic 4 — neocolonialism…",
        "uploader": "📎 Drag your photos or PDFs here",
        "btn_transformar": "✦  Transform notes",
        "descarga_txt": "⬇ Download .txt",
        "descarga_docx": "⬇ Download .docx",
        "sin_resumenes": "No summaries yet. Generate your first one!",
        "ajustes_titulo": "⚙️ Advanced settings",
        "modelo_label": "Claude model",
        "tema_label": "🎨 Visual theme",
        "idioma_app_label": "🌍 App language",
        "guardar": "✦ Save settings",
        "ajustes_guardados": "✓ Settings saved.",
        "ayuda_titulo": "❓ How to use Shaad IA",
        "nombre_ph": "Your name or alias for feedback…",
        "opinion_ph": "What would you improve? What do you like? What's wrong?",
        "enviar_fb": "✦ Send feedback",
        "fb_ok": "✓ Thanks for your feedback!",
        "fb_error": "❌ Error sending. Try again.",
        "fb_vacio": "⚠️ Write your opinion before sending.",
        "footer": "Made with <span>♥</span> for students like you &nbsp;·&nbsp; <strong>Shaad IA</strong> © 2026",
        "login_badge": "✦ Private beta version",
        "login_desc": "Private beta version. Enter the password to access.",
        "contrasena": "Password",
        "contrasena_ph": "Enter the password...",
        "entrar": "✦  Enter",
        "contrasena_error": "Incorrect password.",
        "aviso_foto": "⚠️ Upload at least one photo or PDF.",
        "preparando": "Preparing…",
        "analizando": "Analyzing images…",
        "generando": "Generating summary…",
        "listo": "✓ Done",
    },
    "gl": {
        "badge": "✦ IA para estudantes",
        "slogan": "Transforma apuntes en coñecemento",
        "tab1": "✦ Transcritor",
        "tab2": "🕐 Historial",
        "tab3": "⚙️ Axustes",
        "tab4": "❓ Axuda",
        "idioma": "🌐 Idioma",
        "nivel": "📊 Nivel",
        "tablas": "📋 Táboas/esquemas",
        "contexto_ph": "Ex: Historia, tema 4 — neocolonialismo…",
        "uploader": "📎 Arrastra aquí as túas fotos ou PDFs",
        "btn_transformar": "✦  Transformar apuntes",
        "descarga_txt": "⬇ Descargar .txt",
        "descarga_docx": "⬇ Descargar .docx",
        "sin_resumenes": "Non hai resumos aínda. ¡Xera o primeiro!",
        "ajustes_titulo": "⚙️ Configuración avanzada",
        "modelo_label": "Modelo de Claude",
        "tema_label": "🎨 Tema visual",
        "idioma_app_label": "🌍 Idioma da app",
        "guardar": "✦ Gardar axustes",
        "ajustes_guardados": "✓ Axustes gardados.",
        "ayuda_titulo": "❓ Como usar Shaad IA",
        "nombre_ph": "O teu nome ou alias para o feedback…",
        "opinion_ph": "Que mellorarías? Que che gusta? Que falla?",
        "enviar_fb": "✦ Enviar feedback",
        "fb_ok": "✓ Grazas polo teu feedback!",
        "fb_error": "❌ Erro ao enviar. Téntao de novo.",
        "fb_vacio": "⚠️ Escribe a túa opinión antes de enviar.",
        "footer": "Feito con <span>♥</span> para estudantes coma ti &nbsp;·&nbsp; <strong>Shaad IA</strong> © 2026",
        "login_badge": "✦ Versión beta privada",
        "login_desc": "Versión beta privada. Introduce o contrasinal para acceder.",
        "contrasena": "Contrasinal",
        "contrasena_ph": "Introduce o contrasinal...",
        "entrar": "✦  Entrar",
        "contrasena_error": "Contrasinal incorrecto.",
        "aviso_foto": "⚠️ Sube polo menos unha foto ou PDF.",
        "preparando": "Preparando…",
        "analizando": "Analizando imaxes…",
        "generando": "Xerando resumo…",
        "listo": "✓ Listo",
    }
}

def t(key):
    idioma = get_idioma_app()
    return TEXTOS.get(idioma, TEXTOS["es"]).get(key, TEXTOS["es"].get(key, key))

def get_css():
    tema = get_tema()
    if tema == "claro":
        return """
:root {
    --bg-base:        #f8f7ff;
    --bg-surface:     #ede9ff;
    --bg-card:        #ffffff;
    --border:         rgba(124, 58, 237, 0.15);
    --border-strong:  rgba(124, 58, 237, 0.35);
    --purple-bright:  #7c3aed;
    --purple-mid:     #6d28d9;
    --purple-soft:    rgba(124, 58, 237, 0.08);
    --green-bright:   #16a34a;
    --green-soft:     rgba(22, 163, 74, 0.08);
    --text-primary:   #1a1a2e;
    --text-secondary: #4a4a6a;
    --text-muted:     #9090b0;
    --radius-card:    16px;
    --radius-btn:     10px;
    --shadow-card:    0 4px 24px rgba(0,0,0,0.08), 0 0 0 1px var(--border);
    --shadow-glow-p:  0 0 30px rgba(124,58,237,0.10);
    --shadow-glow-g:  0 0 30px rgba(22,163,74,0.08);
    --font-display:   'Syne', sans-serif;
    --font-body:      'DM Sans', sans-serif;
}
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-base) !important;
}
[data-testid="stAppViewContainer"] {
    background-image:
        radial-gradient(ellipse 60% 40% at 50% -10%, rgba(124,58,237,0.08) 0%, transparent 70%);
}
"""
    else:
        return """
:root {
    --bg-base:        #0a0a0f;
    --bg-surface:     #0f0f1a;
    --bg-card:        #13131f;
    --border:         rgba(138, 92, 246, 0.18);
    --border-strong:  rgba(138, 92, 246, 0.40);
    --purple-bright:  #a855f7;
    --purple-mid:     #7c3aed;
    --purple-soft:    rgba(168, 85, 247, 0.12);
    --green-bright:   #4ade80;
    --green-soft:     rgba(74, 222, 128, 0.10);
    --text-primary:   #f0eeff;
    --text-secondary: #a89fc0;
    --text-muted:     #5c556e;
    --radius-card:    16px;
    --radius-btn:     10px;
    --shadow-card:    0 4px 32px rgba(0,0,0,0.45), 0 0 0 1px var(--border);
    --shadow-glow-p:  0 0 40px rgba(168,85,247,0.15);
    --shadow-glow-g:  0 0 40px rgba(74,222,128,0.12);
    --font-display:   'Syne', sans-serif;
    --font-body:      'DM Sans', sans-serif;
}
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-base) !important;
}
[data-testid="stAppViewContainer"] {
    background-image:
        radial-gradient(ellipse 60% 40% at 50% -10%, rgba(124,58,237,0.20) 0%, transparent 70%),
        radial-gradient(ellipse 40% 30% at 90% 80%, rgba(34,197,94,0.08) 0%, transparent 60%);
}
"""

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

{get_css()}

html, body, [data-testid="stAppViewContainer"] {{
    font-family: var(--font-body) !important;
    color: var(--text-primary) !important;
}}
[data-testid="stHeader"], [data-testid="stToolbar"], footer {{ display: none !important; }}
.block-container {{ max-width: 720px !important; padding: 2rem 1.5rem 4rem !important; }}

.hero-wrap {{ text-align: center; padding: 1.5rem 0 1rem; }}
.hero-badge {{
    display: inline-flex; align-items: center; gap: 6px;
    background: var(--purple-soft); border: 1px solid var(--border-strong);
    border-radius: 999px; padding: 4px 14px; font-size: 0.70rem;
    letter-spacing: 0.12em; text-transform: uppercase; color: var(--purple-bright);
    font-family: var(--font-display); font-weight: 600; margin-bottom: 0.8rem;
}}
.hero-title {{
    font-family: var(--font-display) !important;
    font-size: clamp(2.4rem, 6vw, 3.8rem) !important;
    font-weight: 800 !important; line-height: 1.05 !important;
    background: linear-gradient(135deg, #c084fc 0%, #a855f7 35%, #4ade80 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin: 0 0 0.4rem !important; letter-spacing: -0.02em;
}}
.hero-sub {{
    font-family: var(--font-display); font-size: 0.78rem;
    letter-spacing: 0.20em; text-transform: uppercase; color: var(--text-muted);
}}
.card {{
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius-card); padding: 1.4rem 1.6rem;
    box-shadow: var(--shadow-card); margin-bottom: 1rem;
    transition: border-color 0.25s, box-shadow 0.25s;
}}
.card:hover {{ border-color: var(--border-strong); box-shadow: var(--shadow-card), var(--shadow-glow-p); }}
.card-label {{
    display: flex; align-items: center; gap: 8px;
    font-family: var(--font-display); font-weight: 700; font-size: 0.78rem;
    letter-spacing: 0.10em; text-transform: uppercase; color: var(--text-secondary);
    margin-bottom: 0.8rem;
}}
.card-label .dot {{
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--purple-bright); box-shadow: 0 0 8px var(--purple-bright);
}}

[data-testid="stTextInput"] input {{
    background: var(--bg-surface) !important; border: 1px solid var(--border) !important;
    border-radius: 10px !important; color: var(--text-primary) !important;
    font-family: var(--font-body) !important; padding: 0.75rem 1rem !important;
}}
[data-testid="stTextInput"] input:focus {{
    border-color: var(--purple-bright) !important;
    box-shadow: 0 0 0 3px rgba(168,85,247,0.15) !important;
}}
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label {{ color: var(--text-secondary) !important; font-size: 0.88rem !important; }}
[data-testid="stTextArea"] textarea {{
    background: var(--bg-surface) !important; border: 1px solid var(--border) !important;
    border-radius: 10px !important; color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
}}

[data-testid="stFileUploader"] {{
    border: 2px dashed rgba(138,92,246,0.4) !important;
    border-radius: var(--radius-card) !important;
    background: var(--bg-surface) !important; padding: 1rem !important;
}}
[data-testid="stFileUploader"] * {{ color: var(--text-secondary) !important; }}
[data-testid="stFileUploader"] svg {{ fill: var(--purple-bright) !important; }}
section[data-testid="stFileUploaderDropzone"] {{
    background: var(--bg-surface) !important; border: none !important;
}}

[data-testid="stSelectbox"] > div > div {{
    background: var(--bg-surface) !important; border: 1px solid var(--border) !important;
    border-radius: 10px !important; color: var(--text-primary) !important;
}}
[data-testid="stSelectbox"] label {{ color: var(--text-secondary) !important; font-size: 0.88rem !important; }}
[data-baseweb="select"] * {{ color: var(--text-primary) !important; }}
[data-baseweb="popover"] {{
    background: var(--bg-card) !important; border: 1px solid var(--border-strong) !important;
    border-radius: 12px !important;
}}
[role="option"]:hover {{ background: var(--purple-soft) !important; }}

[data-testid="stButton"] > button {{
    background: linear-gradient(135deg, var(--purple-mid), var(--purple-bright)) !important;
    color: #fff !important; border: none !important; border-radius: var(--radius-btn) !important;
    font-family: var(--font-display) !important; font-weight: 700 !important;
    font-size: 0.90rem !important; padding: 0.70rem 2rem !important; width: 100% !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.40) !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
}}
[data-testid="stButton"] > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(124,58,237,0.55) !important;
}}

[data-testid="stDownloadButton"] > button {{
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: 10px !important;
    font-family: var(--font-display) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.6rem 1.2rem !important;
    width: 100% !important;
    box-shadow: none !important;
    transition: all 0.2s !important;
}}
[data-testid="stDownloadButton"] > button:hover {{
    background: var(--purple-soft) !important;
    border-color: var(--purple-bright) !important;
    transform: translateY(-1px) !important;
    color: var(--text-primary) !important;
}}

[data-testid="stAlert"] {{
    background: var(--bg-card) !important; border-radius: 12px !important;
    border: 1px solid var(--border) !important;
}}
[data-testid="stExpander"] {{
    background: var(--bg-card) !important; border: 1px solid var(--border) !important;
    border-radius: var(--radius-card) !important;
}}
[data-testid="stExpander"] > div > div {{ background: var(--bg-card) !important; }}
[data-testid="stExpander"] summary {{
    color: var(--text-secondary) !important; font-family: var(--font-display) !important;
}}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {{
    color: var(--text-primary) !important; font-family: var(--font-body) !important;
    line-height: 1.7 !important;
}}
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {{
    font-family: var(--font-display) !important; color: var(--text-primary) !important;
}}
[data-testid="stImage"] img {{ border-radius: 12px !important; border: 1px solid var(--border) !important; }}
hr {{ border-color: var(--border) !important; }}
::-webkit-scrollbar {{ width: 6px; }}
::-webkit-scrollbar-track {{ background: var(--bg-base); }}
::-webkit-scrollbar-thumb {{ background: var(--border-strong); border-radius: 3px; }}

.result-card {{
    background: linear-gradient(135deg, rgba(74,222,128,0.05) 0%, var(--bg-card) 50%);
    border: 1px solid rgba(74,222,128,0.25); border-radius: var(--radius-card);
    padding: 1.6rem 1.8rem; box-shadow: var(--shadow-card), var(--shadow-glow-g);
    margin-top: 1.2rem;
}}
.result-badge {{
    background: var(--green-soft); border: 1px solid rgba(74,222,128,0.30);
    color: var(--green-bright); border-radius: 999px; padding: 3px 12px;
    font-size: 0.70rem; letter-spacing: 0.10em; text-transform: uppercase;
    font-family: var(--font-display); font-weight: 600; margin-bottom: 1rem;
    display: inline-block;
}}
.feedback-item {{
    background: var(--bg-surface); border: 1px solid var(--border);
    border-radius: 10px; padding: 0.8rem 1rem; margin-bottom: 0.5rem;
}}
.footer-custom {{
    text-align: center; padding: 2rem 0 0; color: var(--text-muted);
    font-size: 0.78rem; font-family: var(--font-body);
}}
.footer-custom span {{ color: #f43f5e; }}
.footer-custom strong {{ color: var(--purple-bright); }}

[data-testid="stTabs"] [data-baseweb="tab-list"] {{
    background: var(--bg-surface) !important;
    border-radius: 12px !important; padding: 4px !important;
    border: 1px solid var(--border) !important; gap: 2px !important;
}}
[data-testid="stTabs"] [data-baseweb="tab"] {{
    background: transparent !important; color: var(--text-muted) !important;
    border-radius: 8px !important; font-family: var(--font-display) !important;
    font-weight: 600 !important; font-size: 0.85rem !important; border: none !important;
}}
[data-testid="stTabs"] [aria-selected="true"] {{
    background: var(--purple-soft) !important; color: var(--purple-bright) !important;
    border: 1px solid var(--border-strong) !important;
}}
[data-testid="stToggle"] label {{ color: var(--text-secondary) !important; }}
</style>
""", unsafe_allow_html=True)


def encode_image(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def pdf_a_imagenes(archivo_pdf):
    imagenes = []
    if not PDF_DISPONIBLE:
        st.error("❌ PDF no disponible.")
        return imagenes
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(archivo_pdf.read())
        tmp_path = tmp.name
    doc = fitz.open(tmp_path)
    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        imagenes.append(img)
    doc.close()
    os.unlink(tmp_path)
    return imagenes

def transcribir(imagenes, idioma, nivel, contexto, esquemas, modelo):
    api_key = get_api_key()
    if not api_key:
        st.error("❌ No se encontró la API key de Anthropic.")
        return ""
    client = anthropic.Anthropic(api_key=api_key)
    lineas = {"Breve (2-3 líneas)": "2-3", "Medio (4-6 líneas)": "4-6", "Detallado (7-10 líneas)": "7-10"}.get(nivel, "4-6")
    ctx = f"\nContexto adicional: {contexto}" if contexto.strip() else ""
    sin_esquemas = "\nNO uses tablas, esquemas visuales ni diagramas. Solo texto estructurado." if not esquemas else ""

    system = f"""Eres un experto en crear apuntes de estudio para estudiantes de Bachillerato.
Responde SIEMPRE en {idioma}.

ESTRUCTURA: Si las imágenes contienen varios temas o apartados distintos, organiza el resumen separando cada tema con su título numerado:
# 6. Título del tema
[resumen]
---
# 7. Título del tema
[resumen]

FORMATO:
- Título del tema: # Numero. Titulo
- Apartados: ### 1. Nombre: explicación en el mismo renglón
- Conceptos clave: **concepto**

CALIDAD:
- Resumen COMPACTO: cada apartado en {lineas} líneas máximo
- Solo información esencial: definiciones clave, datos importantes, clasificaciones principales
- Elimina ejemplos secundarios y repeticiones
- Lenguaje académico directo para memorizar en examen
- NO inventes información
- NO pongas introducciones ni conclusiones inventadas{sin_esquemas}{ctx}"""

    content = [{"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": encode_image(img)}} for img in imagenes]
    content.append({"type": "text", "text": "Analiza todas las imágenes y organiza el resumen por temas/apartados detectados automáticamente."})

    resp = client.messages.create(
        model=modelo, max_tokens=3000, system=system,
        messages=[{"role": "user", "content": content}]
    )
    return resp.content[0].text

def extraer_titulo(resumen, contexto):
    if contexto.strip():
        return contexto.strip()[:60]
    for linea in resumen.split('\n'):
        linea = linea.strip()
        if linea.startswith('# '):
            titulo = linea[2:].strip()
            return re.sub(r'[\\/*?:"<>|]', '', titulo)[:60]
    return f"Resumen {datetime.datetime.now().strftime('%d/%m %H:%M')}"

def crear_docx(resumen):
    doc = Document()
    NEGRO = RGBColor(0x00, 0x00, 0x00)
    for s in doc.sections:
        s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Pt(56)
    doc.styles['Normal'].font.name = 'Liberation Serif'
    doc.styles['Normal'].font.size = Pt(12)

    def agregar_negritas(p, texto):
        for i, parte in enumerate(re.split(r'\*\*(.*?)\*\*', texto)):
            run = p.add_run(parte)
            run.font.name = 'Liberation Serif'
            run.font.size = Pt(12)
            run.font.color.rgb = NEGRO
            if i % 2 == 1:
                run.bold = True

    for linea in resumen.split('\n'):
        linea = linea.strip()
        if not linea:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(2)
        elif re.match(r'^# ', linea):
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.line_spacing = Pt(17)
            run = p.add_run(linea[2:].strip())
            run.bold = True; run.underline = True
            run.font.name = 'Liberation Serif'; run.font.size = Pt(13); run.font.color.rgb = NEGRO
        elif re.match(r'^## ', linea):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = Pt(17)
            run = p.add_run(linea[3:].strip())
            run.bold = True; run.underline = True
            run.font.name = 'Liberation Serif'; run.font.size = Pt(12); run.font.color.rgb = NEGRO
        elif re.match(r'^### ', linea):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = Pt(17)
            texto_ap = linea[4:].strip()
            m = re.match(r'^([^:]+):(.*)', texto_ap)
            if m:
                run = p.add_run(m.group(1).strip() + ': ')
                run.bold = True; run.underline = True
                run.font.name = 'Liberation Serif'; run.font.size = Pt(12); run.font.color.rgb = NEGRO
                agregar_negritas(p, m.group(2).strip())
            else:
                run = p.add_run(texto_ap)
                run.bold = True; run.underline = True
                run.font.name = 'Liberation Serif'; run.font.size = Pt(12); run.font.color.rgb = NEGRO
        elif re.match(r'^[-] ', linea):
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_after = Pt(2); p.paragraph_format.line_spacing = Pt(17)
            agregar_negritas(p, linea[2:].strip())
        elif re.match(r'^\d+\. ', linea):
            p = doc.add_paragraph(style='List Number')
            p.paragraph_format.space_after = Pt(2); p.paragraph_format.line_spacing = Pt(17)
            agregar_negritas(p, re.sub(r'^\d+\. ', '', linea))
        elif linea == '---':
            doc.add_paragraph()
        else:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(5); p.paragraph_format.line_spacing = Pt(17)
            agregar_negritas(p, linea)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()

def guardar_en_historial(titulo, resumen):
    if "historial" not in st.session_state:
        st.session_state.historial = []
    st.session_state.historial.insert(0, {
        "titulo": titulo, "resumen": resumen,
        "fecha": datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    })
    if len(st.session_state.historial) > 20:
        st.session_state.historial = st.session_state.historial[:20]

def enviar_feedback(usuario, opinion, puntuacion):
    try:
        requests.post(FEEDBACK_URL, json={
            "fecha": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
            "usuario": usuario, "opinion": opinion, "puntuacion": str(puntuacion)
        }, timeout=5)
        return True
    except:
        return False

# ── Login ─────────────────────────────────────────────────────────────────────
def check_password():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if not st.session_state.autenticado:
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                logo_b64 = base64.b64encode(f.read()).decode()
            st.markdown(f'<div style="text-align:center;margin-bottom:0.5rem"><img src="data:image/png;base64,{logo_b64}" style="width:80px;height:80px;object-fit:contain;"></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="hero-wrap">
            <div class="hero-badge">{t('login_badge')}</div>
            <h1 class="hero-title">Shaad IA</h1>
            <p class="hero-sub">{t('slogan')}</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f'<div class="card"><div class="card-label"><span class="dot"></span>🔒 &nbsp;Acceso privado</div><p style="color:var(--text-secondary);font-size:0.9rem;margin-bottom:1rem;">{t("login_desc")}</p></div>', unsafe_allow_html=True)
        password = st.text_input(t("contrasena"), type="password", placeholder=t("contrasena_ph"))
        if st.button(t("entrar")):
            if password == get_app_password():
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error(t("contrasena_error"))
        return False
    return True

if not check_password():
    st.stop()

# ── Hero ──────────────────────────────────────────────────────────────────────
logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<div style="text-align:center;margin:1rem 0 0.5rem"><img src="data:image/png;base64,{logo_b64}" style="width:90px;height:90px;object-fit:contain;"></div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="hero-wrap">
    <div class="hero-badge">{t('badge')}</div>
    <h1 class="hero-title">Shaad IA</h1>
    <p class="hero-sub">{t('slogan')}</p>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([t("tab1"), t("tab2"), t("tab3"), t("tab4")])

# ── TAB 1 ─────────────────────────────────────────────────────────────────────
with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        idioma = st.selectbox(t("idioma"), ["castellano", "galego", "català", "euskara", "english", "français", "português", "deutsch", "italiano"])
    with col2:
        nivel = st.selectbox(t("nivel"), ["Breve (2-3 líneas)", "Medio (4-6 líneas)", "Detallado (7-10 líneas)"], index=1)
    with col3:
        esquemas = st.toggle(t("tablas"), value=False)

    contexto = st.text_input("ctx", placeholder=t("contexto_ph"), label_visibility="collapsed")
    MAX_FOTOS = 5
    archivos = st.file_uploader(t("uploader"), type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True)
    if archivos and len(archivos) > MAX_FOTOS:
        st.warning(f"⚠️ Máximo {MAX_FOTOS} archivos por resumen. Se usarán los primeros {MAX_FOTOS}.")
        archivos = archivos[:MAX_FOTOS]

    imagenes_procesadas = []
    if archivos:
        for archivo in archivos:
            if archivo.type == "application/pdf":
                with st.spinner(f"PDF: {archivo.name}..."):
                    imagenes_procesadas.extend(pdf_a_imagenes(archivo))
            else:
                imagenes_procesadas.append(Image.open(archivo))
        if imagenes_procesadas:
            cols = st.columns(min(len(imagenes_procesadas), 4))
            for i, img in enumerate(imagenes_procesadas[:4]):
                with cols[i % 4]:
                    st.image(img, use_container_width=True)
            if len(imagenes_procesadas) > 4:
                st.caption(f"... +{len(imagenes_procesadas)-4}")

    modelo_guardado = st.session_state.get("modelo_guardado", "claude-haiku-4-5")
    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

    if st.button(t("btn_transformar"), type="primary"):
        if not imagenes_procesadas:
            st.warning(t("aviso_foto"))
        else:
            barra = st.progress(0, text=t("preparando"))
            barra.progress(20, text=t("analizando"))
            resultado = transcribir(imagenes_procesadas, idioma, nivel, contexto, esquemas, modelo_guardado)
            barra.progress(90, text=t("generando"))
            if resultado:
                barra.progress(100, text=t("listo"))
                titulo = extraer_titulo(resultado, contexto)
                guardar_en_historial(titulo, resultado)
                st.markdown(f'<div class="result-card"><span class="result-badge">✓ {titulo}</span></div>', unsafe_allow_html=True)
                st.markdown(resultado)
                docx_bytes = crear_docx(resultado)
                c1, c2 = st.columns(2)
                with c1:
                    st.download_button(t("descarga_txt"), data=resultado, file_name=f"{titulo}.txt", mime="text/plain", key="dl_txt")
                with c2:
                    st.download_button(t("descarga_docx"), data=docx_bytes, file_name=f"{titulo}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key="dl_docx")

# ── TAB 2 ─────────────────────────────────────────────────────────────────────
with tab2:
    historial = st.session_state.get("historial", [])
    if not historial:
        st.markdown(f'<p style="color:var(--text-muted);text-align:center;padding:2rem 0;">{t("sin_resumenes")}</p>', unsafe_allow_html=True)
    else:
        for i, item in enumerate(historial):
            with st.expander(f"📄 {item['titulo']} — {item['fecha']}"):
                st.markdown(item['resumen'])
                c1, c2 = st.columns(2)
                with c1:
                    st.download_button(t("descarga_txt"), data=item['resumen'], file_name=f"{item['titulo']}.txt", mime="text/plain", key=f"h_txt_{i}")
                with c2:
                    st.download_button(t("descarga_docx"), data=crear_docx(item['resumen']), file_name=f"{item['titulo']}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=f"h_docx_{i}")

# ── TAB 3 ─────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown(f'<div class="card-label"><span class="dot"></span>{t("ajustes_titulo")}</div>', unsafe_allow_html=True)

    st.markdown(f"**{t('modelo_label')}**")
    modelo = st.selectbox("modelo", ["claude-haiku-4-5", "claude-sonnet-4-5", "claude-opus-4-5"], index=1,
        format_func=lambda x: {"claude-haiku-4-5": "⚡ Haiku — Más rápido", "claude-sonnet-4-5": "⚖️ Sonnet — Equilibrado", "claude-opus-4-5": "🎯 Opus — Máxima calidad"}[x],
        label_visibility="collapsed")

    st.markdown(f"**{t('tema_label')}**")
    tema = st.selectbox("tema", ["oscuro", "claro"], index=0 if get_tema() == "oscuro" else 1,
        format_func=lambda x: {"oscuro": "🌙 Oscuro", "claro": "☀️ Claro"}[x],
        label_visibility="collapsed")

    st.markdown(f"**{t('idioma_app_label')}**")
    idioma_app = st.selectbox("idioma_app", ["es", "en", "gl"], index=["es","en","gl"].index(get_idioma_app()),
        format_func=lambda x: {"es": "🇪🇸 Castellano", "en": "🇬🇧 English", "gl": "🏴 Galego"}[x],
        label_visibility="collapsed")

    if st.button(t("guardar")):
        st.session_state.modelo_guardado = modelo
        st.session_state.tema = tema
        st.session_state.idioma_app = idioma_app
        st.success(t("ajustes_guardados"))
        st.rerun()

# ── TAB 4 ─────────────────────────────────────────────────────────────────────
with tab4:
    pasos_es = [
        ("1️⃣", "Sube tus fotos o PDF", "Arrastra las imágenes o un PDF de tus apuntes."),
        ("2️⃣", "Elige idioma y nivel", "Selecciona el idioma y el nivel de detalle."),
        ("3️⃣", "Añade contexto", "Opcional pero recomendado: escribe el tema para mejores resultados."),
        ("4️⃣", "Genera el resumen", "Pulsa el botón y espera unos segundos."),
        ("5️⃣", "Descarga", "Descarga en .txt o .docx con formato correcto."),
        ("💡", "Consejo", "Si subes varias fotos de temas distintos, Shaad IA las organiza automáticamente por apartados."),
    ]
    for icono, titulo_paso, desc in pasos_es:
        st.markdown(f'<div class="feedback-item"><strong style="color:var(--purple-bright)">{icono} {titulo_paso}</strong><br><span style="color:var(--text-secondary);font-size:0.9rem">{desc}</span></div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="card-label"><span class="dot"></span>👤 &nbsp;Tu nombre</div>', unsafe_allow_html=True)
    nombre_usuario = st.text_input("nombre", placeholder=t("nombre_ph"), label_visibility="collapsed", value=st.session_state.get("nombre_usuario", ""))
    if nombre_usuario:
        st.session_state.nombre_usuario = nombre_usuario

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="card-label"><span class="dot"></span>💬 &nbsp;Deja tu opinión</div>', unsafe_allow_html=True)
    opinion = st.text_area("opinion", placeholder=t("opinion_ph"), label_visibility="collapsed")
    puntuacion = st.select_slider("Puntuación", options=[1, 2, 3, 4, 5], value=5)

    if st.button(t("enviar_fb")):
        if opinion.strip():
            with st.spinner("Enviando…"):
                ok = enviar_feedback(st.session_state.get("nombre_usuario", "Anónimo"), opinion, puntuacion)
            st.success(t("fb_ok")) if ok else st.error(t("fb_error"))
        else:
            st.warning(t("fb_vacio"))

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f'<div class="footer-custom">{t("footer")}</div>', unsafe_allow_html=True)