import tkinter as tk

root = tk.Tk()

class MyFigure(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self,master)
        self.master = master
        self.bc = tk.Button(self, text='confi',
                            command=lambda:self.configure(bg='red')
                            )
        self.bmanage = tk.Button(self, text='manage',
                                 command = lambda:self._manage()
                                 )
        self.bforget = tk.Button(self, text='forget',
                                 command = lambda:self._forget()
                                 )

        self.bmanage.pack(side='left')
        self.bc.pack(side='left')
        self.bforget.pack(side='left')
        self.frame = tk.Frame(self.master, bg="red", height=100)
        self.label=tk.Label(self.frame, text="hi")
        self.frame.pack()
        self.label.pack(expand=True, fill=tk.BOTH)

    def _manage(self):
        test=self.master.wm_manage(self.frame)

    def _forget(self):
        self.master.wm_forget(self.frame)
        self.frame.pack()

mf = MyFigure(root)
mf.pack()
root.mainloop() 

