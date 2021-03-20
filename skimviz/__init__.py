from tkinter import Tk
from .application import SkimViz

def start():
    tk = Tk()
    app = SkimViz(tk)
    app.mainloop()