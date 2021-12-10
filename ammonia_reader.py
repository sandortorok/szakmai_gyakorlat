from os import read


class Read:
    def __init__(self):
        return
    def controlPanelInit(self):
        f = open("ammonia_inputs.txt", "r")
        reading = False
        elements = []
        for line in f:
            if "ControlPanels" in line:
                reading = True
            elif 'ControlEND' in line:
                reading = False
            elif reading and "id" in line:
                elements.append(eval(line))
        f.close()
        return elements
    def tablesInit(self):
        f = open("ammonia_inputs.txt", "r")
        names = []
        sensors_left = 0
        reading = False
        for line in f:
            if "TablesSTART" in line:
                reading = True
            elif 'TablesEND' in line:
                reading = False
            elif reading and "sensors" in line:
                sensors_left = int(line.split("=")[1])
                names.append(sensors_left)
            elif reading and sensors_left > 0:
                names.append(line.strip())
                sensors_left -=1
        f.close()
        return names
        
# class Writer:
#     def __init__(self):
#         f = open("logs.txt", "a")
#         f.write("-------------------------------------------------" + "\n")
#         f.close()
#     def log(self, str):
#         f = open("logs.txt", "a")
#         f.write(str + "\n")
#         f.close()

