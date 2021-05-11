import tkinter as tk

class ToplevelManager():

    def __init__(self, label_text=None):
        self.label_text = label_text

    def __enter__(self):
        self.newWindow = tk.Toplevel()
        self.newWindow.title("Downloading...")
        self.newWindow.geometry("300x175")

        if self.label_text:
            label = tk.Label(
                master=self.newWindow,
                text=self.label_text
            )
            label.pack(padx=2,pady=2)

    def __exit__(self, exc_type, exc_val, traceback):
        self.newWindow.destroy()