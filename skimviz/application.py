import tkinter as tk
from tkinter import ttk
import tkinter.filedialog
import os
import openmatrix as omx
import geopandas as gp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from shapely.geometry import Point

class SkimViz(tk.Frame):
    def __init__ (self, parent=None):
        super().__init__(parent)
        self.parent = parent
        parent.title("SkimViz")
        self.pack()
        self.create_widgets()
        self.origin_iloc = 0
        self.canvas = None
        self.geo = None
        self.skims = None

    def create_widgets(self):
        frame = ttk.Frame(self)
        frame.grid(column=1, row=0)

        self.open_skimfile_bt = tk.Button(frame)
        self.open_skimfile_bt["text"] = "Open skim file"
        self.open_skimfile_bt["command"] = self.open_skimfile
        self.open_skimfile_bt.pack(side="top")

        self.skimfile_lbl = tk.Label(frame)
        self.skimfile_lbl["text"] = "no file selected"
        self.skimfile_lbl.pack(side='top')

        self.current_skim = tk.StringVar('')
        self.skim_selector = ttk.OptionMenu(frame, self.current_skim)
        self.skim_selector.pack(side="top")
        self.current_skim.trace('w', self.redraw_map)

        self.open_geofile_bt = tk.Button(frame)
        self.open_geofile_bt["text"] = 'Open geography file'
        self.open_geofile_bt["command"] = self.open_geofile
        self.open_geofile_bt.pack(side="top")

        self.geofile_lbl = tk.Label(frame)
        self.geofile_lbl["text"] = "no file selected"
        self.geofile_lbl.pack(side="top")

        self.geo_col = tk.StringVar('')
        self.geo_col_selector = ttk.OptionMenu(frame, self.geo_col)
        self.geo_col_selector.pack(side="top")
        self.geo_col.trace('w', self.redraw_map)

        

    def open_geofile(self):
        self.geofile_path = tkinter.filedialog.askopenfilename()
        if self.geofile_path:
            self.geofile_lbl["text"] = os.path.basename(self.geofile_path)

            self.geo = gp.read_file(self.geofile_path)
            self.geo_col_selector.set_menu(self.geo.columns[0], *self.geo.columns)
            self.redraw_map()

    def open_skimfile(self):
        self.skimfile_path = tkinter.filedialog.askopenfilename()

        if self.skimfile_path:
            self.skimfile_lbl["text"] = os.path.basename(self.skimfile_path)

            self.skims = omx.open_file(self.skimfile_path, "r")
            mtxs = self.skims.list_matrices()
            self.skim_selector.set_menu(mtxs[0], *mtxs)
            self.redraw_map()

    def redraw_map(self, *args):
        if self.geo is None or self.skims is None:
            return

        if self.canvas != None:
            # https://stackoverflow.com/questions/33291297
            self.canvas.get_tk_widget().destroy()
        
        # TODO don't hardwire canvas size
        f, ax = plt.subplots(figsize=(12, 8))
        ax.set_aspect('equal', 'box')
        ax.set_axis_off()
        skim = np.array(self.skims[self.current_skim.get()])
        row = skim[self.origin_iloc, :]
        # TODO mapping support here
        mapping_col = self.geo[self.geo_col.get()].to_numpy()
        sorted_row = pd.Series(row[mapping_col], index=self.geo.index)
        self.geo.plot(column=sorted_row, legend=True, ax=ax)

        self.geo.loc[self.geo[self.geo_col.get()] == self.origin_iloc].plot(color='red', ax=ax)

        self.canvas = FigureCanvasTkAgg(f, self)
        self.canvas.mpl_connect('button_press_event', self.click)
        self.canvas.get_tk_widget().grid(column=0, row=0)

    def click(self, e):
        pt = Point(e.xdata, e.ydata)
        print(f'{pt.coords[:]=}')

        matches = self.geo.sindex.query(pt, predicate='within')

        if len(matches) > 0:
            self.origin_iloc = self.geo.iloc[matches[0]][self.geo_col.get()]
            self.redraw_map()
        else:
            print('No matches!')


