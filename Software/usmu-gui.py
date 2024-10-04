#!/usr/bin/env python
from PyQt6 import QtWidgets
import sys
from gui import mainwindow
import argparse
import logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s [%(module)s]: %(message)s")

# kill on Ctrl-C (useful for debugging)
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    parser = argparse.ArgumentParser()
    parser.add_argument("port")
    args = parser.parse_args()
    window = mainwindow.MainWindow(port=args.port)
    window.show()
    try:
        app.exec()
    except KeyboardInterrupt:
        pass
    window.stop_api_worker()