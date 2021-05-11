import tkinter as tk

# TODO:
class VideoQualitySelector():

    def __init__(self, available_formats, vid_name):
        self.available_formats = available_formats
        self.vid_title = vid_name
        self.selected_format = ''

    def select(self):
        format_info = self.listbox.get(tk.ANCHOR)
        for (f_id, f_info) in self.available_formats:
            if format_info == f_info:
                self.selected_format = f_id
                self.win.destroy()

    def __enter__(self):
        self.win = tk.Toplevel()
        self.win.title("Select video quality for video: ")
        self.win.geometry("450x500")

        self.label = tk.Label(
                master=self.win,
                text=f"Select video quality for {self.vid_title}"
        )
        self.label.pack(pady=7)

        self.listbox = tk.Listbox(self.win, height=20, width=40)
        self.listbox.pack(pady=15)

        self.btn = tk.Button(self.win, text="Confirm selection video quality", command=self.select)
        self.btn.pack(pady=7)

        for (_, f_info) in self.available_formats:
            self.listbox.insert(tk.END, f_info) 

        self.win.wait_window()

        return self.selected_format

    def __exit__(self, exc_type, exc_val, traceback):
        pass