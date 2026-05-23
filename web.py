import streamlit as st
import base64
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import APP_NAME, APP_SLOGAN, APP_PASSWORD, GROQ_API_KEY
from core.transcriber import transcribir_imagen
from core.summarizer import resumir, extraer_titulo
from core.exporter import guardar_docx

st.set_page_config(
    page_title=APP_NAME,
    page_icon="✨",
    layout="centered"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0a0a0f;
        color: #cdd6f4;
    }
    .main { background-color: #0a0a0f; }
    .stApp { background-color: #0a0a0f; }

    .titulo {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #c77dff, #7b2ff7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .slogan {
        text-align: center;
        color: #4a4a6a;
        font-size: 0.95rem;
        margin-bottom: 2rem;
        letter-spacing: 1px;
    }
    .card {
        background: #13131f;
        border: 1px solid #1e1e3a;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .stButton > button {
        background: linear-gradient(135deg, #7b2ff7, #a855f7) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0.7rem 2rem !important;
        width: 100% !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #9b4fff, #c77dff) !important;
        transform: translateY(-1px) !important;
    }
    .stFileUploader {
        background: #0a0a12 !important;
        border: 2px dashed #1e1e3a !important;
        border-radius: 12px !important;
    }
    .stTextInput > div > div > input {
        background: #13131f !important;
        color: #cdd6f4 !important;
        border: 1px solid #1e1e3a !important;
        border-radius: 10px !important;
    }
    .stSelectbox > div > div {
        background: #13131f !important;
        border: 1px solid #1e1e3a !important;
        border-radius: 10px !important;
    }
    .success-box {
        background: #0d1f0d;
        border: 1px solid #1a4a1a;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        color: #a8ff78;
        font-weight: 600;
    }
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #7b2ff7, #00d4a8) !important;
        border-radius: 4px !important;
    }
    div[data-testid="stFileUploader"] {
        background: #0a0a12;
        border: 2px dashed #2d2d5a;
        border-radius: 12px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def check_password():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.markdown('<div class="titulo">Shaad IA</div>', unsafe_allow_html=True)
        st.markdown('<div class="slogan">TRANSFORMA APUNTES EN CONOCIMIENTO</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🔒 Acceso privado")
        st.markdown("Esta es una versión beta privada. Introduce la contraseña para acceder.")
        password = st.text_input("Contraseña", type="password", placeholder="Introduce la contraseña...")

        if st.button("Entrar"):
            if password == APP_PASSWORD:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
        st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

def main():
    if not check_password():
        return

    st.markdown('<div class="titulo">Shaad IA</div>', unsafe_allow_html=True)
    st.markdown('<div class="slogan">TRANSFORMA APUNTES EN CONOCIMIENTO ✨</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📸 Sube tus fotos")
    fotos = st.file_uploader(
        "Arrastra o selecciona las fotos de tus apuntes",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if fotos:
        st.success(f"✓ {len(fotos)} foto(s) seleccionada(s)")
        cols = st.columns(min(len(fotos), 4))
        for i, foto in enumerate(fotos[:4]):
            cols[i].image(foto, use_container_width=True)
        if len(fotos) > 4:
            st.caption(f"... y {len(fotos)-4} más")

    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        idioma = st.selectbox("🌐 Idioma", ["castellano", "gallego", "inglés"])
    with col2:
        nivel = st.selectbox("📊 Nivel de detalle",
                             ["medio", "corto", "largo"],
                             format_func=lambda x: {
                                 "corto": "Corto (2-3 líneas)",
                                 "medio": "Medio (4-6 líneas)",
                                 "largo": "Largo (7-10 líneas)"
                             }[x])

    if fotos and st.button("⚡ Generar Resumen"):
        progreso = st.progress(0)
        estado = st.empty()

        try:
            transcripciones = []
            for i, foto in enumerate(fotos):
                estado.info(f"📷 Transcribiendo foto {i+1}/{len(fotos)}...")
                progreso.progress((i + 1) / (len(fotos) * 2))

                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                    tmp.write(foto.read())
                    tmp_path = tmp.name

                texto = transcribir_imagen(tmp_path)
                transcripciones.append(texto)
                os.unlink(tmp_path)

            estado.info("✍️ Generando resumen...")
            texto_unido = "\n\n".join(transcripciones)

            partes_procesadas = [0]
            total_partes = max(1, len(texto_unido) // 2500 + 1)

            def cb(parte, total):
                partes_procesadas[0] = parte
                progreso.progress(0.5 + (parte / total) * 0.45)
                estado.info(f"✍️ Resumiendo parte {parte}/{total}...")

            resumen = resumir(texto_unido, idioma=idioma, nivel=nivel, callback=cb)

            titulo = extraer_titulo(resumen)
            nombre_archivo = f"{titulo}.docx"

            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                tmp_docx = tmp.name

            guardar_docx(resumen, tmp_docx)

            with open(tmp_docx, "rb") as f:
                docx_bytes = f.read()
            os.unlink(tmp_docx)

            progreso.progress(1.0)
            estado.empty()

            st.markdown(f'<div class="success-box">🎉 ¡Resumen generado con éxito!<br>{nombre_archivo}</div>',
                        unsafe_allow_html=True)

            st.download_button(
                label="📥 Descargar documento",
                data=docx_bytes,
                file_name=nombre_archivo,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

            with st.expander("👁️ Ver resumen"):
                st.markdown(resumen)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

    st.markdown("---")
    st.markdown(
        '<p style="text-align:center; color:#2a2a4a; font-size:0.8rem;">Hecho con ❤️ para estudiantes como tú</p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()