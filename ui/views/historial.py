import os
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class VistaHistorial(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self._construir()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 15)
        layout.setSpacing(12)

        titulo = QLabel("Historial de Resúmenes")
        titulo.setStyleSheet("font-size: 20px; font-weight: 800; color: #c77dff; background: transparent;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        if not self.app.historial:
            vacio = QLabel("No hay resúmenes generados todavía.\nGenera tu primer resumen en la pestaña Transcriptor.")
            vacio.setAlignment(Qt.AlignCenter)
            vacio.setStyleSheet("font-size: 13px; color: #4a4a6a; background: transparent;")
            vacio.setWordWrap(True)
            layout.addWidget(vacio)
            layout.addStretch()
            return

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        contenedor = QWidget()
        contenedor.setStyleSheet("background: transparent;")
        vbox = QVBoxLayout(contenedor)
        vbox.setSpacing(8)
        vbox.setContentsMargins(0, 0, 0, 0)

        for item in reversed(self.app.historial):
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background: #13131f;
                    border: 1px solid #1e1e3a;
                    border-radius: 12px;
                    padding: 4px;
                }
                QFrame:hover { border: 1px solid #7b2ff7; }
            """)
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(16, 12, 16, 12)

            info = QVBoxLayout()
            titulo_doc = QLabel(item.get('titulo', 'Sin título'))
            titulo_doc.setStyleSheet("font-size: 13px; font-weight: 700; color: #cdd6f4; background: transparent;")
            info.addWidget(titulo_doc)

            meta = QLabel(f"📅 {item.get('fecha', '')}  |  📸 {item.get('fotos', 0)} fotos")
            meta.setStyleSheet("font-size: 10px; color: #4a4a6a; background: transparent;")
            info.addWidget(meta)
            card_layout.addLayout(info)
            card_layout.addStretch()

            ruta = item.get('ruta', '')
            if ruta and os.path.exists(ruta):
                btn = QPushButton("Abrir")
                btn.setStyleSheet("""
                    QPushButton {
                        background: #7b2ff7;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-size: 11px;
                        font-weight: 600;
                        padding: 6px 16px;
                    }
                    QPushButton:hover { background: #9b4fff; }
                """)
                btn.setCursor(Qt.PointingHandCursor)
                btn.clicked.connect(lambda checked, r=ruta: QDesktopServices.openUrl(QUrl.fromLocalFile(r)))
                card_layout.addWidget(btn)

            vbox.addWidget(card)

        vbox.addStretch()
        scroll.setWidget(contenedor)
        layout.addWidget(scroll)