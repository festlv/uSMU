from PyQt6.QtCore import QRunnable, pyqtSlot, pyqtSignal, QObject, QCoreApplication
import time
import logging
import typing
import usmu.usmudevice
import threading

class SMUWorkerSignals(QObject):
    vi_measurement_received = pyqtSignal(usmu.usmudevice.VIMeasurement)

class SMUWorker(QRunnable):
    should_stop: bool
    log: logging.Logger
    signals: SMUWorkerSignals
    smu: usmu.usmudevice.SMU
    lock: threading.Lock

    def __init__(self, port:str):
        super().__init__()
        self.log = logging.getLogger("smuworker")
        self.smu = usmu.usmudevice.SMU(port)
        self.signals = SMUWorkerSignals()
        self.should_stop = False
        self.lock = threading.Lock()

    def stop(self):
        self.should_stop = True


    @pyqtSlot()
    def run(self):
        self.log.info("starting loop")

        while not self.should_stop:
            with self.lock:
                meas = self.smu.measure_voltage_current()
                self.signals.vi_measurement_received.emit(meas)
            time.sleep(0.01)
