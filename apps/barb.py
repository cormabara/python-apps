""" This is a simple executable to generate the prg files for TC8 """
import os
import tkinter as tk
from enum import IntEnum
from tkinter import *
from tkinter import simpledialog
from tkinter.filedialog import askopenfilename
from tkinter import filedialog
import numpy as np

max_num_tex = 16
num_tex = 16


class ECols(IntEnum):
    col_design = 0
    col_meters = 1
    col_startpick = 2
    cols = 3


cols_titles = ["design", "meters", "start"]


class TexHeader(tk.Frame):

    def __init__(self, parent_, *args, **kwargs):
        tk.Frame.__init__(self, parent_, *args, **kwargs,height=5)
        self.pack()
        self.hdr1 = tk.Label(self, height=1, text="WEAVING_PROGRAM V1.2")
        self.hdr1.pack(side="top")
        self.hdr2 = Frame(self)
        self.hdr2.pack(side="top")
        self.hdr2a = tk.Label(self.hdr2, height=1,  text="DENSITY ")
        self.hdr2a.pack(side="left")
        self.hdr2b = tk.Text(self.hdr2, height=1, width=10)
        self.hdr2b.insert(INSERT, "10.0")
        self.hdr2b.pack(side="left")
        self.hdr2c = tk.Label(self.hdr2, height=1, text=" PICKS_INCH")
        self.hdr2c.pack(side="left")

        self.hdr3 = tk.Label(self, height=1, text="NUMBER_OF_EXECUTIONS 0")
        self.hdr3.pack(side="top")

    def generate(self,ff_):
        ff_.write(self.hdr1.cget("text") + "\n")
        ff_.write(self.hdr2a.cget("text") + self.hdr2b.get(1.0, "end-1c" ) + self.hdr2c.cget("text") + "\n")
        ff_.write(self.hdr3.cget("text") + "\n")


class TexTable(tk.Frame):

    class TexRow:

        def __init__(self,parent_,row_, *args, **kwargs):
            tk.Frame(parent_,*args, **kwargs)
            self.row = row_
            self.design = ""
            self.meters = 0
            self.first_pick = 1

            self.btn_design = tk.Button(parent_, height=1, text=self.design, command=self.choose_tex)
            self.btn_meters = tk.Button(parent_, text=self.meters, height=1, command=self.choose_meters)
            self.btn_first_pick = tk.Button(parent_, text=self.first_pick, height=1, command=self.choose_first_pick)

            self.btn_design.grid(row=row_, column=ECols.col_design.value, sticky="nsew", padx=1, pady=1)
            self.btn_meters.grid(row=row_, column=ECols.col_meters.value, sticky="nsew", padx=1, pady=1)
            self.btn_first_pick.grid(row=row_, column=ECols.col_startpick.value, sticky="nsew", padx=1, pady=1)

        def get_row(self):
            return [self.btn_design, self.btn_meters, self.btn_first_pick]

        def choose_tex(self):
            filename = askopenfilename()
            self.design = os.path.basename(filename)
            self.btn_design.config(text=self.design)

        def choose_meters(self):
            self.meters = simpledialog.askinteger("Input", "Meters?",
                                                  parent=app, minvalue=0, maxvalue=2000)
            self.btn_meters.config(text=self.meters)

        def choose_first_pick(self):
            self.first_pick = simpledialog.askinteger("Input", "first_pick?",
                                                      parent=app, minvalue=0, maxvalue=2000)
            self.btn_first_pick.config(text=self.first_pick)

        def pack(self):
            self.btn_design.grid(row=self.row, column=ECols.col_design.value, sticky="nsew", padx=1, pady=1)
            self.btn_meters.grid(row=self.row, column=ECols.col_meters.value, sticky="nsew", padx=1, pady=1)
            self.btn_first_pick.grid(row=self.row, column=ECols.col_startpick.value, sticky="nsew", padx=1, pady=1)
            pass

        def pack_forget(self):
            self.btn_design.grid_forget()
            self.btn_meters.grid_forget()
            self.btn_first_pick.grid_forget()
            pass

        def generate(self, file_):
            file_.write("\tBEGIN\n")
            file_.write('\t\tDESIGN \"' + self.design + "\"\n")
            file_.write('\t\tNUMBER_OF_METERS \"' + str(self.meters) + "\"\n")
            file_.write('\t\tFIRST_PICK \"' + str(self.first_pick) + "\"\n")
            file_.write("\tEND\n")

    def __init__(self, parent, rowsnum_):
        # use black background so it "peeks through" to
        # form grid lines
        tk.Frame.__init__(self, parent, background="black")
        self.rows = []
        self._widgets = []
        for column in range(ECols.cols):
            label = tk.Label(self, text=cols_titles[column],borderwidth=0, width=10)
            label.grid(row=0, column=column, sticky="nsew", padx=1, pady=1)
            self._widgets.append(label)

        for row in range(rowsnum_):
            self.rows.append(self.TexRow(self,row))
            self._widgets.append(self.rows[row].get_row())

        for column in range(ECols.cols):
            self.grid_columnconfigure(column, weight=1)

    def set(self, row, column, value):
        widget = self._widgets[row][column]
        widget.configure(text=value)

    def refresh(self,num_tex_):
        for ii in range(max_num_tex):
            if ii >= num_tex:
                self.rows[ii].pack_forget()  # to hide
            else:
                self.rows[ii].pack()

    def generate(self, ff_, numtex_):
        ff_.write("BEGIN\n")
        for ind in range(numtex_):
            self.rows[ind].generate(ff_)
        ff_.write("END\n")


def change_num_tex():
    global num_tex
    num_tex = simpledialog.askinteger("Input", "Insert number of design",
                                      parent=app,
                                      minvalue=0, maxvalue=max_num_tex)
    refresh()


def generate_file():
    file_path = filedialog.asksaveasfilename()
    ff = open(file_path, "w")
    header.generate(ff)
    tex_table.generate(ff, num_tex)
    ff.close()


app = tk.Tk()
app.title("Prg file generation")
app.geometry("600x700")

tex_toolbar = Frame(app,bg="gray",height=40)
tex_toolbar.pack(side=TOP, fill=X)
tk.Button(tex_toolbar, text="Number of tex files", command=change_num_tex).pack(side="left")
tk.Button(tex_toolbar, text="Generate", command=generate_file).pack(side="left")

header = TexHeader(app)
tex_table = TexTable(app, max_num_tex)
tex_table.pack(side="top", fill="x")



def refresh():
    tex_table.refresh(num_tex)

refresh()
app.mainloop()

