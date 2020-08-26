from os import path
from tkinter.filedialog import askdirectory
import youtube_dl
import tkinter as tk
import re

root = None
TB_URL = None
TB_DESTINATION_PATH = None
BTN_START_DOWNLOAD = None
ERR_MSG = None
BTN_SELECT_DIR = None
YOUTUBE_URL_REGEX = re.compile('^(https\:\/\/)?(www\.youtube\.[a-z]{2,4}|youtu\.?be)\/.+$')


def get_vid_info(vid_url):
    vid_info = youtube_dl.YoutubeDL().extract_info(
        url=vid_url, download=False
    )
    return vid_info


def get_video_options(vid_info, vid_dest):
    vid_name = f'{vid_info["title"]}.mp3'
    youtube_dl_options = {
        'format': 'bestaudio/best',
        'keepvideo': False,
        'outtmpl': path.join(vid_dest, vid_name),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }]
    }
    return youtube_dl_options


def destory_err_message():
    global ERR_MSG
    if ERR_MSG:
        ERR_MSG.destroy()


def show_error_message(msg="Please provide a youtube URL."):
    global root, ERR_MSG
    ERR_MSG = tk.Text(master=root)
    ERR_MSG.insert('1.0', msg)
    ERR_MSG.configure(state=tk.DISABLED)
    ERR_MSG.pack(side=tk.BOTTOM)


def url_check(url):
    destory_err_message()
    if url is "":
        show_error_message()
        return False
    elif url is None:
        show_error_message()
        return False
    elif not YOUTUBE_URL_REGEX.findall(url):
        show_error_message("Please provide a valid Youtube URL!")
        return False
    else:
        return True


def convert_video_to_mp3():
    vid_url = get_url_from_textbox()
    vid_dest = get_destination_from_textbox()

    if url_check(vid_url) is False:
        return

    vid_info = get_vid_info(vid_url)
    vid_options = get_video_options(vid_info, vid_dest)

    # start download
    with youtube_dl.YoutubeDL(vid_options) as ydl:
        ydl.download([
            vid_info['webpage_url']
        ])


def select_download_dir():
    global TB_DESTINATION_PATH
    download_dir = askdirectory()
    if TB_DESTINATION_PATH:
        TB_DESTINATION_PATH['state'] = tk.NORMAL
        TB_DESTINATION_PATH.delete(0, tk.END)
        TB_DESTINATION_PATH.insert(0, download_dir)
        TB_DESTINATION_PATH['state'] = tk.DISABLED


def create_root_buttons():
    global root, BTN_START_DOWNLOAD, BTN_SELECT_DIR
    BTN_START_DOWNLOAD = tk.Button(
        master=root,
        text="Start download",
        width=25,
        height=5,
        command=convert_video_to_mp3
    )
    BTN_SELECT_DIR = tk.Button(
        master=root,
        text="Select download directory",
        width=25,
        height=5,
        command=select_download_dir
    )
    BTN_START_DOWNLOAD.pack()
    BTN_SELECT_DIR.pack()


def create_root_textboxes():
    global TB_URL, TB_DESTINATION_PATH
    # create url label and textbox
    url_label = tk.Label(text="Youtube Video URL (required)")
    TB_URL = tk.Entry(width=80)
    url_label.pack()
    TB_URL.pack()

    # create destination label and textbox
    destination_label = tk.Label(text="Destination path (where to download the mp3 file)."
                                      " Leave empty to download mp3 file in current directory")
    TB_DESTINATION_PATH = tk.Entry(state=tk.DISABLED, width=80)
    destination_label.pack()
    TB_DESTINATION_PATH.pack()


def get_url_from_textbox():
    return TB_URL.get().strip()


def get_destination_from_textbox():
    dest = TB_DESTINATION_PATH.get().strip()

    # if destination textbox is left empty, then just default to current directory of the script
    if dest is '' or dest is None:
        return path.dirname(__file__)

    return TB_DESTINATION_PATH.get()


def init_tkinter_root(size):
    global root
    root = tk.Tk()
    root.title = "Youtube to MP3"
    root.geometry(size)
    root.minsize(400, 220)
    root.maxsize(1000, 600)

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Code to add widgets:
    create_root_textboxes()
    create_root_buttons()

    root.mainloop()


def main(size_width=575, size_height=220):
    init_tkinter_root(f'{size_width}x{size_height}')


if __name__ == '__main__':
    main()
