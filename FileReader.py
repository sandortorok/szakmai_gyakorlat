
class Read:
    def __init__(self):
        f = open("input.txt", "r")
        self.sensors = 0
        for line in f:
            if "sensors" in line:
                lines =line.split("=")
                self.sensors = int(lines[1])
class Writer:
    def __init__(self):
        f = open("logs.txt", "a")
        f.write("-------------------------------------------------" + "\n")
        f.close()
    def log(self, str):
        f = open("logs.txt", "a")
        f.write(str + "\n")
        f.close()
        
                

