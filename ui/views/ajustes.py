from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

CARD_STYLE = """
    QFrame {
        background: #13131f;
        border: 1px solid #1e1e3a;
        border-radius: 12px;
    }
"""
RADIO_STYLE = """
    QRadioButton {
        font-size: 11px;
        color: #cdd6f4;
        background: transparent;
        spacing: 8px;
    }
    QRadioButton::indicator {
        width: 16px;
        height: 16px;
        border-radius: 8px;
        border: 2px solid #2d2d5a;
        background: #0a0a0f;
    }
    QRadioButton::indicator:checked {
        background: #7b2ff7;
        border: 2px solid #7b2ff7;
    }
"""

class VistaAjustes(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self._construir()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 15)
        layout.setSpacing(12)

        titulo = QLabel("Ajustes")
        titulo.setStyleSheet("font-size: 20px; font-weight: 800; color: #c77dff; background: transparent;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        # Carpeta destino
        card1 = QFrame()
        card1.setStyleSheet(CARD_STYLE)
        c1 = QVBoxLayout(card1)
        c1.setContentsMargins(16, 14, 16, 14)
        c1.setSpacing(6)

        QLabel("📁 Carpeta de destino", parent=card1).setStyleSheet(
            "font-size: 12px; font-weight: 700; color: #cdd6f4; background: transparent;")
        c1.addWidget(card1.children()[1])

        self.lbl_carpeta = QLabel(self.app.carpeta_destino or "Misma carpeta que las fotos")
        self.lbl_carpeta.setStyleSheet("font-size: 10px; color: #4a4a6a; background: transparent;")
        c1.addWidget(self.lbl_carpeta)

        btn_carpeta = QPushButton("Cambiar carpeta")
        btn_carpeta.setStyleSheet("""
            QPushButton {
                background: #1e1e3a;
                color: #cdd6f4;
                border: none;
                border-radius: 8px;
                font-size: 11px;
                padding: 6px 14px;
            }
            QPushButton:hover { background: #7b2ff7; color: white; }
        """)
        btn_carpeta.setCursor(Qt.PointingHandCursor)
        btn_carpeta.clicked.connect(self._cambiar_carpeta)
        c1.addWidget(btn_carpeta, alignment=Qt.AlignRight)
        layout.addWidget(card1)

        # Idioma
        card2 = QFrame()
        card2.setStyleSheet(CARD_STYLE)
        c2 = QVBoxLayout(card2)
        c2.setContentsMargins(16, 14, 16, 14)
        c2.setSpacing(6)
        lbl2 = QLabel("🌐 Idioma del resumen")
        lbl2.setStyleSheet("font-size: 12px; font-weight: 700; color: #cdd6f4; background: transparent;")
        c2.addWidget(lbl2)

        self.idioma_group = QButtonGroup()
        for op in ["castellano", "gallego", "inglés"]:
            rb = QRadioButton(op.capitalize())
            rb.setStyleSheet(RADIO_STYLE)
            rb.setChecked(op == self.app.idioma)
            rb.toggled.connect(lambda checked, v=op: setattr(self.app, 'idioma', v) if checked else None)
            self.idioma_group.addButton(rb)
            c2.addWidget(rb)
        layout.addWidget(card2)

        # Nivel de detalle
        card3 = QFrame()
        card3.setStyleSheet(CARD_STYLE)
        c3 = QVBoxLayout(card3)
        c3.setContentsMargins(16, 14, 16, 14)
        c3.setSpacing(6)
        lbl3 = QLabel("📊 Nivel de detalle")
        lbl3.setStyleSheet("font-size: 12px; font-weight: 700; color: #cdd6f4; background: transparent;")
        c3.addWidget(lbl3)

        self.nivel_group = QButtonGroup()
        niveles = [
            ("corto", "Muy resumido — 2-3 líneas por apartado"),
            ("medio", "Equilibrado — 4-6 líneas por apartado"),
            ("largo", "Detallado — 7-10 líneas por apartado"),
        ]
        for val, desc in niveles:
            rb = QRadioButton(desc)
            rb.setStyleSheet(RADIO_STYLE)
            rb.setChecked(val == self.app.nivel)
            rb.toggled.connect(lambda checked, v=val: setattr(self.app, 'nivel', v) if checked else None)
            self.nivel_group.addButton(rb)
            c3.addWidget(rb)
        layout.addWidget(card3)

        # Guardar
        btn_guardar = QPushButton("✓ Guardar ajustes")
        btn_guardar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00b894, stop:1 #00d4a8);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 13px;
                font-weight: 700;
                padding: 12px 24px;
            }
            QPushButton:hover { background: #00d4a8; }
        """)
        btn_guardar.setCursor(Qt.PointingHandCursor)
        btn_guardar.clicked.connect(self._guardar)
        layout.addWidget(btn_guardar, alignment=Qt.AlignCenter)
        layout.addStretch()

    def _cambiar_carpeta(self):
        nueva = QFileDialog.getExistingDirectory(self, "Selecciona carpeta de destino")
        if nueva:
            self.app.carpeta_destino = nueva
            self.lbl_carpeta.setText(nueva)

    def _guardar(self):
        QMessageBox.information(self, "Ajustes", "✓ Ajustes guardados correctamente")