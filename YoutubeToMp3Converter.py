from os import path
from tkinter.filedialog import askdirectory, askopenfile
import threading
from tkinter import StringVar
import youtube_dl
import tkinter as tk
import re

root = None
TB_URL = None
TB_DESTINATION_PATH = None
BTN_START_DOWNLOAD = None
ERR_MSG = None
BTN_SELECT_DIR = None
BTN_DOWNLOAD_FROM_TXT = None
YOUTUBE_URL_REGEX = re.compile('^(https\:\/\/)?(www\.youtube\.[a-z]{2,4}|youtu\.?be)\/.+$')


def read_youtube_urls():
    """
    Required format that the txt file containing the youtube urls must have:
        url_1
        url_2
        .
        .
        .
        url_n
    :param filepath:
    :return:
    """
    yt_urls = []
    file_to_read = askopenfile(mode='r', filetypes=[('Text file', '*.txt')])

    if file_to_read is not None:
        while True:
            curr_url = file_to_read.readline()
            cleaned_curr_url = curr_url.strip().rstrip('\n').strip('\r').strip('\t')
            if not curr_url:
                break
            if not cleaned_curr_url:
                continue
            if YOUTUBE_URL_REGEX.findall(cleaned_curr_url):
                yt_urls.append(cleaned_curr_url)
            else:
                show_error_message(f'"{cleaned_curr_url}" IS NOT A VALID YOUTUBE URL. SKIPPED.')

    return yt_urls


def select_download_dir():
    global TB_DESTINATION_PATH
    download_dir = askdirectory()
    if TB_DESTINATION_PATH:
        TB_DESTINATION_PATH['state'] = tk.NORMAL
        TB_DESTINATION_PATH.delete(0, tk.END)
        TB_DESTINATION_PATH.insert(0, download_dir)
        TB_DESTINATION_PATH['state'] = tk.DISABLED


########################### THREADS ###################################
def convert_multiple_youtube_to_mp3():
    t = threading.Thread(target=start_convert_multiple_youtube_to_mp3, args=())
    t.start()


def convert_video_to_mp3():
    t_d = threading.Thread(target=start_download, args=())
    t_d.start()
#######################################################################


##################### YOUTUBE-DL YOUTUBE TO MP3 CONVERSION ############
def get_vid_info(vid_url):
    vid_info = youtube_dl.YoutubeDL().extract_info(
        url=vid_url, download=False
    )
    return vid_info


def get_video_options(vid_dest):
    vid_name = '%(title)s.%(ext)s'
    youtube_dl_options = {
        'format': 'bestaudio/best',
        'outtmpl': path.join(vid_dest, vid_name),
        'keepvideo': False,
        # 'prefer_ffmpeg': True, --> optional
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    return youtube_dl_options
####################################################################################


########################################## HANDLING ERROR MESSAGES AND CHECK FOR YOUTUBE URL VALIDITY #####################
def destory_err_message():
    global ERR_MSG
    if ERR_MSG:
        ERR_MSG.destroy()


def show_error_message(msg="Please provide a youtube URL."):
    global root, ERR_MSG
    str_var = StringVar()
    ERR_MSG = tk.Label(master=root, textvariable=str_var, relief=tk.RAISED, bg='black')
    str_var.set(msg)
    ERR_MSG.configure(state=tk.DISABLED)
    ERR_MSG.place(relx=0.0, rely=1.0, anchor='sw')
    # ERR_MSG.place(relx=1.0, rely=1.0, anchor='se')
    # ERR_MSG.pack()


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
##############################################################################################


########################################## BUTTONS TOGGLES ###################################
def toggle_download_btns_state():
    global BTN_START_DOWNLOAD, BTN_DOWNLOAD_FROM_TXT
    if BTN_START_DOWNLOAD:
        if BTN_START_DOWNLOAD['state'] == tk.NORMAL:
            BTN_START_DOWNLOAD['state'] = tk.DISABLED
        else:
            BTN_START_DOWNLOAD['state'] = tk.NORMAL
    if BTN_DOWNLOAD_FROM_TXT:
        if BTN_DOWNLOAD_FROM_TXT['state'] == tk.NORMAL:
            BTN_DOWNLOAD_FROM_TXT['state'] = tk.DISABLED
        else:
            BTN_DOWNLOAD_FROM_TXT['state'] = tk.NORMAL


##################################### HANDLE SINGLE URL DOWNLOAD AND MULTIPLE URLS DOWNLOADS LOGIC ###############
def start_convert_multiple_youtube_to_mp3():
    try:
        vids_dest = get_download_destination_path()
        urls_to_download = read_youtube_urls()

        # only continue when there are urls to download
        if not urls_to_download:
            return

        # disable both download btn and btn of download from txt file
        toggle_download_btns_state()

        vids_options = get_video_options(vids_dest)
        vids_info = []

        for yt_url in urls_to_download:
            vids_info.append(get_vid_info(yt_url))

        # start downloading and converting the given youtube videos to mp3
        with youtube_dl.YoutubeDL(vids_options) as ydl:
            ydl.download([vid_info['webpage_url'] for vid_info in vids_info])

        toggle_download_btns_state()
    except Exception as e:
        show_error_message(str(e))
        toggle_download_btns_state()


def start_download():
    try:
        vid_url = get_url_from_textbox()
        vid_dest = get_download_destination_path()

        if url_check(vid_url) is False:
            return

        toggle_download_btns_state()

        vid_info = get_vid_info(vid_url)
        vid_options = get_video_options(vid_dest)

        # start download
        with youtube_dl.YoutubeDL(vid_options) as ydl:
            ydl.download([
               vid_info['webpage_url']
            ])

        toggle_download_btns_state()
    except Exception as e:
        show_error_message(str(e))
        toggle_download_btns_state()
##########################################################################################


###################################### WIDGETS CREATION (Buttons and Textboxes) #####################
def create_root_buttons():
    global root, BTN_START_DOWNLOAD, BTN_SELECT_DIR, BTN_DOWNLOAD_FROM_TXT
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
    BTN_DOWNLOAD_FROM_TXT = tk.Button(
        master=root,
        text="Convert multiple youtube videos",
        width=25,
        height=5,
        command=convert_multiple_youtube_to_mp3
    )
    BTN_START_DOWNLOAD.pack()
    BTN_SELECT_DIR.pack()
    BTN_DOWNLOAD_FROM_TXT.pack()


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
###############################################################################################


########################################## GETTERS ##########################################
def get_url_from_textbox():
    return TB_URL.get().strip()


def get_download_destination_path():
    dest = TB_DESTINATION_PATH.get().strip()

    # if destination textbox is left empty, then just default to current directory of the script
    if dest is '' or dest is None:
        return path.dirname(__file__)

    return TB_DESTINATION_PATH.get()
##############################################################################################


########################################## MAIN GUI ##########################################
def init_tkinter_root(size):
    global root
    root = tk.Tk()
    root.wm_iconbitmap('logo.ico')
    root.title("Youtube to MP3")
    root.geometry(size)
    root.minsize(400, 350)
    root.maxsize(1000, 600)

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Add widgets
    create_root_textboxes()
    create_root_buttons()

    root.mainloop()


def main(size_width=575, size_height=350):
    init_tkinter_root(f'{size_width}x{size_height}')


if __name__ == '__main__':
    main()
