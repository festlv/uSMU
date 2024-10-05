from PyQt6 import QtWidgets
import pyqtgraph as pg
from usmu.usmudevice import VIMeasurement
import time
import typing

class HistoryGraphWidget(QtWidgets.QGroupBox):
    gv: pg.PlotWidget
    measurements: typing.List[typing.Tuple[float, VIMeasurement]]

    v_plot: pg.PlotItem
    i_plot: pg.ViewBox
    def __init__(self):
        pg.setConfigOption("useOpenGL", True)
        super().__init__()
        l = QtWidgets.QHBoxLayout()
        self.gv = pg.PlotWidget()
        self.gv.setLabel('bottom', 'Time (s)')
        p1 = self.gv.plotItem
        p1.setLabel(axis="left", text='Voltage', units="V", color="blue")
        p2 = pg.ViewBox()
        p1.showAxis("right")
        p1.scene().addItem(p2)
        p1.getAxis("right").linkToView(p2)
        p2.setXLink(p1)
        p1.getAxis("right").setLabel("Current", units="A", color="red")
        p1.vb.sigResized.connect(self.updateViews)
        self.v_plot = p1
        self.i_plot = p2

        self.updateViews()

        l.addWidget(self.gv)
        self.setLayout(l)
        self.measurements = []

    def measurement_received(self, meas: VIMeasurement):
        self.measurements.append((time.time(), meas))

        datapoints_v = []
        datapoints_i = []
        timestamps = []
        for ts, m in self.measurements:
            rel_ts = time.time() - ts
            if rel_ts < 30:
                plot_ts = 30 - rel_ts
                datapoints_v.append(m.voltage)
                datapoints_i.append(m.current)
                timestamps.append(plot_ts)
        self.v_plot.plot(timestamps, datapoints_v, pen="b", clear=True)
        self.i_plot.clear()
        self.i_plot.addItem(pg.PlotCurveItem( timestamps, datapoints_i, pen="r"))


    def updateViews(self):
        ## view has resized; update auxiliary views to match
        self.i_plot.setGeometry(self.v_plot.vb.sceneBoundingRect())

        ## need to re-update linked axes since this was called
        ## incorrectly while views had different shapes.
        ## (probably this should be handled in ViewBox.resizeEvent)
        self.i_plot.linkedViewChanged(self.v_plot.vb, self.i_plot.XAxis)

