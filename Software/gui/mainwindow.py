import logging
from unittest.mock import right

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QSizePolicy

from gui import smuworker
from gui import measwidget, control, graph

class MainWindow(QtWidgets.QMainWindow):
    log: logging.Logger
    smu_worker: smuworker.SMUWorker

    def __init__(self, *args, **kwargs):
        port = kwargs.pop('port')
        super(MainWindow, self).__init__(*args, **kwargs)
        self.log = logging.getLogger("smugui")
        self.smu_worker = smuworker.SMUWorker(port)

        w = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        leftlayout = QtWidgets.QVBoxLayout()
        mw = measwidget.LiveMeasurementWidget()
        self.smu_worker.signals.vi_measurement_received.connect(mw.measurement_received)
        leftlayout.addWidget(mw)
        cw = control.ControlWidget(self.smu_worker)
        leftlayout.addWidget(cw)

        rightlayout = QtWidgets.QHBoxLayout()
        gw = graph.HistoryGraphWidget()
        self.smu_worker.signals.vi_measurement_received.connect(gw.measurement_received)
        rightlayout.addWidget(gw)

        layout.addLayout(leftlayout)
        layout.addLayout(rightlayout)
        layout.setStretch(0, 10)
        layout.setStretch(1, 50)

        w.setLayout(layout)
        self.setCentralWidget(w)

        self.threadpool = QtCore.QThreadPool()
        self.threadpool.start(self.smu_worker)

    def stop_api_worker(self):
        self.smu_worker.stop()
        self.threadpool.waitForDone(1000)
