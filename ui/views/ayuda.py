from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class VistaAyuda(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self._construir()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 15)
        layout.setSpacing(10)

        titulo = QLabel("Ayuda")
        titulo.setStyleSheet("font-size: 20px; font-weight: 800; color: #c77dff; background: transparent;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        contenedor = QWidget()
        contenedor.setStyleSheet("background: transparent;")
        vbox = QVBoxLayout(contenedor)
        vbox.setSpacing(8)
        vbox.setContentsMargins(0, 0, 0, 0)

        pasos = [
            ("1️⃣", "Seleccionar fotos",
             "Haz clic en 'Seleccionar Fotos' y elige las imágenes de tus apuntes. Puedes seleccionar varias a la vez manteniendo Ctrl."),
            ("2️⃣", "Generar resumen",
             "Pulsa 'Generar Resumen' y espera. La app transcribirá y resumirá automáticamente con IA."),
            ("3️⃣", "Abrir documento",
             "Cuando termine pulsa 'Abrir carpeta' para ver el documento .docx generado. Ábrelo con LibreOffice Writer."),
            ("💡", "Consejos para mejores resultados",
             "Fotos bien iluminadas y enfocadas dan mejores resultados. Selecciona fotos del mismo tema para cada resumen. Evita fotos borrosas o con sombras."),
            ("⚙️", "Ajustes",
             "En Ajustes puedes cambiar el idioma del resumen, el nivel de detalle (corto, medio, largo) y la carpeta donde se guardan los documentos."),
            ("🕐", "Historial",
             "En Historial puedes ver todos los resúmenes generados anteriormente y abrirlos directamente con un clic."),
            ("📁", "Documentos",
             "En Documentos puedes ver y abrir todos los archivos .docx generados en tu carpeta de destino."),
            ("❓", "¿Problemas?",
             "Si la app da error, comprueba tu conexión a internet. Si el resumen sale en otro idioma, cámbialo en Ajustes. Si una foto no se transcribe bien, intenta con mejor iluminación."),
        ]

        for icono, titulo_paso, texto in pasos:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background: #13131f;
                    border: 1px solid #1e1e3a;
                    border-radius: 12px;
                }
                QFrame:hover { border: 1px solid #7b2ff7; }
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(16, 12, 16, 12)
            card_layout.setSpacing(4)

            lbl_titulo = QLabel(f"{icono} {titulo_paso}")
            lbl_titulo.setStyleSheet("font-size: 12px; font-weight: 700; color: #c77dff; background: transparent;")
            card_layout.addWidget(lbl_titulo)

            lbl_texto = QLabel(texto)
            lbl_texto.setStyleSheet("font-size: 11px; color: #8a8aaa; background: transparent;")
            lbl_texto.setWordWrap(True)
            card_layout.addWidget(lbl_texto)

            vbox.addWidget(card)

        vbox.addStretch()
        scroll.setWidget(contenedor)
        layout.addWidget(scroll)