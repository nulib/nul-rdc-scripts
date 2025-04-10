import tkinter as tk
from tkinter import *
from tkinter import ttk


def retrieve():
    input_value = input_path.get()
    output_value = output_path.get()
    print(f"Input Path: {input_value}")
    print(f"Output Path: {output_value}")


root = Tk()
root.title("Video Quality Control")
mainframe = ttk.Frame(root, padding="10")
mainframe.pack()

bottomframe = ttk.Frame(mainframe, padding="10")
bottomframe.pack(side="bottom")

leftframe = ttk.Frame(mainframe, padding="10")
leftframe.pack(side="left")

rightframe = ttk.Frame(mainframe, padding="10")
rightframe.pack(side="right")

title = ttk.Label(mainframe, text="Video Quality Control", font=("Helvetica", 16))
title.pack(pady=10)

input_label = ttk.Label(leftframe, text="Input Path:")
input_label.pack(anchor=W)
input_path = ttk.Entry(leftframe, width=30)
input_path.insert(0, "Input Path to File or Folder")
input_path.pack(pady=5)

output_label = ttk.Label(leftframe, text="Output Path:")
output_label.pack(anchor=W)
output_path = ttk.Entry(leftframe, width=30)
output_path.insert(0, "Output Path to File or Folder")
output_path.pack(pady=5)

suggest_var = StringVar()
suggestions_yes = ttk.Radiobutton(leftframe, text="Yes", variable=suggest_var, value=1)
suggestions_no = ttk.Radiobutton(leftframe, text="No", variable=suggest_var, value=2)
suggestions_yes.pack(anchor=W, pady=5)
suggestions_no.pack(anchor=W, pady=5)

runButton = ttk.Button(bottomframe, text="Run VQC Analysis", command=retrieve)
runButton.pack(pady=10)

mainframe.mainloop()
