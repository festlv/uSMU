#!/usr/bin/env python
import argparse
import usmu.usmudevice
import logging

class USMUCLI:

    def main(self):
        parser = argparse.ArgumentParser(prog="usmu-cli.py")
        parser.add_argument("port", help="Serial port")
        parser.add_argument("-d", "--debug", action='store_true')
        subparsers = parser.add_subparsers(title='commands', required=True)

        idn = subparsers.add_parser('identify', help="Identify attached device")
        idn.set_defaults(func=self.identify)
        ioffs = subparsers.add_parser('calibrate-current-offset', help="Calibrate zero-current offset")
        ioffs.set_defaults(func=self.calibrate_current_offset)
        vdac = subparsers.add_parser('calibrate-vdac', help="Calibrate voltage output")
        vdac.set_defaults(func=self.calibrate_output_voltage)
        vadc = subparsers.add_parser('calibrate-vadc', help="Calibrate voltage measurement")
        vadc.set_defaults(func=self.calibrate_measured_voltage)
        ilim = subparsers.add_parser('calibrate-ilim', help="Calibrate output current limit")
        ilim.set_defaults(func=self.calibrate_output_current)

        args = parser.parse_args()
        loglevel = logging.INFO
        if args.debug:
            loglevel = logging.DEBUG

        logging.basicConfig(level=loglevel)

        self.smu = usmu.usmudevice.SMU(args.port)
        args.func(args)

    def identify(self, args):
        print(self.smu.idn())

    def calibrate_current_offset(self, args):
        input("Disconnect everything from the output terminal of the uSMU, Enter to continue...")
        self.smu.cal_zero_current_offset(dry_run=False)
        print("Calibration finished, restarting device...")
        self.smu.reset()

    def calibrate_output_current(self, args):
        input("Connect ammeter in mA mode to output terminal, Enter to continue...")
        def askfunc():
            return float(input("Measured current (mA): "))
        self.smu.cal_ilimit(askfunc, False)
        print("Calibration finished, restarting device...")
        self.smu.reset()

    def calibrate_output_voltage(self, args):
        input("Connect voltmeter to output terminal, Enter to continue...")
        def askfunc():
            return float(input("Measured voltage (V): "))

        self.smu.cal_vdac(askfunc, False)
        print("Calibration finished, restarting device...")
        self.smu.reset()

    def calibrate_measured_voltage(self, args):
        input("Connect voltmeter to output terminal, Enter to continue...")
        def askfunc():
            return float(input("Measured voltage (V): "))

        self.smu.cal_vadc(askfunc, False)
        print("Calibration finished, restarting device...")
        self.smu.reset()


if __name__ == "__main__":
    cli = USMUCLI()
    cli.main()


