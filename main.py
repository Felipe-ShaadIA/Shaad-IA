import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from ui.app import ShaadApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = ShaadApp()
    ventana.show()
    sys.exit(app.exec())