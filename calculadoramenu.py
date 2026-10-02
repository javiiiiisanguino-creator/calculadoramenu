import math
import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

BLUE_DARK = "#1a237e"
BLUE_MED = "#283593"
BLUE_LIGHT = "#3949ab"
BLUE_ACCENT = "#5c6bc0"
BLUE_PALE = "#e8eaf6"
WHITE = "#ffffff"
GRAY_LIGHT = "#f5f5f5"
GRAY_BORDER = "#d0d3d8"
RED = "#c62828"
RED_HOVER = "#e53935"

MAX_HISTORIAL = 5
SIMBOLOS = {"+": "+", "-": "-", "*": "×", "/": "÷"}


class DialogoAcercaDe(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Acerca de la Calculadora")
        self.setFixedSize(300, 200)
        self.setStyleSheet(f"background-color: {WHITE};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título
        lbl_titulo = QLabel("Calculadora Básica")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        lbl_titulo.setStyleSheet(f"""
            color: {BLUE_DARK};
            font-family: 'Segoe UI';
            font-size: 14pt;
            font-weight: bold;
        """)
        layout.addWidget(lbl_titulo)

        # Información
        lbl_info = QLabel("Realizado por Javier Sanguino - 2026\nPySide6 Edition")
        lbl_info.setAlignment(Qt.AlignCenter)
        lbl_info.setStyleSheet(f"""
            color: {BLUE_MED};
            font-family: 'Segoe UI';
            font-size: 10pt;
        """)
        layout.addWidget(lbl_info)

        # Botón Cerrar
        btn_cerrar = QPushButton("Aceptar")
        btn_cerrar.setCursor(Qt.PointingHandCursor)
        btn_cerrar.clicked.connect(self.accept)
        btn_cerrar.setStyleSheet(f"""
            QPushButton {{
                background-color: {BLUE_ACCENT};
                color: {WHITE};
                font-family: 'Segoe UI';
                font-size: 10pt;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {BLUE_LIGHT};
            }}
        """)
        layout.addWidget(btn_cerrar)


class Calculadora(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Calculadora")
        self.setFixedSize(360, 640)
        self.setStyleSheet(f"background-color: {GRAY_LIGHT};")

        self._operacion = None
        self._operandos = []
        self._nuevo_numero = False
        self._error_activo = False
        self._historial = []

        self._crear_menu()
        self._construir_interfaz()
        self._refrescar_historial()

    # ------------------------------------------------------------------ MENU

    def _crear_menu(self):
        barra_menu = self.menuBar()
        barra_menu.setStyleSheet(f"""
            QMenuBar {{
                background-color: {WHITE};
                color: {BLUE_DARK};
                font-family: 'Segoe UI';
                font-size: 10pt;
            }}
            QMenuBar::item {{
                background: transparent;
                padding: 6px 12px;
                color: {BLUE_DARK};
            }}
            QMenuBar::item:selected {{
                background-color: {BLUE_PALE};
            }}
            QMenu {{
                background-color: {WHITE};
                border: 1px solid {GRAY_BORDER};
            }}
            QMenu::item {{
                padding: 6px 24px;
                color: {BLUE_DARK};
            }}
            QMenu::item:selected {{
                background-color: {BLUE_ACCENT};
                color: {WHITE};
            }}
        """)

        # Menú Calculadora
        menu_calc = barra_menu.addMenu("Calculadora")

        accion_limpiar = QAction("Limpiar (C)", self)
        accion_limpiar.setShortcut(QKeySequence("Ctrl+L"))
        accion_limpiar.triggered.connect(self._limpiar)
        menu_calc.addAction(accion_limpiar)

        menu_calc.addSeparator()

        accion_salir = QAction("Salir", self)
        accion_salir.setShortcut(QKeySequence("Ctrl+Q"))
        accion_salir.triggered.connect(self.close)
        menu_calc.addAction(accion_salir)

        # Menú Acerca de...
        menu_acerca = barra_menu.addMenu("Acerca de...")

        accion_info = QAction("Información", self)
        accion_info.setShortcut(QKeySequence("F1"))
        accion_info.triggered.connect(self._mostrar_acerca_de)
        menu_acerca.addAction(accion_info)

    def _mostrar_acerca_de(self):
        dialogo = DialogoAcercaDe(self)
        dialogo.exec()

    # ------------------------------------------------------------------ UI

    def _construir_interfaz(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        contenedor = QVBoxLayout(central_widget)
        contenedor.setContentsMargins(20, 16, 20, 16)
        contenedor.setSpacing(10)

        # Header
        header = QLabel("Calculadora Básica")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(f"""
            background-color: {BLUE_DARK};
            color: {WHITE};
            font-family: 'Segoe UI';
            font-size: 16px;
            font-weight: bold;
            border-radius: 8px;
            padding: 12px;
        """)
        contenedor.addWidget(header)

        # Pantalla principal
        self.pantalla = QLabel("0")
        self.pantalla.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.pantalla.setStyleSheet(f"""
            background-color: {WHITE};
            color: {BLUE_DARK};
            font-family: 'Consolas';
            font-size: 24px;
            font-weight: bold;
            border: 2px solid {BLUE_ACCENT};
            border-radius: 8px;
            padding: 10px 15px;
        """)
        contenedor.addWidget(self.pantalla)

        # Operación en curso
        self.lbl_operacion = QLabel("")
        self.lbl_operacion.setAlignment(Qt.AlignRight)
        self.lbl_operacion.setStyleSheet(
            f"color: {BLUE_DARK}; font-family: 'Segoe UI'; font-size: 11px; background: transparent;"
        )
        contenedor.addWidget(self.lbl_operacion)

        self._construir_teclado(contenedor)
        self._construir_historial(contenedor)

        # Footer
        footer = QLabel("Realizado por Javier Sanguino - 2026")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(f"""
            background-color: {BLUE_PALE};
            color: {BLUE_DARK};
            font-family: 'Segoe UI';
            font-size: 9px;
            border-radius: 6px;
            padding: 6px;
        """)
        contenedor.addWidget(footer)

    def _construir_teclado(self, padre_layout):
        marco_teclado = QWidget()
        grid = QGridLayout(marco_teclado)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(6)

        botones = [
            ("7", 0, 0), ("8", 0, 1), ("9", 0, 2), ("/", 0, 3),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2), ("*", 1, 3),
            ("1", 2, 0), ("2", 2, 1), ("3", 2, 2), ("-", 2, 3),
            ("0", 3, 0), (".", 3, 1), ("C", 3, 2), ("+", 3, 3),
        ]

        for texto, fila, col in botones:
            if texto in SIMBOLOS:
                bg, hover, fg = BLUE_MED, BLUE_DARK, WHITE
                comando = lambda _, t=texto: self._operador(t)
            elif texto == "C":
                bg, hover, fg = RED, RED_HOVER, WHITE
                comando = self._limpiar
            else:
                bg, hover, fg = BLUE_PALE, BLUE_ACCENT, BLUE_DARK
                comando = lambda _, t=texto: self._digito(t)

            btn = QPushButton(texto)
            btn.setFixedSize(65, 45)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(comando)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg};
                    color: {fg};
                    font-family: 'Segoe UI';
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 8px;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: {hover};
                }}
            """)
            grid.addWidget(btn, fila, col)

        btn_igual = QPushButton("=")
        btn_igual.setFixedHeight(45)
        btn_igual.setCursor(Qt.PointingHandCursor)
        btn_igual.clicked.connect(self._igual)
        btn_igual.setStyleSheet(f"""
            QPushButton {{
                background-color: {BLUE_ACCENT};
                color: {WHITE};
                font-family: 'Segoe UI';
                font-size: 18px;
                font-weight: bold;
                border-radius: 8px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {BLUE_LIGHT};
            }}
        """)
        grid.addWidget(btn_igual, 4, 0, 1, 4)
        padre_layout.addWidget(marco_teclado)

    def _construir_historial(self, padre_layout):
        marco = QFrame()
        marco.setStyleSheet(f"""
            QFrame {{
                background-color: {WHITE};
                border: 1px solid {GRAY_BORDER};
                border-radius: 8px;
            }}
        """)
        layout_hist = QVBoxLayout(marco)
        layout_hist.setContentsMargins(10, 8, 10, 8)

        lbl_titulo = QLabel(f"Historial (últimas {MAX_HISTORIAL} operaciones)")
        lbl_titulo.setStyleSheet(
            f"color: {BLUE_MED}; font-family: 'Segoe UI'; font-size: 10px; font-weight: bold; border: none; background: transparent;"
        )
        layout_hist.addWidget(lbl_titulo)

        self.marco_historial_interno = QVBoxLayout()
        self.marco_historial_interno.setSpacing(2)
        layout_hist.addLayout(self.marco_historial_interno)

        btn_limpiar = QPushButton("Limpiar historial")
        btn_limpiar.setCursor(Qt.PointingHandCursor)
        btn_limpiar.clicked.connect(self._limpiar_historial)
        btn_limpiar.setStyleSheet(f"""
            QPushButton {{
                background-color: {BLUE_PALE};
                color: {BLUE_DARK};
                font-family: 'Segoe UI';
                font-size: 9px;
                border-radius: 6px;
                padding: 4px 8px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {BLUE_ACCENT};
                color: {WHITE};
            }}
        """)
        layout_hist.addWidget(btn_limpiar, alignment=Qt.AlignRight)
        padre_layout.addWidget(marco)

    # ----------------------------------------------------------- historial

    def _registrar_historial(self, a, b, op, resultado):
        self._historial.insert(0, (a, b, op, resultado))
        del self._historial[MAX_HISTORIAL:]
        self._refrescar_historial()

    def _refrescar_historial(self):
        while self.marco_historial_interno.count():
            item = self.marco_historial_interno.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self._historial:
            lbl = QLabel("Sin operaciones")
            lbl.setStyleSheet(
                "color: #9e9e9e; font-family: 'Segoe UI'; font-size: 9px; font-style: italic; border: none; background: transparent;"
            )
            self.marco_historial_interno.addWidget(lbl)
            return

        for indice, (a, b, op, resultado) in enumerate(self._historial, start=1):
            fila = QWidget()
            fila.setStyleSheet("background: transparent; border: none;")
            layout_fila = QHBoxLayout(fila)
            layout_fila.setContentsMargins(0, 1, 0, 1)

            lbl_idx = QLabel(f"{indice}.")
            lbl_idx.setStyleSheet("color: #9e9e9e; font-family: 'Segoe UI'; font-size: 9px;")
            lbl_idx.setFixedWidth(20)

            lbl_op = QLabel(f"{self._formatear(a)} {SIMBOLOS[op]} {self._formatear(b)}")
            lbl_op.setStyleSheet(f"color: {BLUE_MED}; font-family: 'Consolas'; font-size: 10px;")

            lbl_res = QLabel(f"= {self._formatear(resultado)}")
            lbl_res.setAlignment(Qt.AlignRight)
            lbl_res.setStyleSheet(
                f"color: {BLUE_DARK}; font-family: 'Consolas'; font-size: 10px; font-weight: bold;"
            )

            layout_fila.addWidget(lbl_idx)
            layout_fila.addWidget(lbl_op, 1)
            layout_fila.addWidget(lbl_res)

            self.marco_historial_interno.addWidget(fila)

    def _limpiar_historial(self):
        self._historial = []
        self._refrescar_historial()

    # ------------------------------------------------------------- lógica

    def _digito(self, texto):
        if self._error_activo:
            self._reiniciar()

        actual = self.pantalla.text()
        if self._nuevo_numero:
            actual = "0"
            self._nuevo_numero = False

        if texto == ".":
            if "." in actual:
                return
            if actual in ("0", "-0"):
                self._cambiar_texto("0.")
            else:
                self._cambiar_texto(actual + ".")
            return

        if actual in ("0", "-0"):
            self._cambiar_texto(texto)
        else:
            self._cambiar_texto(actual + texto)

    def _operador(self, op):
        if self._error_activo:
            self._reiniciar()

        valor = self._leer_pantalla()
        if valor is None:
            return

        if self._operacion is not None and not self._nuevo_numero:
            resultado = self._calcular(self._operandos[0], valor, self._operacion)
            if resultado is None:
                return
            self._registrar_historial(self._operandos[0], valor, self._operacion, resultado)
            self._operandos = [resultado]
            self._cambiar_texto(self._formatear(resultado))
        else:
            self._operandos = [valor]

        self._operacion = op
        self._nuevo_numero = True
        self.lbl_operacion.setText(f"{self._formatear(self._operandos[0])} {SIMBOLOS[op]}")

    def _igual(self):
        if self._operacion is None or len(self._operandos) < 1:
            return

        valor = self._leer_pantalla()
        if valor is None:
            return

        a, b, op = self._operandos[0], valor, self._operacion
        resultado = self._calcular(a, b, op)

        self._operacion = None
        self._operandos = []
        self._nuevo_numero = True
        self.lbl_operacion.setText("")

        if resultado is None:
            return

        self._registrar_historial(a, b, op, resultado)
        self._cambiar_texto(self._formatear(resultado))

    def _calcular(self, a, b, op):
        try:
            if op == "+":
                resultado = a + b
            elif op == "-":
                resultado = a - b
            elif op == "*":
                resultado = a * b
            elif op == "/":
                if b == 0:
                    self._error("No se puede dividir entre cero")
                    return None
                resultado = a / b
            else:
                self._error("Operación no válida")
                return None

            if not math.isfinite(resultado):
                self._error("El resultado es demasiado grande")
                return None
            return resultado
        except ZeroDivisionError:
            self._error("No se puede dividir entre cero")
            return None
        except (OverflowError, ValueError):
            self._error("Error en la operación")
            return None

    def _leer_pantalla(self):
        try:
            valor = float(self.pantalla.text())
            if not math.isfinite(valor):
                raise ValueError
            return valor
        except ValueError:
            self._error("Entrada no válida")
            return None

    def _formatear(self, valor):
        if valor == int(valor) and abs(valor) < 1e16:
            return str(int(valor))
        return f"{valor:.10g}"

    def _cambiar_texto(self, texto):
        self.pantalla.setText(texto)

    def _error(self, mensaje):
        self.pantalla.setText(mensaje)
        self._operacion = None
        self._operandos = []
        self._nuevo_numero = True
        self._error_activo = True
        self.lbl_operacion.setText("")
        self._mostrar_error(mensaje)

    def _mostrar_error(self, mensaje):
        box = QMessageBox(
            QMessageBox.Icon.Warning,
            "Error",
            mensaje,
            QMessageBox.StandardButton.Ok,
            self,
        )
        box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {WHITE};
            }}
            QMessageBox QLabel {{
                color: #000000;
                font-family: 'Segoe UI';
                font-size: 11pt;
            }}
            QMessageBox QPushButton {{
                background-color: {RED};
                color: {WHITE};
                font-family: 'Segoe UI';
                font-size: 10pt;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 6px 24px;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {RED_HOVER};
            }}
        """)
        for etiqueta in box.findChildren(QLabel):
            etiqueta.setStyleSheet(
                "color: #000000; background: transparent; font-family: 'Segoe UI'; font-size: 11pt;"
            )
        box.exec()

    def _limpiar(self):
        self._reiniciar()

    def _reiniciar(self):
        self._operacion = None
        self._operandos = []
        self._nuevo_numero = False
        self._error_activo = False
        self.lbl_operacion.setText("")
        self._cambiar_texto("0")

    # ----------------------------------------------------------- teclado físico

    def keyPressEvent(self, evento):
        texto = evento.text()
        if texto.isdigit() or texto == ".":
            self._digito(texto)
        elif texto in SIMBOLOS:
            self._operador(texto)
        elif evento.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Equal):
            self._igual()
        elif evento.key() == Qt.Key_Backspace:
            if self._error_activo:
                self._reiniciar()
                return
            if self._nuevo_numero:
                self._cambiar_texto("0")
                return
            actual = self.pantalla.text()
            nuevo = actual[:-1] if len(actual) > 1 else "0"
            if nuevo in ("", "-", "+", "-."):
                nuevo = "0"
            self._cambiar_texto(nuevo)
        elif evento.key() == Qt.Key_Escape:
            self._limpiar()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    calc = Calculadora()
    calc.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()