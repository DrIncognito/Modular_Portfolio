from modular_portfolio.modular_core.interface import BasePlugin

class InfoTool (BasePlugin):
    def run(self, mode: str):
        if mode == 'cli':
            print("\n[InfoTool CLI]")
            print("This is a CLI plugin demo. You can add your own logic here!")
            print("Try running this tool in web or GUI mode for a different experience.\n")
        elif mode == 'web':
            # Use Flask's render_template to render a Jinja2 template
            from flask import render_template
            return render_template('info_tool.html')
        elif mode == 'gui':
            try:
                from PyQt5.QtWidgets import QMessageBox, QApplication
                app = QApplication.instance() or QApplication([])
                msg = QMessageBox()
                msg.setWindowTitle("ExampleModule GUI Info")
                msg.setText("This is a PyQt5 GUI plugin demo!\nYou can build custom dialogs and widgets here.")
                msg.exec_()
            except ImportError:
                print("PyQt5 is not installed. Please install it to use GUI features.")
        else:
            print(f"Unknown mode: {mode}")
