import streamlit as st
import anthropic
import base64
import os
from PIL import Image
import io

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

.block-container { max-width: 720px !important; padding: 3rem 1.5rem 4rem !important; }

.hero-wrap { text-align: center; padding: 2rem 0 1.5rem; }
.hero-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: var(--purple-soft); border: 1px solid var(--border-strong);
    border-radius: 999px; padding: 4px 14px; font-size: 0.70rem;
    letter-spacing: 0.12em; text-transform: uppercase; color: var(--purple-bright);
    font-family: var(--font-display); font-weight: 600; margin-bottom: 1rem;
}
.hero-logo { width: 64px; height: 64px; margin: 0 auto 0.8rem; display: block; }
.hero-title {
    font-family: var(--font-display) !important;
    font-size: clamp(2.4rem, 6vw, 3.8rem) !important;
    font-weight: 800 !important; line-height: 1.05 !important;
    background: linear-gradient(135deg, #c084fc 0%, #a855f7 35%, #4ade80 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin: 0 0 0.5rem !important; letter-spacing: -0.02em;
}
.hero-sub {
    font-family: var(--font-display); font-size: 0.78rem;
    letter-spacing: 0.20em; text-transform: uppercase; color: var(--text-muted);
}

.card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius-card); padding: 1.6rem 1.8rem;
    box-shadow: var(--shadow-card); transition: border-color 0.25s, box-shadow 0.25s;
    margin-bottom: 1.2rem;
}
.card:hover { border-color: var(--border-strong); box-shadow: var(--shadow-card), var(--shadow-glow-p); }
.card-label {
    display: flex; align-items: center; gap: 8px;
    font-family: var(--font-display); font-weight: 700; font-size: 0.80rem;
    letter-spacing: 0.10em; text-transform: uppercase; color: var(--text-secondary);
    margin-bottom: 1rem;
}
.card-label .dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--purple-bright); box-shadow: 0 0 8px var(--purple-bright); flex-shrink: 0;
}
.card-label.green .dot { background: var(--green-bright); box-shadow: 0 0 8px var(--green-bright); }

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: var(--bg-surface) !important; border: 1px solid var(--border) !important;
    border-radius: 10px !important; color: var(--text-primary) !important;
    font-family: var(--font-body) !important; font-size: 0.95rem !important;
    padding: 0.75rem 1rem !important; box-shadow: none !important;
}
[data-testid="stTextInput"] input:focus { border-color: var(--purple-bright) !important; box-shadow: 0 0 0 3px rgba(168,85,247,0.15) !important; }
[data-testid="stTextInput"] label, [data-testid="stTextArea"] label { color: var(--text-secondary) !important; font-family: var(--font-body) !important; font-size: 0.88rem !important; }

[data-testid="stFileUploader"] {
    border: 2px dashed var(--border) !important; border-radius: var(--radius-card) !important;
    background: var(--bg-surface) !important; padding: 1.2rem !important;
}
[data-testid="stFileUploader"]:hover { border-color: var(--purple-bright) !important; background: var(--purple-soft) !important; }
[data-testid="stFileUploader"] label, [data-testid="stFileUploader"] p { color: var(--text-secondary) !important; }

[data-testid="stSelectbox"] > div > div {
    background: var(--bg-surface) !important; border: 1px solid var(--border) !important;
    border-radius: 10px !important; color: var(--text-primary) !important;
}
[data-testid="stSelectbox"] label { color: var(--text-secondary) !important; font-size: 0.88rem !important; }
[data-baseweb="select"] * { color: var(--text-primary) !important; }
[data-baseweb="popover"] { background: var(--bg-card) !important; border: 1px solid var(--border-strong) !important; border-radius: 12px !important; }
[role="option"]:hover { background: var(--purple-soft) !important; }

[data-testid="stButton"] > button {
    background: linear-gradient(135deg, var(--purple-mid), var(--purple-bright)) !important;
    color: #fff !important; border: none !important; border-radius: var(--radius-btn) !important;
    font-family: var(--font-display) !important; font-weight: 700 !important;
    font-size: 0.90rem !important; letter-spacing: 0.05em !important;
    padding: 0.70rem 2rem !important; width: 100% !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.40) !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
}
[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(124,58,237,0.55) !important;
}

[data-testid="stAlert"] {
    background: var(--bg-card) !important; border-radius: 12px !important;
    border: 1px solid var(--border) !important; font-family: var(--font-body) !important;
}

[data-testid="stExpander"] {
    background: var(--bg-card) !important; border: 1px solid var(--border) !important;
    border-radius: var(--radius-card) !important;
}
[data-testid="stExpander"] summary { font-family: var(--font-display) !important; font-weight: 600 !important; color: var(--text-secondary) !important; }

[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li { color: var(--text-primary) !important; font-family: var(--font-body) !important; line-height: 1.7 !important; }
[data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3 { font-family: var(--font-display) !important; color: var(--text-primary) !important; }

[data-testid="stImage"] img { border-radius: 12px !important; border: 1px solid var(--border) !important; }

hr { border-color: var(--border) !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 3px; }

.result-card {
    background: linear-gradient(135deg, rgba(74,222,128,0.05) 0%, var(--bg-card) 50%);
    border: 1px solid rgba(74,222,128,0.25); border-radius: var(--radius-card);
    padding: 1.8rem 2rem; box-shadow: var(--shadow-card), var(--shadow-glow-g); margin-top: 1.5rem;
}
.result-badge {
    background: var(--green-soft); border: 1px solid rgba(74,222,128,0.30);
    color: var(--green-bright); border-radius: 999px; padding: 3px 12px;
    font-size: 0.70rem; letter-spacing: 0.10em; text-transform: uppercase;
    font-family: var(--font-display); font-weight: 600;
}

.footer-custom {
    text-align: center; padding: 2rem 0 0; color: var(--text-muted);
    font-size: 0.78rem; font-family: var(--font-body); letter-spacing: 0.03em;
}
.footer-custom span { color: #f43f5e; }
.footer-custom strong { color: var(--purple-bright); }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def encode_image_to_base64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def get_api_key():
    try:
        return st.secrets.get("ANTHROPIC_API_KEY", "")
    except:
        return os.environ.get("ANTHROPIC_API_KEY", "")

def get_app_password():
    try:
        return st.secrets.get("APP_PASSWORD", "shaad2026")
    except:
        return os.environ.get("APP_PASSWORD", "shaad2026")

def get_detail_lines(nivel: str) -> str:
    mapa = {
        "Breve (2-3 líneas)": "2-3",
        "Medio (4-6 líneas)": "4-6",
        "Detallado (7-10 líneas)": "7-10",
    }
    return mapa.get(nivel, "4-6")

def transcribir_apuntes(imagenes, idioma, nivel, contexto, esquemas):
    api_key = get_api_key()
    if not api_key:
        st.error("❌ No se encontró la API key de Anthropic.")
        return ""

    client = anthropic.Anthropic(api_key=api_key)
    lineas = get_detail_lines(nivel)
    ctx_str = f"\nContexto adicional: {contexto}" if contexto.strip() else ""

    esquemas_instruccion = ""
    if not esquemas:
        esquemas_instruccion = "\nNO uses tablas, esquemas visuales ni diagramas. Solo texto estructurado con títulos y listas cuando sea necesario."

    system_prompt = f"""Eres un experto en crear apuntes de estudio para estudiantes de Bachillerato.
Responde SIEMPRE en {idioma}.
Haz un resumen completo y compacto del contenido. Cada apartado en {lineas} líneas.
Mantén toda la información importante: definiciones, autores, fechas clave, clasificaciones.
Usa un lenguaje académico claro, directo y pensado para memorizar en examen.
NO inventes información que no esté en el texto.
NO pongas conclusiones ni introducciones inventadas.{esquemas_instruccion}{ctx_str}"""

    content = []
    for img in imagenes:
        b64 = encode_image_to_base64(img)
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}})
    content.append({"type": "text", "text": "Transcribe y resume el contenido de estos apuntes."})

    resp = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": content}]
    )
    return resp.content[0].text


# ── Login ─────────────────────────────────────────────────────────────────────
def check_password():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.markdown("""
        <div class="hero-wrap">
            <div class="hero-badge">✦ Versión beta privada</div>
            <h1 class="hero-title">Shaad IA</h1>
            <p class="hero-sub">Transforma apuntes en conocimiento</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-label"><span class="dot"></span>🔒 &nbsp;Acceso privado</div>', unsafe_allow_html=True)
        st.markdown('<p style="color:var(--text-secondary); font-size:0.9rem; margin-bottom:1rem;">Introduce la contraseña para acceder a la beta.</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

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
    st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="hero-logo">', unsafe_allow_html=True)

st.markdown("""
<div class="hero-wrap">
    <div class="hero-badge">✦ IA para estudiantes</div>
    <h1 class="hero-title">Shaad IA</h1>
    <p class="hero-sub">Transforma apuntes en conocimiento</p>
</div>
""", unsafe_allow_html=True)


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["✦ Transcriptor", "⚙️ Ajustes"])

with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-label"><span class="dot"></span>⚙️ &nbsp;Ajustes</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    idioma_ajuste = st.selectbox(
        "🌐 Idioma por defecto",
        ["castellano", "galego", "català", "euskara", "english", "français", "português", "deutsch", "italiano"],
        key="idioma_ajuste"
    )
    nivel_ajuste = st.selectbox(
        "📊 Nivel de detalle por defecto",
        ["Breve (2-3 líneas)", "Medio (4-6 líneas)", "Detallado (7-10 líneas)"],
        index=1,
        key="nivel_ajuste"
    )
    esquemas_ajuste = st.toggle(
        "📊 Incluir tablas y esquemas visuales en el resumen",
        value=False,
        key="esquemas_ajuste"
    )
    if st.button("✦ Guardar ajustes", key="guardar_ajustes"):
        st.session_state.idioma_guardado = idioma_ajuste
        st.session_state.nivel_guardado = nivel_ajuste
        st.session_state.esquemas_guardado = esquemas_ajuste
        st.success("✓ Ajustes guardados correctamente.")

with tab1:
    # Opciones rápidas
    col1, col2 = st.columns(2)
    with col1:
        idioma = st.selectbox(
            "🌐 Idioma",
            ["castellano", "galego", "català", "euskara", "english", "français", "português", "deutsch", "italiano"],
            index=0,
            key="idioma_main"
        )
    with col2:
        nivel = st.selectbox(
            "📊 Nivel de detalle",
            ["Breve (2-3 líneas)", "Medio (4-6 líneas)", "Detallado (7-10 líneas)"],
            index=1,
            key="nivel_main"
        )

    # Contexto
    st.markdown('<div class="card-label" style="margin-top:1rem"><span class="dot"></span>Contexto opcional</div>', unsafe_allow_html=True)
    contexto = st.text_input(
        label="contexto",
        placeholder="Ej: Historia, tema 4 — neocolonialismo…",
        label_visibility="collapsed"
    )

    # Subida
    st.markdown('<div class="card-label" style="margin-top:1rem"><span class="dot"></span>📷 &nbsp;Sube tus fotos</div>', unsafe_allow_html=True)
    archivos = st.file_uploader(
        label="uploader",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if archivos:
        cols = st.columns(min(len(archivos), 4))
        for i, archivo in enumerate(archivos):
            with cols[i % 4]:
                st.image(Image.open(archivo), use_container_width=True)

    # Botón
    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)
    if st.button("✦  Transformar apuntes", type="primary"):
        if not archivos:
            st.warning("⚠️ Sube al menos una foto para continuar.")
        else:
            imagenes = [Image.open(f) for f in archivos]
            esquemas = st.session_state.get("esquemas_guardado", False)
            with st.spinner("Analizando tus apuntes…"):
                resultado = transcribir_apuntes(imagenes, idioma, nivel, contexto, esquemas)

            if resultado:
                st.markdown('<div class="result-card"><span class="result-badge">✓ Resumen listo</span></div>', unsafe_allow_html=True)
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