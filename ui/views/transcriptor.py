import os
import math
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class SpinnerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 40)
        self.angulo = 0
        self.activo = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)

    def iniciar(self):
        self.activo = True
        self.timer.start(30)
        self.show()

    def detener(self):
        self.activo = False
        self.timer.stop()
        self.hide()
        self.update()

    def _tick(self):
        self.angulo = (self.angulo + 10) % 360
        self.update()

    def paintEvent(self, event):
        if not self.activo:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        cx, cy, r = 20, 20, 15
        for i in range(12):
            angulo = self.angulo + i * 30
            rad = math.radians(angulo)
            x1 = cx + (r - 6) * math.cos(rad)
            y1 = cy + (r - 6) * math.sin(rad)
            x2 = cx + r * math.cos(rad)
            y2 = cy + r * math.sin(rad)
            alpha = int(40 + 215 * (i / 12))
            color = QColor(199, 125, 255, alpha)
            pen = QPen(color, 2.5, Qt.SolidLine, Qt.RoundCap)
            painter.setPen(pen)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

class Miniatura(QLabel):
    def __init__(self, ruta, parent=None):
        super().__init__(parent)
        self.setFixedSize(64, 64)
        self.setStyleSheet("""
            border-radius: 8px;
            border: 1px solid #1e1e3a;
            background: #13131f;
        """)
        pixmap = QPixmap(ruta)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self.setPixmap(pixmap)
            self.setScaledContents(False)
            self.setAlignment(Qt.AlignCenter)
        self.setToolTip(os.path.basename(ruta))

class VistaTranscriptor(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setAcceptDrops(True)
        self._construir()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 16)
        layout.setSpacing(12)

        # Titulo
        titulo = QLabel("Shaad IA")
        titulo.setStyleSheet("font-size: 32px; font-weight: 900; color: #c77dff; background: transparent; letter-spacing: -1px;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        slogan = QLabel("Transforma apuntes en conocimiento ✨")
        slogan.setStyleSheet("font-size: 11px; color: #3a3a5a; background: transparent; letter-spacing: 1px;")
        slogan.setAlignment(Qt.AlignCenter)
        layout.addWidget(slogan)

        # Zona drag & drop
        self.zona_drop = QFrame()
        self.zona_drop.setFixedHeight(110)
        self.zona_drop.setStyleSheet("""
            QFrame {
                background: #0a0a12;
                border: 2px dashed #1e1e3a;
                border-radius: 16px;
            }
        """)
        drop_layout = QVBoxLayout(self.zona_drop)
        drop_layout.setAlignment(Qt.AlignCenter)
        drop_layout.setSpacing(4)

        icono_drop = QLabel("📂")
        icono_drop.setStyleSheet("font-size: 28px; background: transparent;")
        icono_drop.setAlignment(Qt.AlignCenter)
        drop_layout.addWidget(icono_drop)

        self.lbl_drop = QLabel("Arrastra tus fotos aquí\no selecciona archivos")
        self.lbl_drop.setStyleSheet("font-size: 11px; color: #3a3a5a; background: transparent;")
        self.lbl_drop.setAlignment(Qt.AlignCenter)
        drop_layout.addWidget(self.lbl_drop)

        layout.addWidget(self.zona_drop)

        # Botones
        f_btn = QHBoxLayout()
        f_btn.setSpacing(12)

        self.btn_fotos = QPushButton("📁  Seleccionar fotos")
        self.btn_fotos.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7b2ff7, stop:1 #a855f7);
                color: white; border: none; border-radius: 12px;
                font-size: 13px; font-weight: 700; padding: 11px 22px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #9b4fff, stop:1 #c77dff);
            }
        """)
        self.btn_fotos.setCursor(Qt.PointingHandCursor)
        self.btn_fotos.clicked.connect(self._seleccionar_fotos)
        f_btn.addWidget(self.btn_fotos)

        self.btn_generar = QPushButton("✦  Generar resumen")
        self.btn_generar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00b894, stop:1 #00d4a8);
                color: white; border: none; border-radius: 12px;
                font-size: 13px; font-weight: 700; padding: 11px 22px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00d4a8, stop:1 #00f0c0);
            }
            QPushButton:disabled { background: #13131f; color: #2a2a4a; }
        """)
        self.btn_generar.setCursor(Qt.PointingHandCursor)
        self.btn_generar.setEnabled(False)
        self.btn_generar.clicked.connect(self._generar)
        f_btn.addWidget(self.btn_generar)

        layout.addLayout(f_btn)

        # Miniaturas
        self.scroll_miniaturas = QScrollArea()
        self.scroll_miniaturas.setFixedHeight(80)
        self.scroll_miniaturas.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_miniaturas.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_miniaturas.setWidgetResizable(True)
        self.scroll_miniaturas.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.scroll_miniaturas.hide()

        self.frame_miniaturas = QWidget()
        self.frame_miniaturas.setStyleSheet("background: transparent;")
        self.layout_miniaturas = QHBoxLayout(self.frame_miniaturas)
        self.layout_miniaturas.setSpacing(8)
        self.layout_miniaturas.setContentsMargins(0, 0, 0, 0)
        self.layout_miniaturas.addStretch()
        self.scroll_miniaturas.setWidget(self.frame_miniaturas)
        layout.addWidget(self.scroll_miniaturas)

        # Barra progreso
        self.barra = QProgressBar()
        self.barra.setFixedHeight(5)
        self.barra.setTextVisible(False)
        self.barra.setValue(0)
        self.barra.setStyleSheet("""
            QProgressBar { background: #13131f; border-radius: 2px; border: none; }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7b2ff7, stop:1 #00d4a8);
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.barra)

        # Estado + spinner + cancelar
        f_estado = QHBoxLayout()
        f_estado.setSpacing(8)

        self.spinner = SpinnerWidget()
        self.spinner.hide()
        f_estado.addWidget(self.spinner)

        self.lbl_estado = QLabel("")
        self.lbl_estado.setStyleSheet("font-size: 12px; font-weight: 700; color: #f9e2af; background: transparent;")
        f_estado.addWidget(self.lbl_estado)
        f_estado.addStretch()

        self.btn_cancelar = QPushButton("✕ Cancelar")
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background: #2a1a1a; color: #f38ba8;
                border: 1px solid #3a1a1a; border-radius: 8px;
                font-size: 10px; padding: 5px 12px;
            }
            QPushButton:hover { background: #f38ba8; color: white; }
        """)
        self.btn_cancelar.setCursor(Qt.PointingHandCursor)
        self.btn_cancelar.clicked.connect(self._cancelar)
        f_estado.addWidget(self.btn_cancelar)
        layout.addLayout(f_estado)

        # Log
        log_header = QHBoxLayout()
        lbl_log = QLabel("PROCESO EN CURSO")
        lbl_log.setStyleSheet("font-size: 9px; font-weight: 700; color: #7b2ff7; background: transparent; letter-spacing: 1px;")
        log_header.addWidget(lbl_log)
        log_header.addStretch()
        layout.addLayout(log_header)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background: #080810;
                border: 1px solid #1a1a2e;
                border-radius: 12px;
                color: #a8ff78;
                font-family: 'Consolas', monospace;
                font-size: 10px;
                padding: 10px;
            }
        """)
        self.log_text.setFixedHeight(130)
        layout.addWidget(self.log_text)

        # Resultado
        self.lbl_archivo = QLabel("")
        self.lbl_archivo.setStyleSheet("font-size: 10px; color: #4a4a6a; background: transparent;")
        self.lbl_archivo.setAlignment(Qt.AlignCenter)
        self.lbl_archivo.setWordWrap(True)
        layout.addWidget(self.lbl_archivo)

        f_bottom = QHBoxLayout()
        f_bottom.setSpacing(10)
        f_bottom.addStretch()

        self.btn_abrir = QPushButton("📁  Abrir carpeta")
        self.btn_abrir.setStyleSheet("""
            QPushButton {
                background: #13131f;
                color: #cdd6f4;
                border: 1px solid #1e1e3a;
                border-radius: 10px;
                font-size: 11px;
                font-weight: 600;
                padding: 8px 18px;
            }
            QPushButton:hover { background: #1e1e3a; border-color: #7b2ff7; }
            QPushButton:disabled { color: #2a2a4a; border-color: #13131f; }
        """)
        self.btn_abrir.setCursor(Qt.PointingHandCursor)
        self.btn_abrir.setEnabled(False)
        self.btn_abrir.clicked.connect(self._abrir_carpeta)
        f_bottom.addWidget(self.btn_abrir)
        f_bottom.addStretch()
        layout.addLayout(f_bottom)

        pie = QLabel("Hecho con ❤️ para estudiantes como tú")
        pie.setAlignment(Qt.AlignCenter)
        pie.setStyleSheet("font-size: 9px; color: #1e1e2e; background: transparent;")
        layout.addWidget(pie)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.zona_drop.setStyleSheet("""
                QFrame {
                    background: #0f0f1a;
                    border: 2px dashed #7b2ff7;
                    border-radius: 16px;
                }
            """)

    def dragLeaveEvent(self, event):
        self.zona_drop.setStyleSheet("""
            QFrame {
                background: #0a0a12;
                border: 2px dashed #1e1e3a;
                border-radius: 16px;
            }
        """)

    def dropEvent(self, event):
        self.zona_drop.setStyleSheet("""
            QFrame {
                background: #0a0a12;
                border: 2px dashed #1e1e3a;
                border-radius: 16px;
            }
        """)
        archivos = [u.toLocalFile() for u in event.mimeData().urls()
                    if u.toLocalFile().lower().endswith(('.jpg', '.jpeg', '.png'))]
        if archivos:
            self.app.fotos = sorted(archivos)
            self._actualizar_miniaturas()
            self.btn_generar.setEnabled(True)
            self.log(f"📸 {len(archivos)} foto(s) añadidas por drag & drop.")

    def _seleccionar_fotos(self):
        fotos, _ = QFileDialog.getOpenFileNames(
            self, "Selecciona las fotos", "",
            "Imágenes (*.jpg *.jpeg *.png)"
        )
        if fotos:
            self.app.fotos = sorted(fotos)
            self._actualizar_miniaturas()
            self.btn_generar.setEnabled(True)
            self.log(f"📸 {len(fotos)} foto(s) seleccionada(s).")

    def _actualizar_miniaturas(self):
        for i in reversed(range(self.layout_miniaturas.count())):
            w = self.layout_miniaturas.itemAt(i).widget()
            if w:
                w.deleteLater()

        for ruta in self.app.fotos:
            mini = Miniatura(ruta)
            self.layout_miniaturas.addWidget(mini)

        self.layout_miniaturas.addStretch()
        n = len(self.app.fotos)
        self.lbl_drop.setText(f"✓ {n} foto{'s' if n>1 else ''} seleccionada{'s' if n>1 else ''}")
        self.scroll_miniaturas.show()

    def _generar(self):
        self.btn_generar.setEnabled(False)
        self.btn_fotos.setEnabled(False)
        self.lbl_estado.setText("Procesando...")
        self.spinner.iniciar()
        self.barra.setValue(0)
        self.app.procesar()

    def _cancelar(self):
        self.app.cancelar_flag = True
        self.log("⚠️ Cancelando...")

    def _abrir_carpeta(self):
        if self.app.fotos:
            carpeta = self.app.carpeta_destino or os.path.dirname(self.app.fotos[0])
            QDesktopServices.openUrl(QUrl.fromLocalFile(carpeta))

    @Slot(str)
    def log(self, msg):
        self.log_text.append(msg)

    @Slot(float)
    def actualizar_barra(self, valor):
        self.barra.setValue(int(valor * 100))

    @Slot(str, str)
    def on_done(self, nombre_archivo, carpeta):
        self.spinner.detener()
        self.lbl_estado.setText("¡Resumen generado con éxito! 🎉")
        self.lbl_estado.setStyleSheet("font-size: 12px; font-weight: 700; color: #a8ff78; background: transparent;")
        self.lbl_archivo.setText(f"📄 {nombre_archivo}  |  📁 {carpeta}")
        self.btn_abrir.setEnabled(True)
        self.btn_generar.setEnabled(True)
        self.btn_fotos.setEnabled(True)
        self.log(f"\n✅ Guardado: {nombre_archivo}")

    @Slot(str)
    def on_error(self, error):
        self.spinner.detener()
        self.lbl_estado.setText("❌ Error al procesar")
        self.lbl_estado.setStyleSheet("font-size: 12px; font-weight: 700; color: #f38ba8; background: transparent;")
        self.btn_generar.setEnabled(True)
        self.btn_fotos.setEnabled(True)
        self.log(f"\n❌ Error: {error}")