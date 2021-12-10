import serial

ser = serial.Serial('/dev/ttyUSB0', 38400, timeout = 1)
i = 0
while i < 1:
    ser.write(b'get' + bytearray.fromhex('0001') + b'#')
    x = ser.read(size = 7)
    str = x.hex()
    print("szoveg: " + str)
    print((str[0:2])+ ' ' + str[2:4] + ' ' + str[4:6] + ' ' + str[6:8] + ' ' + str[8:10] + ' ' + str[10:12] + ' ' + str[12:14])
    print('1.: ' + bin(int(str[0:2], base=16)))
    print('2.: ' + bin(int(str[2:4], base=16)))
    print('3.: ' + bin(int(str[4:6], base=16)))
    print('4.: ' + bin(int(str[6:8], base=16)))
    print('5.: ' + bin(int(str[8:10], base=16)))
    print('6.: ' + bin(int(str[10:12], base=16)))
    print('7.: ' + bin(int(str[12:14], base=16)))
    i+=1
    print("SensorNumber: ")
    print(int(str[0:2], base  = 16) + 256 * int(str[2:4], base  = 16))

    print("AmmoniaValue: ")
    print(int(str[4:6], base  = 16) + 256 * int(str[6:8], base  = 16))

    print("Canvalue: ")
    print(int(str[10:12], base  = 16))
