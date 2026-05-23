import os
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class VistaDocumentos(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self._construir()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 15)
        layout.setSpacing(12)

        titulo = QLabel("Documentos")
        titulo.setStyleSheet("font-size: 20px; font-weight: 800; color: #c77dff; background: transparent;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        carpeta = self.app.carpeta_destino or os.path.expanduser("~/Downloads")

        lbl_carpeta = QLabel(f"📁 {carpeta}")
        lbl_carpeta.setStyleSheet("font-size: 10px; color: #4a4a6a; background: transparent;")
        lbl_carpeta.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_carpeta)

        btn_abrir = QPushButton("📂 Abrir carpeta de documentos")
        btn_abrir.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7b2ff7, stop:1 #a855f7);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 13px;
                font-weight: 700;
                padding: 12px 24px;
            }
            QPushButton:hover { background: #9b4fff; }
        """)
        btn_abrir.setCursor(Qt.PointingHandCursor)
        btn_abrir.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(carpeta)))
        layout.addWidget(btn_abrir, alignment=Qt.AlignCenter)

        try:
            archivos = sorted(
                [f for f in os.listdir(carpeta) if f.endswith('.docx')],
                reverse=True
            )[:10]

            if archivos:
                lbl = QLabel("Archivos recientes:")
                lbl.setStyleSheet("font-size: 12px; font-weight: 700; color: #cdd6f4; background: transparent;")
                layout.addWidget(lbl)

                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

                contenedor = QWidget()
                contenedor.setStyleSheet("background: transparent;")
                vbox = QVBoxLayout(contenedor)
                vbox.setSpacing(6)
                vbox.setContentsMargins(0, 0, 0, 0)

                for arch in archivos:
                    card = QFrame()
                    card.setStyleSheet("""
                        QFrame {
                            background: #13131f;
                            border: 1px solid #1e1e3a;
                            border-radius: 10px;
                        }
                        QFrame:hover { border: 1px solid #7b2ff7; }
                    """)
                    card_layout = QHBoxLayout(card)
                    card_layout.setContentsMargins(14, 10, 14, 10)

                    lbl_arch = QLabel(f"📄 {arch}")
                    lbl_arch.setStyleSheet("font-size: 11px; color: #cdd6f4; background: transparent;")
                    card_layout.addWidget(lbl_arch)
                    card_layout.addStretch()

                    ruta = os.path.join(carpeta, arch)
                    btn = QPushButton("Abrir")
                    btn.setStyleSheet("""
                        QPushButton {
                            background: #1e1e3a;
                            color: #cdd6f4;
                            border: none;
                            border-radius: 6px;
                            font-size: 10px;
                            padding: 4px 12px;
                        }
                        QPushButton:hover { background: #7b2ff7; color: white; }
                    """)
                    btn.setCursor(Qt.PointingHandCursor)
                    btn.clicked.connect(lambda checked, r=ruta: QDesktopServices.openUrl(QUrl.fromLocalFile(r)))
                    card_layout.addWidget(btn)
                    vbox.addWidget(card)

                vbox.addStretch()
                scroll.setWidget(contenedor)
                layout.addWidget(scroll)
            else:
                vacio = QLabel("No hay documentos en esta carpeta todavía.")
                vacio.setAlignment(Qt.AlignCenter)
                vacio.setStyleSheet("font-size: 12px; color: #4a4a6a; background: transparent;")
                layout.addWidget(vacio)
        except:
            pass

        layout.addStretch()