import tkinter as tk

def on_entry_change(*args):
    target.set("Hello World")  # Set only the second entry's value
    print("Entry changed:", entry.get())  # Print the value of the first entry

root = tk.Tk()
var = tk.StringVar()
var.trace_add("write", on_entry_change)  # Call function on change

entry = tk.Entry(root, textvariable=var)
entry.pack()

target = tk.StringVar()  # Create a separate StringVar for the second entry
target_entry = tk.Entry(root, textvariable=target)
target_entry.pack()

root.mainloop()