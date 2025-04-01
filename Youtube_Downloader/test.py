import tkinter as tk
from tkinter import ttk
from tkinter.ttk import Style

root = tk.Tk()

entry_style = Style()

entry_style.configure('style.TEntry', 

            fieldbackground="black", 

            foreground="white"           

           )

e = ttk.Entry(root, width=80, style='style.TEntry', font='sans 15 bold')

e.focus_force()

e.grid(row=0, column=0, columnspan=4, padx=0, pady=0, sticky="nsew")

root.mainloop()