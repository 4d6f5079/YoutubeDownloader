from os import path
import youtube_dl
import tkinter as tk
import re

gui = None
tb_url = None
tb_destination_path = None
btn_convert = None
err_msg = None
youtube_uris_regex = re.compile('^(https\:\/\/)?(www\.youtube\.[a-z]{2,4}|youtu\.?be)\/.+$')


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
    global err_msg
    if err_msg:
        err_msg.destroy()


def show_error_message(msg="Please provide a youtube URL."):
    global gui, err_msg
    err_msg = tk.Text(master=gui)
    err_msg.insert('1.0', msg)
    err_msg.pack()


def url_check(url):
    destory_err_message()
    if url is "":
        show_error_message()
        return False
    elif url is None:
        show_error_message()
        return False
    elif not youtube_uris_regex.findall(url):
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


def create_gui_buttons():
    global gui, btn_convert
    btn_convert = tk.Button(
        master=gui,
        text="Start download",
        width=25,
        height=5,
        command=convert_video_to_mp3
    )
    btn_convert.pack()


def create_gui_textboxes():
    global tb_url, tb_destination_path
    # create url label and textbox
    url_label = tk.Label(text="Youtube Video URL (required)")
    tb_url = tk.Entry(width=80)
    url_label.pack()
    tb_url.pack()

    # create destination label and textbox
    destination_label = tk.Label(text="Destination path (where to download the mp3 file)."
                                      " Leave empty to download mp3 file in current directory")
    tb_destination_path = tk.Entry(width=80)
    destination_label.pack()
    tb_destination_path.pack()


def get_url_from_textbox():
    return tb_url.get().strip()


def get_destination_from_textbox():
    dest = tb_destination_path.get().strip()

    # if destination textbox is left empty, then just default to current directory of the script
    if dest is '' or dest is None:
        return path.dirname(__file__)

    return tb_destination_path.get()


def init_tkinter_gui(size):
    global gui
    gui = tk.Tk()
    gui.title = "Youtube to MP3"
    gui.geometry(size)
    gui.minsize(575, 220)
    gui.maxsize(600, 220)

    # Code to add widgets:
    create_gui_textboxes()
    create_gui_buttons()

    gui.mainloop()


def main(size_width=575, size_height=220):
    init_tkinter_gui(f'{size_width}x{size_height}')


if __name__ == '__main__':
    main()
