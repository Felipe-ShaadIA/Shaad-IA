import sys
import os
import math
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from config.settings import APP_NAME, ASSETS_DIR
from core.transcriber import transcribir_imagen
from core.summarizer import resumir, extraer_titulo
from core.exporter import guardar_docx
from services.history import cargar_historial, guardar_historial, añadir_entrada
from services.logger import log_info, log_error

class WorkerSignals(QObject):
    log = Signal(str)
    progress = Signal(float)
    done = Signal(str, str)
    error = Signal(str)

class Worker(QRunnable):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.signals = WorkerSignals()

    def run(self):
        try:
            total = len(self.app.fotos)
            transcripciones = []
            log_info(f"Iniciando procesamiento de {total} fotos")

            for i, foto in enumerate(self.app.fotos):
                if self.app.cancelar_flag:
                    self.signals.log.emit("⚠️ Cancelado.")
                    return
                nombre = os.path.basename(foto)
                self.signals.log.emit(f"\n  → Foto {i+1}/{total}: {nombre}")
                self.signals.log.emit("    Transcribiendo...")
                try:
                    texto = transcribir_imagen(foto)
                    transcripciones.append(texto)
                    self.signals.log.emit("    ✓ Transcrita")
                    log_info(f"Foto transcrita: {nombre}")
                except Exception as e:
                    log_error(f"Error transcribiendo {nombre}: {str(e)}")
                    raise
                self.signals.progress.emit((i + 1) / (total * 2))

            if self.app.cancelar_flag:
                return

            self.signals.log.emit("\n✍️  Generando resumen...")

            def cb(parte, total_partes):
                self.signals.log.emit(f"    Resumiendo foto {parte}/{total_partes}...")
                self.signals.progress.emit(0.5 + (parte / total_partes) * 0.45)

            texto_unido = "\n\n".join(transcripciones)
            resumen = resumir(
                texto_unido,
                idioma=self.app.idioma,
                nivel=self.app.nivel,
                cancelar_flag=lambda: self.app.cancelar_flag,
                callback=cb
            )

            if self.app.cancelar_flag or not resumen:
                return

            titulo = extraer_titulo(resumen)
            carpeta = self.app.carpeta_destino or os.path.dirname(self.app.fotos[0])
            nombre_archivo = titulo + ".docx"
            ruta_docx = os.path.join(carpeta, nombre_archivo)
            guardar_docx(resumen, ruta_docx)

            self.app.historial = añadir_entrada(
                self.app.historial, titulo, ruta_docx, total)
            guardar_historial(self.app.historial)

            log_info(f"Resumen guardado: {nombre_archivo}")
            self.signals.progress.emit(1.0)
            self.signals.done.emit(nombre_archivo, carpeta)

        except Exception as e:
            log_error(f"Error en procesamiento: {str(e)}")
            self.signals.error.emit(str(e))

class ShaadApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.fotos = []
        self.cancelar_flag = False
        self.historial = cargar_historial()
        self.idioma = "castellano"
        self.nivel = "medio"
        self.carpeta_destino = ""
        self.thread_pool = QThreadPool()

        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(1000, 750)

        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        self.setStyleSheet(self._estilos())
        self._construir_ui()
        log_info("Shaad IA iniciada")

    def _estilos(self):
        return """
        QMainWindow, QWidget { background: #0d0d14; font-family: 'Segoe UI', Arial; }
        #sidebar {
            background: #0a0a12;
            border-right: 1px solid #1a1a2e;
        }
        #main_panel { background: #0d0d14; }
        #sidebar_btn {
            background: transparent;
            color: #4a4a6a;
            border: none;
            border-radius: 12px;
            font-size: 10px;
            padding: 12px 6px;
            text-align: center;
        }
        #sidebar_btn:hover {
            background: #13131f;
            color: #cdd6f4;
        }
        #sidebar_btn_active {
            background: #1a1a2e;
            color: #c77dff;
            border: none;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 700;
            padding: 12px 6px;
            text-align: center;
        }
        #pro_tips {
            background: #13131f;
            border: 1px solid #1e1e3a;
            border-radius: 12px;
        }
        QScrollBar:vertical {
            background: #0a0a0f;
            width: 4px;
            border-radius: 2px;
        }
        QScrollBar::handle:vertical {
            background: #2d2d5a;
            border-radius: 2px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """

    def _construir_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.stack = QStackedWidget()
        self.stack.setObjectName("main_panel")

        from ui.views.transcriptor import VistaTranscriptor
        from ui.views.historial import VistaHistorial
        from ui.views.documentos import VistaDocumentos
        from ui.views.ajustes import VistaAjustes
        from ui.views.ayuda import VistaAyuda

        self.vista_transcriptor = VistaTranscriptor(self)
        self.vista_historial = VistaHistorial(self)
        self.vista_documentos = VistaDocumentos(self)
        self.vista_ajustes = VistaAjustes(self)
        self.vista_ayuda = VistaAyuda(self)

        self.stack.addWidget(self.vista_transcriptor)
        self.stack.addWidget(self.vista_historial)
        self.stack.addWidget(self.vista_documentos)
        self.stack.addWidget(self.vista_ajustes)
        self.stack.addWidget(self.vista_ayuda)

        self.sidebar = self._crear_sidebar()
        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack)
        self.stack.setCurrentIndex(0)

    def _crear_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(100)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(8, 16, 8, 16)
        layout.setSpacing(2)

        # Logo
        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        lbl_logo = QLabel()
        lbl_logo.setAlignment(Qt.AlignCenter)
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            lbl_logo.setPixmap(pixmap)
        else:
            lbl_logo.setText("🎓")
            lbl_logo.setStyleSheet("font-size: 28px; background: transparent;")
        layout.addWidget(lbl_logo)

        lbl_name = QLabel(APP_NAME)
        lbl_name.setAlignment(Qt.AlignCenter)
        lbl_name.setStyleSheet("font-size: 9px; font-weight: 800; color: #c77dff; background: transparent;")
        layout.addWidget(lbl_name)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background: #1a1a2e; margin: 6px 0; max-height: 1px;")
        layout.addWidget(sep)

        botones = [
            ("📝", "Resumen", 0),
            ("🕐", "Historial", 1),
            ("📁", "Documentos", 2),
            ("⚙️", "Ajustes", 3),
            ("❓", "Ayuda", 4),
        ]
        self.sidebar_btns = []
        for icono, label, idx in botones:
            btn = QPushButton(f"{icono}\n{label}")
            btn.setObjectName("sidebar_btn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, i=idx: self._cambiar_vista(i))
            layout.addWidget(btn)
            self.sidebar_btns.append(btn)

        layout.addStretch()

        tips = QWidget()
        tips.setObjectName("pro_tips")
        tips_layout = QVBoxLayout(tips)
        tips_layout.setContentsMargins(8, 8, 8, 8)
        tips_layout.setSpacing(2)
        for txt, style in [
            ("⭐", "font-size:14px; color:#f9e2af;"),
            ("Pro Tips", "font-size:8px; font-weight:700; color:#f9e2af;"),
            ("Mejores fotos\nmejores\nresúmenes 😊", "font-size:7px; color:#4a4a6a;")
        ]:
            l = QLabel(txt)
            l.setAlignment(Qt.AlignCenter)
            l.setStyleSheet(f"{style} background: transparent;")
            l.setWordWrap(True)
            tips_layout.addWidget(l)
        layout.addWidget(tips)

        self._cambiar_vista(0)
        return sidebar

    def _cambiar_vista(self, idx):
        self.stack.setCurrentIndex(idx)
        for i, btn in enumerate(self.sidebar_btns):
            btn.setObjectName("sidebar_btn_active" if i == idx else "sidebar_btn")
            btn.setStyle(btn.style())

    def procesar(self):
        self.cancelar_flag = False
        worker = Worker(self)
        worker.signals.log.connect(self.vista_transcriptor.log)
        worker.signals.progress.connect(self.vista_transcriptor.actualizar_barra)
        worker.signals.done.connect(self.vista_transcriptor.on_done)
        worker.signals.error.connect(self.vista_transcriptor.on_error)
        self.thread_pool.start(worker)