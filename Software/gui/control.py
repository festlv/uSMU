from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import QLabel, QLineEdit, QPushButton
from gui import smuworker
from gui.smuworker import SMUWorker


class ULineEdit(QtWidgets.QWidget):
    line_edit: QLineEdit
    unit_label: QLabel

    def __init__(self, unit:str):
        super().__init__()
        layout = QtWidgets.QHBoxLayout()
        self.line_edit = QLineEdit()
        self.unit_label = QLabel(unit)
        self.unit_label.setFixedWidth(40)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.unit_label)
        self.setLayout(layout)


class ControlWidget(QtWidgets.QGroupBox):
    volt_sp: ULineEdit
    curr_sp: ULineEdit
    smuw: smuworker.SMUWorker
    pb_set: QPushButton
    pb_enable: QPushButton
    pb_disable: QPushButton
    def __init__(self, smuw:SMUWorker):
        super().__init__()
        self.smuw = smuw
        self.setTitle("Output control")
        l = QtWidgets.QFormLayout()
        self.volt_sp = ULineEdit("V")
        self.volt_sp.line_edit.setText("5.0")
        self.volt_sp.line_edit.setValidator(QDoubleValidator(-5, 5, 3))
        l.addRow("Set voltage:", self.volt_sp)

        self.curr_sp = ULineEdit("mA")
        self.curr_sp.line_edit.setText("10")
        self.curr_sp.line_edit.setValidator(QDoubleValidator(0, 50, 1))
        l.addRow("Current limit:", self.curr_sp)

        self.pb_set = QPushButton("Set")
        self.pb_set.clicked.connect(self.handle_set)
        l.addRow("", self.pb_set)

        self.pb_enable = QPushButton("Enable")
        self.pb_enable.clicked.connect(self.handle_enable)
        self.pb_disable = QPushButton("Disable")
        self.pb_disable.clicked.connect(self.handle_disable)
        l.addRow(self.pb_disable, self.pb_enable)

        self.setStyleSheet("font-family: mono;font-size: 16pt;")
        self.setLayout(l)

    def handle_set(self):
        volt = float(self.volt_sp.line_edit.text())
        curr = float(self.curr_sp.line_edit.text())
        with self.smuw.lock:
            self.smuw.smu.set_voltage(volt)
            self.smuw.smu.set_current_limit(curr)

    def handle_disable(self):
        with self.smuw.lock:
            self.smuw.smu.disable_output()

    def handle_enable(self):
        with self.smuw.lock:
            self.smuw.smu.enable_output()