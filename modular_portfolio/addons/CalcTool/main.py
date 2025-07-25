
from modular_portfolio.modular_core.interface import BasePlugin
from modular_portfolio.modular_core.loader import PluginLoader
try:
    from core import calculate, Operation  # Use installed CalcModule
except ImportError:
    # fallback or error if CalcModule is not installed
    calculate = None
    Operation = None

def eval_expression(expr: str):
    # Only basic arithmetic for demo: +, -, *, /
    import re
    expr = expr.replace(' ', '')
    # Match a simple binary operation: a+b, a-b, a*b, a/b
    m = re.match(r'^([-+]?\d*\.?\d+)([+\-*/])([-+]?\d*\.?\d+)$', expr)
    if not m:
        raise ValueError("Only simple expressions like 2+2, 3*4, 5-1, 8/2 are supported.")
    a, op, b = m.groups()
    a = float(a)
    b = float(b)
    if op == '+':
        return calculate(operation=Operation.ADD, a=a, b=b)
    elif op == '-':
        return calculate(operation=Operation.SUBTRACT, a=a, b=b)
    elif op == '*':
        return calculate(operation=Operation.MULTIPLY, a=a, b=b)
    elif op == '/':
        return calculate(operation=Operation.DIVIDE, a=a, b=b)
    else:
        raise ValueError("Unsupported operator.")

class CalcTool(BasePlugin):
    def run(self, mode: str):
        if mode == 'cli':
            print("\n[CalcTool CLI]")
            # Try to run the installed CalcModule CLI interactively
        elif mode == 'web':
            return None
        elif mode == 'gui':
            try:
                from PyQt5.QtWidgets import QInputDialog, QMessageBox, QApplication
                app = QApplication.instance() or QApplication([])
                expr, ok = QInputDialog.getText(None, "CalcTool", "Enter expression to calculate (e.g. 2+2):")
                if ok and expr:
                    try:
                        result = eval_expression(expr)
                        QMessageBox.information(None, "Result", f"Result: {result}")
                    except Exception as e:
                        QMessageBox.critical(None, "Error", str(e))
            except ImportError:
                print("PyQt5 is not installed.")
        else:
            print(f"Mode {mode} not supported.")
