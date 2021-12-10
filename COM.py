import serial
import serial.tools.list_ports
import threading
class StorePacket:
    def __init__(self, n = -1, v = -1, c = -1):
        self.number = n
        self.value = v
        self.horn = True
        self.can = c

class ComPacket:
    def __init__(self, max):
        self.lock = threading.Lock()
        self.maxsensors = max
        self.currentsensor = 0
    def query(self):

        self.currentsensor += 1
        if self.currentsensor > self.maxsensors:
            self.currentsensor = 1
        hexnumber = format(self.currentsensor, 'x')
        if len(hexnumber) == 1:
            strsensor = "000" + hexnumber
        else:
            strsensor = "00" + hexnumber

        try:
            # print('try1')
            self.ser = serial.Serial('/dev/ttyUSB0', 38400, timeout = 10)
            # print('try2')
            self.ser.write(b'get' + bytearray.fromhex(strsensor) + b'#')
            # print('try3')
            x = self.ser.read(size = 7)
            # print('try4')
            str = x.hex()
            number = int(str[0:2], base  = 16) + 256 * int(str[2:4], base  = 16)
            value = int(str[4:6], base  = 16) + 256 * int(str[6:8], base  = 16)
            can = int(str[10:12], base  = 16)
            self.ser.close()
            return StorePacket(number, value, can)
        except Exception as e:
            # print(e)
            return StorePacket(self.currentsensor, 0, 0)

