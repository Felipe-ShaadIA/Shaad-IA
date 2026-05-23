import streamlit as st
import anthropic
import base64
import os
import io
import json
import datetime
import requests
import tempfile
from PIL import Image

try:
    import fitz  # PyMuPDF
    PDF_DISPONIBLE = True
except ImportError:
    PDF_DISPONIBLE = False

st.set_page_config(
    page_title="Shaad IA · Apuntes Inteligentes",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

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
    font-family: var(--font-body) !important;
    color: var(--text-primary) !important;
}
[data-testid="stAppViewContainer"] {
    background-image:
        radial-gradient(ellipse 60% 40% at 50% -10%, rgba(124,58,237,0.20) 0%, transparent 70%),
        radial-gradient(ellipse 40% 30% at 90% 80%, rgba(34,197,94,0.08) 0%, transparent 60%);
}
[data-testid="stHeader"], [data-testid="stToolbar"], footer { display: none !important; }
.block-container { max-width: 720px !important; padding: 2rem 1.5rem 4rem !important; }

.hero-wrap { text-align: center; padding: 1.5rem 0 1rem; }
.hero-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: var(--purple-soft); border: 1px solid var(--border-strong);
    border-radius: 999px; padding: 4px 14px; font-size: 0.70rem;
    letter-spacing: 0.12em; text-transform: uppercase; color: var(--purple-bright);
    font-family: var(--font-display); font-weight: 600; margin-bottom: 0.8rem;
}
.hero-title {
    font-family: var(--font-display) !important;
    font-size: clamp(2.4rem, 6vw, 3.8rem) !important;
    font-weight: 800 !important; line-height: 1.05 !important;
    background: linear-gradient(135deg, #c084fc 0%, #a855f7 35%, #4ade80 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin: 0 0 0.4rem !important; letter-spacing: -0.02em;
}
.hero-sub {
    font-family: var(--font-display); font-size: 0.78rem;
    letter-spacing: 0.20em; text-transform: uppercase; color: var(--text-muted);
}

.card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius-card); padding: 1.4rem 1.6rem;
    box-shadow: var(--shadow-card); margin-bottom: 1rem;
    transition: border-color 0.25s, box-shadow 0.25s;
}
.card:hover { border-color: var(--border-strong); box-shadow: var(--shadow-card), var(--shadow-glow-p); }
.card-label {
    display: flex; align-items: center; gap: 8px;
    font-family: var(--font-display); font-weight: 700; font-size: 0.78rem;
    letter-spacing: 0.10em; text-transform: uppercase; color: var(--text-secondary);
    margin-bottom: 0.8rem;
}
.card-label .dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--purple-bright); box-shadow: 0 0 8px var(--purple-bright);
}
.card-label .dot-green { background: var(--green-bright); box-shadow: 0 0 8px var(--green-bright); }

[data-testid="stTextInput"] input {
    background: var(--bg-surface) !important; border: 1px solid var(--border) !important;
    border-radius: 10px !important; color: var(--text-primary) !important;
    font-family: var(--font-body) !important; padding: 0.75rem 1rem !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--purple-bright) !important;
    box-shadow: 0 0 0 3px rgba(168,85,247,0.15) !important;
}
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label { color: var(--text-secondary) !important; font-size: 0.88rem !important; }
[data-testid="stTextArea"] textarea {
    background: var(--bg-surface) !important; border: 1px solid var(--border) !important;
    border-radius: 10px !important; color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
}

[data-testid="stFileUploader"] {
    border: 2px dashed var(--border) !important;
    border-radius: var(--radius-card) !important;
    background: var(--bg-surface) !important; padding: 1rem !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--purple-bright) !important;
    background: var(--purple-soft) !important;
}

[data-testid="stSelectbox"] > div > div {
    background: var(--bg-surface) !important; border: 1px solid var(--border) !important;
    border-radius: 10px !important; color: var(--text-primary) !important;
}
[data-testid="stSelectbox"] label { color: var(--text-secondary) !important; font-size: 0.88rem !important; }
[data-baseweb="select"] * { color: var(--text-primary) !important; }
[data-baseweb="popover"] {
    background: var(--bg-card) !important; border: 1px solid var(--border-strong) !important;
    border-radius: 12px !important;
}
[role="option"]:hover { background: var(--purple-soft) !important; }

[data-testid="stButton"] > button {
    background: linear-gradient(135deg, var(--purple-mid), var(--purple-bright)) !important;
    color: #fff !important; border: none !important; border-radius: var(--radius-btn) !important;
    font-family: var(--font-display) !important; font-weight: 700 !important;
    font-size: 0.90rem !important; padding: 0.70rem 2rem !important; width: 100% !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.40) !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
}
[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(124,58,237,0.55) !important;
}

[data-testid="stAlert"] {
    background: var(--bg-card) !important; border-radius: 12px !important;
    border: 1px solid var(--border) !important;
}
[data-testid="stExpander"] {
    background: var(--bg-card) !important; border: 1px solid var(--border) !important;
    border-radius: var(--radius-card) !important;
}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    color: var(--text-primary) !important; font-family: var(--font-body) !important;
    line-height: 1.7 !important;
}
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {
    font-family: var(--font-display) !important; color: var(--text-primary) !important;
}
[data-testid="stImage"] img { border-radius: 12px !important; border: 1px solid var(--border) !important; }
hr { border-color: var(--border) !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 3px; }

.result-card {
    background: linear-gradient(135deg, rgba(74,222,128,0.05) 0%, var(--bg-card) 50%);
    border: 1px solid rgba(74,222,128,0.25); border-radius: var(--radius-card);
    padding: 1.6rem 1.8rem; box-shadow: var(--shadow-card), var(--shadow-glow-g);
    margin-top: 1.2rem;
}
.result-badge {
    background: var(--green-soft); border: 1px solid rgba(74,222,128,0.30);
    color: var(--green-bright); border-radius: 999px; padding: 3px 12px;
    font-size: 0.70rem; letter-spacing: 0.10em; text-transform: uppercase;
    font-family: var(--font-display); font-weight: 600;
}
.historial-item {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 12px; padding: 1rem 1.2rem; margin-bottom: 0.6rem;
    transition: border-color 0.2s;
}
.historial-item:hover { border-color: var(--border-strong); }
.feedback-item {
    background: var(--bg-surface); border: 1px solid var(--border);
    border-radius: 10px; padding: 0.8rem 1rem; margin-bottom: 0.5rem;
}
.footer-custom {
    text-align: center; padding: 2rem 0 0; color: var(--text-muted);
    font-size: 0.78rem; font-family: var(--font-body);
}
.footer-custom span { color: #f43f5e; }
.footer-custom strong { color: var(--purple-bright); }

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: var(--bg-surface) !important;
    border-radius: 12px !important; padding: 4px !important;
    border: 1px solid var(--border) !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important; color: var(--text-muted) !important;
    border-radius: 8px !important; font-family: var(--font-display) !important;
    font-weight: 600 !important; font-size: 0.85rem !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: var(--purple-soft) !important;
    color: var(--purple-bright) !important;
    border: 1px solid var(--border-strong) !important;
}
</style>
""", unsafe_allow_html=True)

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

def encode_image(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def pdf_a_imagenes(archivo_pdf):
    imagenes = []
    if not PDF_DISPONIBLE:
        st.error("❌ PDF no disponible. Instala PyMuPDF.")
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
    ctx = f"\nContexto: {contexto}" if contexto.strip() else ""
    sin_esquemas = "\nNO uses tablas, esquemas visuales ni diagramas. Solo texto." if not esquemas else ""

    system = f"""Eres un experto en crear apuntes de estudio para Bachillerato.
Responde SIEMPRE en {idioma}.
Haz un resumen COMPACTO. Cada apartado en {lineas} líneas máximo.
Mantén solo la información esencial: definiciones clave, datos importantes, clasificaciones principales.
Elimina ejemplos secundarios, repeticiones y detalles innecesarios.
Usa lenguaje académico directo pensado para memorizar en examen.
NO inventes información. NO pongas introducciones ni conclusiones inventadas.{sin_esquemas}{ctx}"""

    content = [{"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": encode_image(img)}} for img in imagenes]
    content.append({"type": "text", "text": "Resume el contenido de estos apuntes de forma compacta."})

    resp = client.messages.create(
        model=modelo,
        max_tokens=2048,
        system=system,
        messages=[{"role": "user", "content": content}]
    )
    return resp.content[0].text

def guardar_en_historial(titulo, resumen):
    if "historial" not in st.session_state:
        st.session_state.historial = []
    st.session_state.historial.insert(0, {
        "titulo": titulo,
        "resumen": resumen,
        "fecha": datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    })
    if len(st.session_state.historial) > 20:
        st.session_state.historial = st.session_state.historial[:20]

def enviar_feedback(usuario, opinion, puntuacion):
    try:
        requests.post(FEEDBACK_URL, json={
            "fecha": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
            "usuario": usuario,
            "opinion": opinion,
            "puntuacion": puntuacion
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

        st.markdown("""
        <div class="hero-wrap">
            <div class="hero-badge">✦ Versión beta privada</div>
            <h1 class="hero-title">Shaad IA</h1>
            <p class="hero-sub">Transforma apuntes en conocimiento</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="card-label"><span class="dot"></span>🔒 &nbsp;Acceso privado</div><p style="color:var(--text-secondary);font-size:0.9rem;margin-bottom:1rem;">Versión beta privada. Introduce la contraseña para acceder.</p></div>', unsafe_allow_html=True)
        password = st.text_input("Contraseña", type="password", placeholder="Introduce la contraseña...")
        if st.button("✦  Entrar"):
            if password == get_app_password():
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
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

st.markdown("""
<div class="hero-wrap">
    <div class="hero-badge">✦ IA para estudiantes</div>
    <h1 class="hero-title">Shaad IA</h1>
    <p class="hero-sub">Transforma apuntes en conocimiento</p>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["✦ Transcriptor", "🕐 Historial", "⚙️ Ajustes", "❓ Ayuda"])

# ── TAB 1: TRANSCRIPTOR ───────────────────────────────────────────────────────
with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        idioma = st.selectbox("🌐 Idioma", ["castellano", "galego", "català", "euskara", "english", "français", "português", "deutsch", "italiano"])
    with col2:
        nivel = st.selectbox("📊 Nivel", ["Breve (2-3 líneas)", "Medio (4-6 líneas)", "Detallado (7-10 líneas)"], index=1)
    with col3:
        esquemas = st.toggle("📋 Tablas/esquemas", value=False)

    contexto = st.text_input("Contexto opcional", placeholder="Ej: Historia, tema 4 — neocolonialismo…", label_visibility="collapsed")

    archivos = st.file_uploader(
        "Sube fotos o PDFs de tus apuntes",
        type=["jpg", "jpeg", "png", "pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    imagenes_procesadas = []
    if archivos:
        for archivo in archivos:
            if archivo.type == "application/pdf":
                with st.spinner(f"Procesando PDF: {archivo.name}..."):
                    imgs = pdf_a_imagenes(archivo)
                    imagenes_procesadas.extend(imgs)
            else:
                imagenes_procesadas.append(Image.open(archivo))

        cols = st.columns(min(len(imagenes_procesadas), 4))
        for i, img in enumerate(imagenes_procesadas[:4]):
            with cols[i % 4]:
                st.image(img, use_container_width=True)
        if len(imagenes_procesadas) > 4:
            st.caption(f"... y {len(imagenes_procesadas)-4} página(s) más")

    modelo_guardado = st.session_state.get("modelo_guardado", "claude-sonnet-4-5")

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
    if st.button("✦  Transformar apuntes", type="primary"):
        if not imagenes_procesadas:
            st.warning("⚠️ Sube al menos una foto o PDF.")
        else:
            barra = st.progress(0, text="Analizando apuntes…")
            barra.progress(30, text="Transcribiendo…")
            resultado = transcribir(imagenes_procesadas, idioma, nivel, contexto, esquemas, modelo_guardado)
            barra.progress(80, text="Generando resumen…")

            if resultado:
                barra.progress(100, text="✓ Listo")
                titulo = contexto.strip() if contexto.strip() else f"Resumen {datetime.datetime.now().strftime('%d/%m %H:%M')}"
                guardar_en_historial(titulo, resultado)

                st.markdown('<div class="result-card"><span class="result-badge">✓ Resumen listo</span></div>', unsafe_allow_html=True)
                st.markdown(resultado)

                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.download_button("⬇ Descargar .txt", data=resultado, file_name=f"{titulo}.txt", mime="text/plain")
                with col_d2:
                    try:
                        from docx import Document
                        from docx.shared import Pt
                        doc = Document()
                        for linea in resultado.split('\n'):
                            doc.add_paragraph(linea)
                        buf = io.BytesIO()
                        doc.save(buf)
                        buf.seek(0)
                        st.download_button("⬇ Descargar .docx", data=buf.getvalue(), file_name=f"{titulo}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    except:
                        pass

# ── TAB 2: HISTORIAL ──────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="card-label"><span class="dot"></span>🕐 &nbsp;Historial de resúmenes</div>', unsafe_allow_html=True)
    historial = st.session_state.get("historial", [])
    if not historial:
        st.markdown('<p style="color:var(--text-muted);text-align:center;padding:2rem 0;">No hay resúmenes todavía. ¡Genera el primero!</p>', unsafe_allow_html=True)
    else:
        for i, item in enumerate(historial):
            with st.expander(f"📄 {item['titulo']} — {item['fecha']}"):
                st.markdown(item['resumen'])
                st.download_button(
                    "⬇ Descargar .txt",
                    data=item['resumen'],
                    file_name=f"{item['titulo']}.txt",
                    mime="text/plain",
                    key=f"dl_{i}"
                )

# ── TAB 3: AJUSTES ────────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="card-label"><span class="dot"></span>⚙️ &nbsp;Configuración</div>', unsafe_allow_html=True)

    st.markdown("**Modelo de Claude**")
    modelo = st.selectbox(
        "modelo",
        ["claude-haiku-4-5", "claude-sonnet-4-5", "claude-opus-4-5"],
        index=1,
        format_func=lambda x: {
            "claude-haiku-4-5": "⚡ Haiku — Más rápido",
            "claude-sonnet-4-5": "⚖️ Sonnet — Equilibrado (recomendado)",
            "claude-opus-4-5": "🎯 Opus — Máxima calidad"
        }[x],
        label_visibility="collapsed"
    )

    st.markdown("**Nombre de usuario** (aparece en el feedback)")
    nombre_usuario = st.text_input("nombre", placeholder="Tu nombre o alias…", label_visibility="collapsed", value=st.session_state.get("nombre_usuario", ""))

    if st.button("✦ Guardar ajustes"):
        st.session_state.modelo_guardado = modelo
        st.session_state.nombre_usuario = nombre_usuario
        st.success("✓ Ajustes guardados.")

# ── TAB 4: AYUDA ──────────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="card-label"><span class="dot"></span>❓ &nbsp;Cómo usar Shaad IA</div>', unsafe_allow_html=True)

    pasos = [
        ("1️⃣", "Sube tus fotos o PDF", "Arrastra las imágenes de tus apuntes o un PDF directamente."),
        ("2️⃣", "Elige idioma y nivel", "Selecciona el idioma del resumen y el nivel de detalle que necesitas."),
        ("3️⃣", "Añade contexto", "Opcional: escribe el tema para que el resumen sea más preciso."),
        ("4️⃣", "Genera el resumen", "Pulsa el botón y espera unos segundos."),
        ("5️⃣", "Descarga", "Descarga el resultado en .txt o .docx directamente."),
    ]
    for icono, titulo, desc in pasos:
        st.markdown(f'<div class="feedback-item"><strong style="color:var(--purple-bright)">{icono} {titulo}</strong><br><span style="color:var(--text-secondary);font-size:0.9rem">{desc}</span></div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="card-label"><span class="dot-green dot"></span>💬 &nbsp;Deja tu opinión</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:var(--text-secondary);font-size:0.88rem;margin-bottom:0.8rem;">Tu feedback ayuda a mejorar Shaad IA. ¡Cuéntanos qué te parece!</p>', unsafe_allow_html=True)

    nombre_fb = st.session_state.get("nombre_usuario", "")
    opinion = st.text_area("Tu opinión", placeholder="¿Qué mejorarías? ¿Qué te gusta? ¿Qué falla?", label_visibility="collapsed")
    puntuacion = st.select_slider("Puntuación", options=[1, 2, 3, 4, 5], value=5)

    if st.button("✦ Enviar feedback"):
        if opinion.strip():
            with st.spinner("Enviando…"):
                ok = enviar_feedback(nombre_fb or "Anónimo", opinion, puntuacion)
            if ok:
                st.success("✓ ¡Gracias por tu feedback!")
            else:
                st.error("❌ Error al enviar. Inténtalo de nuevo.")
        else:
            st.warning("⚠️ Escribe tu opinión antes de enviar.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer-custom">
    Hecho con <span>♥</span> para estudiantes como tú &nbsp;·&nbsp;
    <strong>Shaad IA</strong> © 2026
</div>
""", unsafe_allow_html=True)