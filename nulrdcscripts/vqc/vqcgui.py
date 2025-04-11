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

# Creates input entry box 
input_label = ttk.Label(leftframe, text="Input Path:")
input_label.pack(anchor=W)
input_path = ttk.Entry(leftframe, width=30)
input_path.insert(0, "Input Path to File or Folder")
input_path.pack(pady=5)

# Creates output entry box
output_label = ttk.Label(leftframe, text="Output Path:")
output_label.pack(anchor=W)
output_path = ttk.Entry(leftframe, width=30)
output_path.insert(0, "Output Path to File or Folder")
output_path.pack(pady=5)


# Creates that suggestions radiobuttons --> Yes, No STR
suggest_frame = ttk.Frame(leftframe, padding=10)
suggest_label = ttk.Label(leftframe, text = 'Suggestions? : ')
suggest_label.pack(anchor=W)

suggest_var = StringVar()
suggestions = ttk.Label(leftframe, text='Suggestions? :')
suggestions_yes = ttk.Radiobutton(leftframe, text="Yes", variable=suggest_var, value='yes')
suggestions_no = ttk.Radiobutton(leftframe, text="No", variable=suggest_var, value='no')
suggestions_yes.pack(anchor=W, padx=10)
suggestions_no.pack(anchor=W,padx=10)

# Creates the bit depth radiobuttons --> 10, 8, Unknown INT -- Unknown comes back as 999
bit_frame = ttk.Frame(leftframe,padding=10)
bit_label = ttk.Label(leftframe, text='Bit Depth:')
bit_label.pack(anchor=W)
bitdepth_var = IntVar()
bitdepth_10 = ttk.Radiobutton(leftframe, text='8 Bit', variable=bitdepth_var,value=10)
bitdepth_8 = ttk.Radiobutton(leftframe, text = '10 Bit', variable = bitdepth_var,value=8)
bitdepth_ukn = ttk.Radiobutton(leftframe, text= 'Evaluate',variable = bitdepth_var,value=999)
bitdepth_10.pack(anchor=W,padx=10)
bitdepth_8.pack(anchor=W,padx=10)
bitdepth_ukn.pack(anchor=W,padx=10)

# Select verbosity level
verb_var_begin=BooleanVar()
verb_var_expert=BooleanVar()
verbosity_frame = ttk.Frame(rightframe, padding=10)
verbosity_label = ttk.Label(rightframe, text='Verbosity Level:')
verbosity_label.pack(anchor=W)
verbosity_beginner = ttk.Checkbutton(rightframe, text='Beginner', variable=verb_var_begin)
verbosity_expert = ttk.Checkbutton(rightframe, text='Expert', variable=verb_var_expert)
verbosity_beginner.pack(anchor=W, padx=10)
verbosity_expert.pack(anchor=W, padx=10)

# Video Type

video_type_frame = ttk.Frame(rightframe, padding=10)
video_type_label = ttk.Label(rightframe, text='Video Type:')
video_type_label.pack(anchor=W)
video_type_var = StringVar()
video_type_color = ttk.Radiobutton(rightframe, text='Color', variable=video_type_var, value='color')
video_type_bw= ttk.Radiobutton(rightframe, text='Black & White', variable=video_type_var, value='bw')
video_type_bw.pack(anchor=W, padx=10)
video_type_color.pack(anchor=W, padx=10)


# Execute button --> retrieves the data and uses it to run VQC
runButton = ttk.Button(bottomframe, text="Run VQC Analysis", command=retrieve)
runButton.pack(pady=10)

mainframe.mainloop()
