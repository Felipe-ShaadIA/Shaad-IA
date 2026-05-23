import streamlit as st
import anthropic
import base64
import os
from PIL import Image
import io

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Shaad IA · Apuntes Inteligentes",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ─── Google Fonts ─── */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

/* ─── Root tokens ─── */
:root {
    --bg-base:        #0a0a0f;
    --bg-surface:     #0f0f1a;
    --bg-card:        #13131f;
    --bg-card-hover:  #17172a;
    --border:         rgba(138, 92, 246, 0.18);
    --border-strong:  rgba(138, 92, 246, 0.40);
    --purple-bright:  #a855f7;
    --purple-mid:     #7c3aed;
    --purple-soft:    rgba(168, 85, 247, 0.12);
    --green-bright:   #4ade80;
    --green-mid:      #22c55e;
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

/* ─── Base reset ─── */
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

[data-testid="stHeader"],
[data-testid="stToolbar"],
footer { display: none !important; }

/* ─── Block container ─── */
.block-container {
    max-width: 720px !important;
    padding: 3rem 1.5rem 4rem !important;
}

/* ─── Hero ─── */
.hero-wrap {
    text-align: center;
    padding: 2.5rem 0 2rem;
    position: relative;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--purple-soft);
    border: 1px solid var(--border-strong);
    border-radius: 999px;
    padding: 4px 14px;
    font-size: 0.70rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--purple-bright);
    font-family: var(--font-display);
    font-weight: 600;
    margin-bottom: 1.2rem;
}
.hero-title {
    font-family: var(--font-display) !important;
    font-size: clamp(2.4rem, 6vw, 3.8rem) !important;
    font-weight: 800 !important;
    line-height: 1.05 !important;
    background: linear-gradient(135deg, #c084fc 0%, #a855f7 35%, #4ade80 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.5rem !important;
    letter-spacing: -0.02em;
}
.hero-sub {
    font-family: var(--font-display);
    font-size: 0.78rem;
    letter-spacing: 0.20em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.3rem;
}

/* ─── Cards ─── */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-card);
    padding: 1.6rem 1.8rem;
    box-shadow: var(--shadow-card);
    transition: border-color 0.25s, box-shadow 0.25s;
    margin-bottom: 1.2rem;
}
.card:hover {
    border-color: var(--border-strong);
    box-shadow: var(--shadow-card), var(--shadow-glow-p);
}
.card-label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 0.80rem;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    color: var(--text-secondary);
    margin-bottom: 1rem;
}
.card-label .dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--purple-bright);
    box-shadow: 0 0 8px var(--purple-bright);
    flex-shrink: 0;
}
.card-label.green .dot { background: var(--green-bright); box-shadow: 0 0 8px var(--green-bright); }

/* ─── Streamlit widget overrides ─── */
/* Text input */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
    font-size: 0.95rem !important;
    padding: 0.75rem 1rem !important;
    box-shadow: none !important;
    transition: border-color 0.2s !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--purple-bright) !important;
    box-shadow: 0 0 0 3px rgba(168,85,247,0.15) !important;
    outline: none !important;
}
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label {
    color: var(--text-secondary) !important;
    font-family: var(--font-body) !important;
    font-size: 0.88rem !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    border: 2px dashed var(--border) !important;
    border-radius: var(--radius-card) !important;
    background: var(--bg-surface) !important;
    padding: 1.2rem !important;
    transition: border-color 0.2s, background 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--purple-bright) !important;
    background: var(--purple-soft) !important;
}
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] p,
[data-testid="stFileUploaderDropzoneInstructions"] small {
    color: var(--text-secondary) !important;
    font-family: var(--font-body) !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] svg { color: var(--purple-bright) !important; }

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
}
[data-testid="stSelectbox"] > div > div:focus-within {
    border-color: var(--purple-bright) !important;
    box-shadow: 0 0 0 3px rgba(168,85,247,0.15) !important;
}
[data-testid="stSelectbox"] label {
    color: var(--text-secondary) !important;
    font-family: var(--font-body) !important;
    font-size: 0.88rem !important;
}
[data-baseweb="select"] * { color: var(--text-primary) !important; }
[data-baseweb="popover"] { background: var(--bg-card) !important; border: 1px solid var(--border-strong) !important; border-radius: 12px !important; }
[role="option"] { background: transparent !important; }
[role="option"]:hover { background: var(--purple-soft) !important; }

/* Primary button */
[data-testid="stButton"] > button[kind="primary"],
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, var(--purple-mid), var(--purple-bright)) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--radius-btn) !important;
    font-family: var(--font-display) !important;
    font-weight: 700 !important;
    font-size: 0.90rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.70rem 2rem !important;
    width: 100% !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.40) !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
    cursor: pointer !important;
}
[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(124,58,237,0.55) !important;
}
[data-testid="stButton"] > button:active {
    transform: translateY(0) !important;
}

/* Spinner / status */
[data-testid="stSpinner"] p { color: var(--purple-bright) !important; font-family: var(--font-body) !important; }
[data-testid="stStatusWidget"] { background: var(--bg-card) !important; border: 1px solid var(--border) !important; border-radius: 12px !important; }

/* Success / info / warning messages */
[data-testid="stAlert"] {
    background: var(--bg-card) !important;
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
    font-family: var(--font-body) !important;
}

/* Expander */
[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-card) !important;
}
[data-testid="stExpander"] summary {
    font-family: var(--font-display) !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
}

/* Markdown / text */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span {
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
    line-height: 1.7 !important;
}
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {
    font-family: var(--font-display) !important;
    color: var(--text-primary) !important;
}

/* Image preview */
[data-testid="stImage"] img {
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
}

/* Divider */
hr { border-color: var(--border) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 3px; }

/* ─── Result card ─── */
.result-card {
    background: linear-gradient(135deg, rgba(74,222,128,0.05) 0%, var(--bg-card) 50%);
    border: 1px solid rgba(74,222,128,0.25);
    border-radius: var(--radius-card);
    padding: 1.8rem 2rem;
    box-shadow: var(--shadow-card), var(--shadow-glow-g);
    margin-top: 1.5rem;
}
.result-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 1.2rem;
}
.result-badge {
    background: var(--green-soft);
    border: 1px solid rgba(74,222,128,0.30);
    color: var(--green-bright);
    border-radius: 999px;
    padding: 3px 12px;
    font-size: 0.70rem;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    font-family: var(--font-display);
    font-weight: 600;
}

/* ─── Footer ─── */
.footer-custom {
    text-align: center;
    padding: 2rem 0 0;
    color: var(--text-muted);
    font-size: 0.78rem;
    font-family: var(--font-body);
    letter-spacing: 0.03em;
}
.footer-custom span { color: #f43f5e; }
.footer-custom strong { color: var(--purple-bright); }

/* ─── Columns gap fix ─── */
[data-testid="stHorizontalBlock"] { gap: 1rem !important; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def encode_image_to_base64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def get_detail_prompt(nivel: str) -> str:
    mapa = {
        "Breve (2-3 líneas)":    "Resume cada concepto clave en 2-3 líneas muy concisas.",
        "Medio (4-6 líneas)":    "Explica cada concepto con claridad en 4-6 líneas.",
        "Detallado (7-10 líneas)": "Desarrolla cada concepto de forma completa en 7-10 líneas con ejemplos si es posible.",
        "Máximo (10+ líneas)":   "Explica cada concepto exhaustivamente con todos los detalles, subpuntos y ejemplos.",
    }
    return mapa.get(nivel, "Explica cada concepto con claridad en 4-6 líneas.")


def transcribir_apuntes(imagenes: list, idioma: str, nivel: str, contexto: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY", st.secrets.get("ANTHROPIC_API_KEY", ""))
    if not api_key:
        st.error("❌ No se encontró la API key de Anthropic. Añádela en los Secrets de Streamlit.")
        return ""

    client = anthropic.Anthropic(api_key=api_key)
    detalle = get_detail_prompt(nivel)
    ctx_str = f"\nContexto adicional del usuario: {contexto}" if contexto.strip() else ""

    system_prompt = f"""Eres un asistente experto en educación y síntesis de apuntes académicos.
Tu tarea es transcribir y transformar apuntes manuscritos o fotografiados en conocimiento estructurado y claro.
Responde SIEMPRE en {idioma}.
{detalle}
Organiza el contenido con títulos, subtítulos y listas cuando sea útil.
Usa un lenguaje preciso pero accesible para estudiantes.{ctx_str}"""

    content = []
    for img in imagenes:
        b64 = encode_image_to_base64(img)
        content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}
        })
    content.append({
        "type": "text",
        "text": "Por favor, transcribe y estructura el conocimiento contenido en estos apuntes."
    })

    resp = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": content}]
    )
    return resp.content[0].text


# ── UI ────────────────────────────────────────────────────────────────────────

# Hero
st.markdown("""
<div class="hero-wrap">
    <div class="hero-badge">✦ IA para estudiantes</div>
    <h1 class="hero-title">Shaad IA</h1>
    <p class="hero-sub">Transforma apuntes en conocimiento</p>
</div>
""", unsafe_allow_html=True)

# ── Card: Contexto ────────────────────────────────────────────────────────────
st.markdown("""
<div class="card">
  <div class="card-label"><span class="dot"></span>Contexto (opcional)</div>
</div>
""", unsafe_allow_html=True)

contexto = st.text_input(
    label="contexto_hidden",
    placeholder="Ej: Biología celular, tema 4 — mitosis y meiosis…",
    label_visibility="collapsed",
)

# ── Card: Subida de imágenes ──────────────────────────────────────────────────
st.markdown("""
<div class="card" style="margin-top:1.2rem">
  <div class="card-label"><span class="dot"></span>📷 &nbsp;Sube tus fotos</div>
</div>
""", unsafe_allow_html=True)

archivos = st.file_uploader(
    label="uploader_hidden",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
    label_visibility="collapsed",
)

if archivos:
    cols = st.columns(min(len(archivos), 4))
    for i, archivo in enumerate(archivos):
        with cols[i % 4]:
            img = Image.open(archivo)
            st.image(img, use_container_width=True)

# ── Card: Opciones ────────────────────────────────────────────────────────────
st.markdown("""<div style="margin-top:1.2rem"></div>""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="card-label" style="margin-bottom:0.4rem">
        <span class="dot"></span>🌐 &nbsp;Idioma
    </div>""", unsafe_allow_html=True)
    idioma = st.selectbox(
        label="idioma_hidden",
        options=["castellano", "català", "galego", "euskara", "english", "français", "português", "deutsch", "italiano"],
        label_visibility="collapsed",
    )

with col2:
    st.markdown("""
    <div class="card-label" style="margin-bottom:0.4rem">
        <span class="dot" style="background:var(--green-bright);box-shadow:0 0 8px var(--green-bright)"></span>
        📋 &nbsp;Nivel de detalle
    </div>""", unsafe_allow_html=True)
    nivel = st.selectbox(
        label="nivel_hidden",
        options=["Breve (2-3 líneas)", "Medio (4-6 líneas)", "Detallado (7-10 líneas)", "Máximo (10+ líneas)"],
        index=1,
        label_visibility="collapsed",
    )

# ── CTA ───────────────────────────────────────────────────────────────────────
st.markdown("<div style='margin-top:1.8rem'></div>", unsafe_allow_html=True)

if st.button("✦  Transformar apuntes", type="primary"):
    if not archivos:
        st.warning("⚠️ Sube al menos una foto de tus apuntes para continuar.")
    else:
        imagenes = [Image.open(f) for f in archivos]
        with st.spinner("Analizando tus apuntes…"):
            resultado = transcribir_apuntes(imagenes, idioma, nivel, contexto)

        if resultado:
            st.markdown("""
            <div class="result-card">
                <div class="result-header">
                    <span class="result-badge">✓ Transcripción lista</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(resultado)

            st.download_button(
                label="⬇  Descargar como .txt",
                data=resultado,
                file_name="apuntes_shaad.txt",
                mime="text/plain",
            )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer-custom">
    Hecho con <span>♥</span> para estudiantes como tú &nbsp;·&nbsp;
    <strong>Shaad IA</strong> © 2026
</div>
""", unsafe_allow_html=True)
