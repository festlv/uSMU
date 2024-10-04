import serial
import logging
import typing
from collections import namedtuple
import time

IDNResponse = namedtuple("IDNResponse", ["manufacturer","model", "serial_number", "version"])

class SCPIException(Exception):
    pass

class SCPIDevice:
    def __init__(self, device, baud_rate=9600):
        self.log = logging.getLogger("scpidev")
        self.dev = serial.Serial(port=device, baudrate=baud_rate, timeout=1)

    def query(self, q:str) -> typing.Optional[str]:
        self.log.debug(f"query: {q}")
        q_term =  q + "\n"
        self.dev.write(q_term.encode("ascii"))
        resp = self.dev.readline()
        if resp:
            resp = resp.rstrip().decode("ascii")
            self.log.debug(f"response: {resp}")
            if resp.startswith("**ERROR"):
                raise SCPIException(f"SCPI error encountered while executing '{q}': {resp}")
            return resp
        return None

    def cmd(self, cmd: str):
        self.log.debug(f"cmd: {cmd}")
        cmd_term = cmd + "\n"
        self.dev.write(cmd_term.encode("ascii"))
        # if the next command is sent too fast, it is not processed by device
        time.sleep(0.1)

    def reset(self):
        self.cmd("*RST")
        self.dev.close()

    def idn(self) -> typing.Optional[IDNResponse]:
        resp = self.query("*IDN?")
        try:
            if resp:
                return IDNResponse(*(resp.split(",")))
        except TypeError:
            raise SCPIException(f"Invalid response to *IDN?: '{resp}'")
        return None

