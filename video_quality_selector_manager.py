import tkinter as tk
from tkinter import Scrollbar, Frame


class VideoQualitySelector(tk.Toplevel):
    def __init__(self, parent, available_formats, vid_name):
        super().__init__(parent)

        self.available_formats = available_formats
        self.vid_title = vid_name
        self.selection = ""

        # init toplevel with title and size
        self.title("Select video quality")
        self.geometry("450x500")

        # create label to show soem text
        self.label = tk.Label(
            master=self, text=f'Select video quality for \n "{self.vid_title}"'
        )
        self.label.pack(pady=7)

        # create frame to put listbox with scrollbar
        self.frame = Frame(self)
        self.frame.pack()

        # create listbox for video quality items
        self.listbox = tk.Listbox(self.frame, height=15, width=40)
        self.listbox.pack(side=tk.LEFT, fill=tk.Y)

        # attach scrollbar to listbox
        self.scrollbar = Scrollbar(self.frame, orient="vertical")
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=self.scrollbar.set)

        # create button to confirm the selected video quality
        self.btn = tk.Button(
            self, text="Confirm selection video quality", command=self.select
        )
        self.btn.pack(pady=7)

        # init listbox with the video quality items
        for (_, f_info) in self.available_formats:
            self.listbox.insert(tk.END, f_info)

    def select(self):
        """
        Get the selected video quality id and destroy the toplevel window
        """
        selection = self.listbox.curselection()
        if selection:
            self.selection = self.available_formats[selection[0]][0]
            self.destroy()

    def show(self):
        """Show the toplevel window and return the video quality id from the user selection

        Returns:
            selection: the selected video quality id
        """
        self.deiconify()
        self.wm_protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window(self)
        return self.selection
