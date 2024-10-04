from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QLabel

from usmu.usmudevice import VIMeasurement

class MeasWidgetBase(QtWidgets.QGroupBox):
    def measurement_received(self, meas:VIMeasurement):
        pass

class LiveMeasurementWidget(MeasWidgetBase):
    volt_label: QLabel
    curr_label: QLabel

    def __init__(self):
        super().__init__()
        self.setTitle("Live measurement")
        l = QtWidgets.QHBoxLayout()
        self.volt_label = QLabel(self)
        self.curr_label = QLabel(self)
        l.addWidget(self.volt_label)
        l.addWidget(self.curr_label)
        self.setStyleSheet("font-family: mono;font-size: 16pt;")
        self.setLayout(l)

    def measurement_received(self, meas: VIMeasurement):
        val = meas.voltage
        label = self.volt_label
        if abs(val) > 1:
            label.setText(f"{val:4.3f}V")
        elif abs(val) > 0.001:
            val = val * 1e3
            label.setText(f"{val:5.2f}mV")

        val = meas.current
        label = self.curr_label
        if abs(val) > 1e-3:
            val = val*1e3
            label.setText(f"{val:4.3f}mA")
        elif abs(val) > 1e-6:
            val = val * 1e6
            label.setText(f"{val:5.2f}uA")
        else:
            val = val * 1e9
            label.setText(f"{val:5.2f}nA")





