import tkinter as tk

def on_entry_change(*args):
    print("Entry changed:", var.get())  # Event triggered

root = tk.Tk()
var = tk.StringVar()
var.trace_add("write", on_entry_change)  # Call function on change

entry = tk.Entry(root, textvariable=var)
entry.pack()

root.mainloop()