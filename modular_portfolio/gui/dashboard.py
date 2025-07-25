import sys
from modular_portfolio.modular_core.loader import PluginLoader

def launch_gui():
    try:
        from PyQt5.QtWidgets import (
            QApplication, QMainWindow, QWidget, QPushButton, QGridLayout, QLabel, QVBoxLayout, QScrollArea
        )
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
    except ImportError:
        print("PyQt5 is not installed. Please install it with 'pip install pyqt5' to use the GUI dashboard.")
        return

    loader = PluginLoader()
    plugins = loader.get_plugins('gui')

    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Modular Portfolio Dashboard")
    window.resize(800, 600)

    central = QWidget()
    layout = QVBoxLayout()

    title = QLabel("Modular Portfolio Dashboard")
    title.setFont(QFont("Arial", 20, QFont.Bold))
    title.setAlignment(Qt.AlignCenter)
    layout.addWidget(title)

    grid = QGridLayout()
    for i, plugin in enumerate(plugins):
        btn = QPushButton(plugin['metadata']['name'])
        btn.setMinimumHeight(60)
        btn.setStyleSheet("font-size: 16px; background: #007bff; color: white; border-radius: 8px;")
        btn.clicked.connect(lambda _, p=plugin: p['class']().run('gui'))
        grid.addWidget(btn, i // 3, i % 3)

    grid_widget = QWidget()
    grid_widget.setLayout(grid)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(grid_widget)
    layout.addWidget(scroll)

    central.setLayout(layout)
    window.setCentralWidget(central)
    window.show()
    app.exec_()

if __name__ == "__main__":
    launch_gui()
