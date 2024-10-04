import usmu.scpidevice as scpidevice
import typing
from dataclasses import dataclass
import logging
import usmu.cal as cal


@dataclass
class VIMeasurement:
    voltage: float
    current: float

class SMU(scpidevice.SCPIDevice):
    def idn(self) -> typing.Optional[scpidevice.IDNResponse]:
        resp = self.query("*IDN?")
        try:
            if resp:
                fields = resp.split(" ")
                return scpidevice.IDNResponse(manufacturer=fields[0],
                                   model=fields[0],
                                   version=fields[2],
                                   serial_number=fields[3])
        except TypeError:
            raise scpidevice.SCPIException(f"Invalid response to *IDN?: '{resp}'")
        return None


    def enable_output(self):
        return self.cmd("CH1:ENA")

    def disable_output(self):
        return self.cmd("CH1:DIS")

    def set_output_current_limit_dac(self, value:int):
        return self.cmd(f"ILIM {value}")

    def set_output_voltage_dac(self, value:int):
        return self.cmd(f"DAC {value}")

    def set_and_measure_voltage_current(self, output_voltage:float):
        resp = self.query(f"CH1:MEA:VOL {output_voltage:.3E}").split(",")
        return VIMeasurement(float(resp[0]), float(resp[1]))

    def measure_voltage_current(self):
        resp = self.query(f"CH1:MEA:VOL").split(",")
        return VIMeasurement(float(resp[0]), float(resp[1]))

    def set_voltage(self, volt: float):
        self.cmd(f"CH1:VOL {volt:.3E}")

    def set_current_limit(self, curr: float):
        self.cmd(f"CH1:CUR {curr:.3E}")

    def set_current_range(self, r:int):
        return self.cmd(f"CH1:RANGE {r}")

    def cal_zero_current_offset_write(self, i_range:int, fit:cal.LinFitResult):
        self.cmd(f"CAL:CUR:RANGE{i_range} {fit.slope:.5E} {fit.intercept:.5E}")

    def cal_zero_current_offset(self, dry_run=True):
        """
        Perform a zero current offset calibration on all current ranges
        :param dry_run:
        :return:
        """
        self.enable_output()
        self.set_output_current_limit_dac(100)

        cal_v_steps = [-5, -2.5, -1, 0, 1, 2.5, 5]
        for i_range in range(1, 4+1):
            self.log.info(f"starting calibration for range {i_range}")
            self.set_current_range(i_range)
            fit = cal.LinFitter()
            for v_step in cal_v_steps:
                # for some reason, first measurement when changing the voltage returns wildly different current measurement
                _ = self.set_and_measure_voltage_current(v_step)
                meas = self.set_and_measure_voltage_current(v_step)
                self.log.info(f"v_step={v_step}, V={meas.voltage}V, I={meas.current}A")
                fit.add_point(meas.voltage, -meas.current)
            fit_res = fit.fit()
            self.log.info(f"linear fit result: {fit_res}")
            if not dry_run:
                self.log.info(f"writing coefficients for range {i_range}")
                self.cal_zero_current_offset_write(i_range, fit_res)

    def cal_ilimit_write(self, fit:cal.LinFitResult):
        self.cmd(f"CAL:ILIM {fit.slope:.5E} {fit.intercept:.5E}")

    def cal_ilimit(self, askfunc, dry_run=True):
        self.log.info("starting output current calibration...")
        self.enable_output()
        self.set_voltage(5)
        fit = cal.LinFitter()
        for istep in range(400, 4096, 600):
            self.log.info(f"setting ilim={istep}")
            self.set_output_current_limit_dac(istep)
            current_ma = askfunc()
            fit.add_point(current_ma, istep)
            self.log.info(f"ilim={istep},current={current_ma}mA")
        fit_res = fit.fit()
        self.log.info(f"linear fit result: {fit_res}")
        if not dry_run:
            self.log.info("writing coefficients for current calibration")
            self.cal_ilimit_write(fit_res)

    def cal_vdac_write(self, fit:cal.LinFitResult):
        self.cmd(f"CAL:DAC {round(fit.slope, 2)} {round(fit.intercept, 2)}")

    def cal_vdac(self, askfunc, dry_run=True):
        self.log.info("starting output voltage calibration...")
        self.enable_output()
        self.set_output_current_limit_dac(100)
        fit = cal.LinFitter()
        for vstep in range(5000, 55000, 7500):
            self.log.info(f"setting vdac={vstep}")
            self.set_output_voltage_dac(vstep)
            volt = askfunc()
            fit.add_point(volt, vstep)
            self.log.info(f"vdac={vstep},voltage={volt}V")
        fit_res = fit.fit()
        self.log.info(f"linear fit result: {fit_res}")
        if not dry_run:
            self.log.info("writing coefficients for current calibration")
            self.cal_ilimit_write(fit_res)

    def cal_vadc_write(self, fit: cal.LinFitResult):
        self.cmd(f"CAL:ADC {fit.slope:.5E} {fit.intercept:.5E}")

    def cal_vadc(self, askfunc, dry_run=True):
        self.log.info("starting voltage measurement calibration...")
        self.enable_output()
        self.set_output_current_limit_dac(100)
        self.cmd("CH1:VCAL")
        fit = cal.LinFitter()
        for vstep in range(-5, 6, 1):
            self.log.info(f"setting voltage={vstep}")
            _ = self.set_and_measure_voltage_current(vstep)
            meas = self.set_and_measure_voltage_current(vstep)
            act_v = askfunc()
            fit.add_point(meas.voltage, act_v)
            self.log.info(f"set voltage={vstep}, ADC counts={meas.voltage}, actual voltage={act_v}")
        fit_res = fit.fit()
        self.log.info(f"linear fit result: {fit_res}")
        if not dry_run:
            self.log.info("writing coefficients for ADC calibration")
            self.cal_vadc_write(fit_res)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    smu = SMU("/dev/ttyACM0")
    print(smu.idn())
    #smu.enable_output()
    #smu.set_output_current_limit_dac(100)
    #print(smu.set_and_measure_voltage_current(1))
    smu.cal_zero_current_offset(dry_run=False)