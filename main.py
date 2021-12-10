from tkinter import *
from tkinter import ttk
import Sens1
from datetime import datetime
import COM
import FileReader as R



class Application (object):
    def tab1load(self):
        for j in range(4):
            for i in range(25):
                if((j*25 + i +1)<= self.sensors):
                    label = Label(self.tab1, text='Szenzor ' + str(j*25 + i) + ' [ppm] :', font='arial 12 bold', fg='black')
                    label.grid(row = i, column = 3*j, pady = 1, padx = 4)
                    self.labels.append(label)

                    entry = Entry(self.tab1, font='arial 9 bold', width=7, bd=3, justify=RIGHT)
                    entry.grid(row = i, column = 3*j+ 1, pady = 1, padx = 4)
                    self.entries.append(entry)

                    button = Button(self.tab1, width=80, height=15, text=' Info ', font='arial 8 bold', bd=3, 
                       fg='black', image=self.btnIcon, compound=LEFT,  command=lambda x=(j*25 + i): self.chooseSensorNumber(x))
                    button.grid(row = i, column = 3*j+2, pady = 1, padx=(5, 50))
                    self.buttons.append(button)

        statusBar = Label(self.status, text='Aktualis lekerdezett cim: ',
                        font='arial 12 bold', fg='black')
        statusBar.place(x=20, y=8)
    def tab2load(self):
        for j in range(4):
            for i in range(25):
                if((j*25 + i +1 +100)<= self.sensors):
                    label = Label(self.tab2, text='Szenzor ' + str(j*25 + i+100) + ' [ppm] :', font='arial 12 bold', fg='black')
                    label.grid(row = i, column = 3*j, pady = 1, padx = 4)
                    self.labels.append(label)

                    entry = Entry(self.tab2, font='arial 9 bold', width=7, bd=3, justify=RIGHT)
                    entry.grid(row = i, column = 3*j+ 1, pady = 1, padx = 4)
                    self.entries.append(entry)

                    button = Button(self.tab2, width=80, height=15, text=' Info ', font='arial 8 bold', bd=3, 
                       fg='black', image=self.btnIcon, compound=LEFT,  command=lambda x=(j*25 + i+100): self.chooseSensorNumber(x))
                    button.grid(row = i, column = 3*j+2, pady = 1, padx=(5, 50))
                    self.buttons.append(button)

    def __init__(self, master, sen):
        self.logger = R.Writer()
        self.logger.log("alkalmazas elinditva ekkor: ")
        date = datetime.now().date()
        exact_time = datetime.now().strftime(" %H:%M:%S")
        self.logger.log(str(date) + str(exact_time))
        self.master = master
        self.sensors = sen
        # Frames
        self.top = Frame(master, height=30, bg='white')
        self.top.pack(fill=X)
        self.bottom = Frame(master, height=700, bg='#adff2f')
        self.bottom.pack(fill=X)
        self.status = Frame(master, height=30, bd=2)
        self.status.pack(fill=X)

        # Top labels
        self.date_lbl = Label(self.top, text="Mai datum: " + str(date), font='arial 12 bold',bg='white', fg='#ffa500')
        self.date_lbl.place(x=1200, y=10)

        # Tab control

        self.tabs = ttk.Notebook(self.bottom, width=1500, height=680)
        self.tabs.pack()
        self.tab1_icon = PhotoImage(file='icons/home.png')
        self.tab2_icon = PhotoImage(file='icons/advancedsettings.png')
        self.tab3_icon = PhotoImage(file='icons/clipboard_01.png')
        self.tab1 = ttk.Frame(self.tabs)
        self.tab2 = ttk.Frame(self.tabs)
        self.tab3 = ttk.Frame(self.tabs)
        self.tab4 = ttk.Frame(self.tabs)
        self.tabs.add(self.tab1, text='Szenzor attekinto', image=self.tab1_icon, compound=LEFT)
        self.tabs.add(self.tab2, text='Szenzor attekinto2', image=self.tab1_icon, compound=LEFT)
        self.tabs.add(self.tab3, text='Beallitas', image=self.tab2_icon, compound=LEFT)
        self.tabs.add(self.tab4, text='Szerviz - Log', image=self.tab3_icon, compound=LEFT)

        # Bottom labels, Entries, Buttons

        self.labels = []
        self.entries = []
        self.buttons = []

        self.btnIcon = PhotoImage(file='icons/button_info_01.png')
        self.tab1load()
        self.tab2load()

    def chooseSensorNumber(self, x):
        Sens1.Sensor1(x)
        self.logger.log("rakattintottak a " + str(x) +". szenzor info-jara")
    def update(self):
        p = COM.ComPacket()
        s = p.query()
        if (s.number <= self.sensors):
            self.entries[s.number-1].delete(0, END)
            self.entries[s.number-1].insert(0, str(s.value))
            if (s.number < 30):
                self.entries[s.number-1].config(bg='#7fff00') #light green color
            elif(s.number < 70):
                self.entries[s.number-1].config(bg='yellow')
            elif(s.number <= 200):
                self.entries[s.number-1].config(bg='red')

        self.master.after(100, self.update)



def main():

    Reader = R.Read()
    root = Tk()
    app = Application(root, Reader.sensors)
    root.title("Ammonia szivargas monitor")
    root.geometry("1500x850")
    root.resizable(False, False)
    app.update()
    root.mainloop()


if __name__ == '__main__':
    main()
