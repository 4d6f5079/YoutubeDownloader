import tkinter as tk

class ToplevelManager():

    def __init__(self, label_text=None):
        self.label_text = label_text

    def __enter__(self):
        self.newWindow = tk.Toplevel()
        self.newWindow.title("Downloading...")
        self.newWindow.geometry("275x125")

        if self.label_text:
            label = tk.Label(
                master=self.newWindow,
                text=self.label_text,
                wraplength=self.newWindow.winfo_width()
            )
            label.pack(padx=0,pady=0)

    def __exit__(self, exc_type, exc_val, traceback):
        self.newWindow.destroy()