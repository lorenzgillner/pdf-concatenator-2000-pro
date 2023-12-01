import pikepdf
import tkinter as tk
import tkinter.filedialog as tkfd
import tkinter.ttk as ttk
from tkinter import messagebox, dnd

import os
import datetime
import getpass


APP_NAME = "PDF Concatenator 2000 Pro"
DEFAULT_OUTPUT_NAME = "document.pdf"
DEFAULT_OUTPUT_DIR = "Documents"

DIRECTION_UP = 1
DIRECTION_DOWN = -1

PADDING = 10


def set_action_buttons(event=None):
    selection = file_box.curselection()
    length = len(files)

    if length > 0 and selection:
        btn_rm.config(state=tk.NORMAL)
    else:
        btn_rm.config(state=tk.DISABLED)

    if selection:
        if selection[0] > 0:
            btn_up.config(state=tk.NORMAL)
        else:
            btn_up.config(state=tk.DISABLED)

        # length > 1 and selection and 
        if selection[0] < length-1:
            btn_dn.config(state=tk.NORMAL)
        else:
            btn_dn.config(state=tk.DISABLED)


def update_list():
    var_file_list.set(files)


def move_item(direction: int):
    selection = file_box.curselection()
    selection_length = len(selection)

    if selection_length > 0:
        current_index = selection[0]

        if direction == DIRECTION_UP:
            in_limits = current_index > 0
        else:
            in_limits = current_index < len(files) - 1

        if in_limits:
            new_index = current_index - direction
            files[current_index], files[new_index] = (
                files[new_index],
                files[current_index],
            )
            file_box.selection_clear(current_index)
            file_box.selection_set(new_index)
            file_box.activate(new_index)
            update_list()
            set_action_buttons()


def delete_item():
    selection = file_box.curselection()
    if len(selection) > 0:
        files.pop(selection[0])
        update_list()
        set_action_buttons()


def add_item():
    selection = file_box.curselection()
    current_index = selection[0] if selection else 0

    file_names = tkfd.askopenfilenames(
        defaultextension=".pdf",
        filetypes=[
            ("PDF", "*.pdf"),
        ],
    )
    for fn in file_names:
        files.insert(current_index+1, fn)
        update_list()
        set_action_buttons()


def select_output():
    new_file_name = tkfd.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[
            ("PDF", "*.pdf"),
        ],
    )
    var_file_name.set(new_file_name)


def concatenate_documents():
    try:
        pdf = pikepdf.Pdf.new()
        current_date = datetime.date.today().strftime("D:%Y%m%d%H%M%S")
        current_user = getpass.getuser().title()

        pdf.docinfo["/Creator"] = APP_NAME
        pdf.docinfo["/Title"] = "Concatenated Document"
        pdf.docinfo["/CreationDate"] = current_date
        pdf.docinfo["/ModDate"] = current_date
        pdf.docinfo["/Author"] = current_user

        for file in files:
            src = pikepdf.Pdf.open(file)
            pdf.pages.extend(src.pages)
            src.close()

        pdf.save(var_file_name.get())
        pdf.close()

        messagebox.showinfo(message="File created successfully!")

    except Exception as e:
        print(e)
        messagebox.showerror(message="Oh no, something went wrong :(")


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# files will be stored here
files = []

# get user's home directory path
home_directory = os.path.expanduser("~")

# set default output directory path
if os.path.exists(os.path.join(home_directory, DEFAULT_OUTPUT_DIR)):
    destination_directory = DEFAULT_OUTPUT_DIR
else:
    destination_directory = ""

# set up main window
root = tk.Tk()
root.title(APP_NAME)
root.minsize(400, 400)
icon = tk.PhotoImage(file="icon.png")
root.iconphoto(True, icon)

# create interactive variables
var_file_list = tk.StringVar(value=files)
var_file_name = tk.StringVar(
    value=os.path.join(home_directory, destination_directory, DEFAULT_OUTPUT_NAME)
)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# create file list with action buttons
frm_files = tk.LabelFrame(master=root, relief=tk.GROOVE, text="File list")
file_box = tk.Listbox(
    master=frm_files, listvariable=var_file_list, selectmode=tk.SINGLE
)
file_box.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
file_box.bind("<FocusIn>", set_action_buttons)
file_box.bind("<FocusOut>", set_action_buttons)
file_box.bind("<<ListboxSelect>>", set_action_buttons)

# create new frame for action buttons
frm_action = tk.Frame(master=frm_files)

# button for adding files
btn_ad = tk.Button(
    master=frm_action,
    text="+",
    width=1,
    height=1,
    fg="green",
    activeforeground="green",
    command=add_item,
)

# button for removing the currently selected file
btn_rm = tk.Button(
    master=frm_action,
    text="-",
    width=1,
    height=1,
    fg="red",
    activeforeground="red",
    command=delete_item,
    state=tk.DISABLED,
)

# button for moving the currently selected file up
btn_up = tk.Button(
    master=frm_action,
    text="▲",
    width=1,
    height=1,
    command=lambda: move_item(DIRECTION_UP),
    state=tk.DISABLED,
)

# button for moving the currently selected file down
btn_dn = tk.Button(
    master=frm_action,
    text="▼",
    width=1,
    height=1,
    command=lambda: move_item(DIRECTION_DOWN),
    state=tk.DISABLED,
)

# pack action buttons
btn_ad.pack(side=tk.LEFT, anchor=tk.N)
btn_rm.pack(side=tk.LEFT, anchor=tk.N)
btn_up.pack(side=tk.LEFT, anchor=tk.N)
btn_dn.pack(side=tk.LEFT, anchor=tk.N)

# pack action buttons frame
frm_action.pack(pady=(0, 5))

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# create frame for specifying the output file path
frm_output = tk.LabelFrame(master=root, relief=tk.GROOVE, text="Output path")
output_name = tk.Entry(
    master=frm_output, font=("Arial", 14), textvariable=var_file_name
)
output_select = tk.Button(
    master=frm_output, text="…", height=1, command=select_output
)
output_name.pack(padx=5, pady=5, side=tk.LEFT, fill=tk.X, expand=True)
output_select.pack(padx=(0, 5), pady=5, side=tk.LEFT)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# create frame for button to start file concatenation
frm_concat = tk.Frame(master=root)
btn_concat = tk.Button(
    master=frm_concat,
    text="Combine my PDFs!",
    bg="cyan",
    activebackground="lightcyan",
    command=concatenate_documents,
    padx=PADDING,
    pady=PADDING,
    font=("Arial", 14),
)
btn_concat.pack(fill=tk.BOTH)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# align widget frames
frm_files.pack(padx=PADDING, pady=PADDING, side=tk.TOP, fill=tk.BOTH, expand=True)
frm_output.pack(padx=PADDING, pady=PADDING, side=tk.TOP, fill=tk.BOTH)
frm_concat.pack(padx=PADDING, pady=PADDING, side=tk.TOP, fill=tk.X, expand=True)

# XXX is this even necessary?
var_file_list.set(files)

# start the event loop
root.mainloop()
