import pikepdf
import tkinter as tk
import tkinter.filedialog as tkfd
import tkinter.ttk as ttk
from tkinter import messagebox

import os
import datetime
import getpass


APP_NAME = 'PDF Concatenator 2000 Pro'
DEFAULT_OUTPUT_NAME = 'document.pdf'
DEFAULT_OUTPUT_DIR = 'Documents'

DIRECTION_UP = 1
DIRECTION_DOWN = -1


def update_list():
    var_files.set(files)


def move_item(direction: int):
    selection = file_box.curselection()
    selection_length = len(selection)

    if selection_length > 0:
        current_index = selection[0]
        
        if direction == DIRECTION_UP:
            in_limits = current_index > 0
        else:
            in_limits = current_index < selection_length-1
        
        if in_limits:
            new_index = current_index - direction
            files[current_index], files[new_index] = files[new_index], files[current_index]
            file_box.selection_clear(current_index)
            file_box.selection_set(new_index)
            file_box.activate(new_index)
            update_list()


def delete_item():
    selection = file_box.curselection()
    if len(selection) > 0:
        files.pop(selection[0])
        update_list()


def open_file_dialog():
    file_names = tkfd.askopenfilenames(defaultextension='.pdf', filetypes=[('PDF', '*.pdf'),])
    for fn in file_names:
        files.append(fn)
        update_list()


def select_output():
    new_file_name = tkfd.asksaveasfilename(defaultextension='.pdf', filetypes=[('PDF', '*.pdf'),])
    var_file_name.set(new_file_name)


def concatenate_documents():
    try:
        pdf = pikepdf.Pdf.new()
        current_date = datetime.date.today().strftime("D:%Y%m%d%H%M%S")
        current_user = getpass.getuser().title()
        
        pdf.docinfo['/Creator'] = APP_NAME
        pdf.docinfo['/Title'] = 'Concatenated Document'
        pdf.docinfo['/CreationDate'] = current_date
        pdf.docinfo['/ModDate'] = current_date
        pdf.docinfo['/Author'] = current_user

        for file in files:
            src = pikepdf.Pdf.open(file)
            pdf.pages.extend(src.pages)
            src.close()

        pdf.save(var_file_name.get())
        pdf.close()

        messagebox.showinfo(message='File created successfully!')
        
    except Exception as e:
        print(e)
        messagebox.showerror(message='Oh no, something went wrong :(')


home_directory = os.path.expanduser('~')

files = []

if os.path.exists(os.path.join(home_directory, DEFAULT_OUTPUT_DIR)):
    destination_directory = DEFAULT_OUTPUT_DIR
else:
    destination_directory = ''

root = tk.Tk()
root.title(APP_NAME)
root.minsize(400, 400)
icon = tk.PhotoImage(file='icon.png')
root.iconphoto(True, icon)


var_files = tk.StringVar(value=files)
var_file_name = tk.StringVar(value=os.path.join(home_directory, destination_directory, DEFAULT_OUTPUT_NAME))

frm_files = tk.LabelFrame(master=root, relief=tk.GROOVE, text='File list')
file_box = tk.Listbox(master=frm_files, listvariable=var_files, selectmode=tk.SINGLE)
var_files.set(files)
file_box.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
file_buttons = tk.Frame(master=frm_files)
btn_add = tk.Button(master=file_buttons, text='+', width=1, height=1, fg='green', activeforeground='green', command=open_file_dialog)
btn_rem = tk.Button(master=file_buttons, text='-', width=1, height=1, fg='red', activeforeground='red', command=delete_item)
btn_up = tk.Button(master=file_buttons, text='∆', width=1, height=1, command=lambda: move_item(DIRECTION_UP)) #state=tk.DISABLED
btn_dn = tk.Button(master=file_buttons, text='∇', width=1, height=1, command=lambda: move_item(DIRECTION_DOWN))
btn_add.pack(side=tk.LEFT, anchor=tk.NW)
btn_rem.pack(side=tk.LEFT, anchor=tk.NW)
btn_up.pack(side=tk.LEFT, anchor=tk.NW)
btn_dn.pack(side=tk.LEFT, anchor=tk.NW)
file_buttons.pack(pady=(0,5))

frm_output = tk.LabelFrame(master=root, relief=tk.GROOVE, text='Output path')
output_name = tk.Entry(master=frm_output, font=('Arial', 14), textvariable=var_file_name)
output_select = tk.Button(master=frm_output, text='...', height=1, command=select_output)
output_name.pack(padx=5, pady=5, side=tk.LEFT, fill=tk.X, expand=True)
output_select.pack(padx=(0,5), pady=5, side=tk.LEFT)

frm_files.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

btn_glue = tk.Button(master=root, text='Combine my PDFs!', bg='cyan', activebackground='lightcyan', command=concatenate_documents, padx=5, pady=5, font=('Arial', 14))
btn_glue.pack(padx=10, pady=10, side=tk.BOTTOM, fill=tk.X)

frm_output.pack(padx=10, pady=10, side=tk.BOTTOM, fill=tk.BOTH)

root.mainloop()
