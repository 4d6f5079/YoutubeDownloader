import tkinter as tk

class VideoQualitySelector(tk.Toplevel):

    def __init__(self, parent, available_formats, vid_name):
        super().__init__(parent)

        self.available_formats = available_formats
        self.vid_title = vid_name
        self.selection = ''

        self.title("Select video quality")
        self.geometry("450x500")

        self.label = tk.Label(
                master=self,
                text=f"Select video quality for \"{self.vid_title}\""
        )
        self.label.pack(pady=7)

        self.listbox = tk.Listbox(self, height=20, width=40)
        self.listbox.pack(pady=15)

        self.btn = tk.Button(self, text="Confirm selection video quality", command=self.select)
        self.btn.pack(pady=7)

        for (_, f_info) in self.available_formats:
            self.listbox.insert(tk.END, f_info) 

    def select(self):
        selection = self.listbox.curselection()
        if selection:
            self.selection = self.available_formats[selection[0]][0]
            self.destroy()

    def show(self):
        self.deiconify()
        self.wm_protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window(self)
        return self.selection
