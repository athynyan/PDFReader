import os
from subprocess import Popen
import tkinter
from tkinter import Frame, Listbox, filedialog
from tkinter.constants import END
import json


config = {
    'file_reader': '',
    'initial_dir': '/',
    'resolution': {
        'width': 800,
        'height': 900
    }
}
filepaths: dict[str, str] | None = None


def load_files(address: str, filter: list[str] | None = None) -> dict[str, str]:
    filepaths: dict[str, str] = {}
    
    for path, subdirs, files in os.walk(address):
        for file in files:
            if (filter is not None and file.split('.')[-1] in filter) or (filter is None):
                filepaths[file] = os.path.join(path, file)

    return dict(sorted(filepaths.items(), key=lambda item: item[0].lower()))


def open_folder():
    global filepaths
    global config

    folder_name = filedialog.askdirectory(initialdir=config['initial_dir'], title="Select Folder")
    filepaths = load_files(folder_name.replace('/', '\\'), ['zip', 'cbz'])

    lb.delete(0, END)

    for x in range(len(filepaths)):
        lb.insert(x, list(filepaths.keys())[x].split('\\')[-1])

    if folder_name != '':
        config['initial_dir'] = folder_name


def reload_folder():
    global filepaths

    filepaths = load_files(config['initial_dir'].replace('/', '\\'), ['pdf', 'epub', 'zip', 'cbz'])

    lb.delete(0, END)

    for x in range(len(filepaths)):
        lb.insert(x, list(filepaths.keys())[x].split('\\')[-1])
    
    print('reloaded')


def pick_reader():
    global config

    file_name = filedialog.askopenfilename(
        initialdir=config['initial_dir'],
        title="Select File",
        filetypes=(('executables', '*.exe'), ('all files', '*'))
    )
    
    last_dir = '/'.join(file_name.split('/')[:-1])
    if file_name != '':
        config['file_reader'] = file_name
        config['initial_dir'] = last_dir
        label.config(text = f'Current reader: {file_name}')


def open_file(event):
    filename = lb.get(lb.curselection())
    if filepaths:
        try:
            Popen([config['file_reader'], filepaths[filename]])
        except tkinter.TclError:
            print('No index')


def delete_file(event):
    try:
        filepath = lb.get(lb.curselection())
        os.remove(filepath)
        reload_folder()
    except FileNotFoundError:
        print('File doesn\'t exist')

def save_resolution(event):
    global config
    size = canvas.winfo_geometry().split('+')[0].split('x')

    config['resolution'] = {
        'width': size[0],
        'height': size[1]
    }
    


if __name__ == '__main__':
    try:
        with open('config.json', 'r+') as file:
            config = json.load(file)
    except FileNotFoundError: 
        print('No file found.')

    root = tkinter.Tk()
    root.title('Reader File Browser')

    label = tkinter.Label(root, text=f'Current reader: {config["file_reader"]}')
    label.pack()

    open_folder_button = tkinter.Button(root, text='Open Folder', fg='black', relief='flat', command=open_folder)
    open_folder_button.pack(side='left', anchor='nw')

    reload_button = tkinter.Button(root, text='Reload', fg='black', relief='flat', command=reload_folder)
    reload_button.pack(side='left', anchor='nw')

    reader_pick_button = tkinter.Button(root, text='Pick a Reader', relief='flat', command=pick_reader)
    reader_pick_button.pack(side='right', anchor='ne')

    canvas = tkinter.Canvas(root, height=config['resolution']['height'], width=config['resolution']['width'])
    canvas.pack()
    canvas.bind('<Configure>', save_resolution)

    lb = Listbox(root)
    lb.place(relwidth=0.8, relheight=0.9, relx=0.1, rely=0.05)
    lb.bind('<Double-Button-1>', open_file)
    lb.bind('<KeyPress-KP_Delete>', delete_file)

    root.mainloop()

    with open('config.json', 'w+') as file:
        json.dump(config, file)