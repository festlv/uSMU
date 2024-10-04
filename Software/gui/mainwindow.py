import logging
from PyQt6 import QtWidgets, QtCore
from gui import smuworker
from gui import measwidget, control

class MainWindow(QtWidgets.QMainWindow):
    log: logging.Logger
    smu_worker: smuworker.SMUWorker

    def __init__(self, *args, **kwargs):
        port = kwargs.pop('port')
        super(MainWindow, self).__init__(*args, **kwargs)
        self.log = logging.getLogger("smugui")
        self.smu_worker = smuworker.SMUWorker(port)

        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        mw = measwidget.LiveMeasurementWidget()
        self.smu_worker.signals.vi_measurement_received.connect(mw.measurement_received)
        layout.addWidget(mw)

        cw = control.ControlWidget(self.smu_worker)
        layout.addWidget(cw)

        w.setLayout(layout)
        self.setCentralWidget(w)

        self.threadpool = QtCore.QThreadPool()
        self.threadpool.start(self.smu_worker)

    def stop_api_worker(self):
        self.smu_worker.stop()
        self.threadpool.waitForDone(1000)
