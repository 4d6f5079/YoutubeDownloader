from os import path, environ
from tkinter.filedialog import askdirectory
from tkinter.ttk import Progressbar
import threading
from tkinter import messagebox, Tk
import youtube_dl
import tkinter as tk
import re

root = None
TB_URL = None
TB_DESTINATION_PATH = None
BTN_START_DOWNLOAD = None
ERR_MSG = None
PROGRESS_BAR = None
YOUTUBE_URL_REGEX = re.compile('^(https\:\/\/)?(www\.youtube\.[a-z]{2,4}|youtu\.?be)\/.+$')
DESKTOP_PATH = path.join(path.join(environ['USERPROFILE']), 'Desktop')

##################################### UTILITIES #########################
def select_download_dir():
    global TB_DESTINATION_PATH
    download_dir = askdirectory()
    if TB_DESTINATION_PATH:
        TB_DESTINATION_PATH['state'] = tk.NORMAL
        TB_DESTINATION_PATH.delete(0, tk.END)
        TB_DESTINATION_PATH.insert(0, download_dir)
        TB_DESTINATION_PATH['state'] = tk.DISABLED
###########################################################################


########################### THREADS ###################################
def convert_video_to_mp3():
    t_d = threading.Thread(target=start_download, args=())
    t_d.start()
#######################################################################


##################### YOUTUBE-DL YOUTUBE TO MP3 CONVERSION FOR GETTING VIDEO INFO AND OPTIONS THAT YOUTUBE-DL NEEDS ############
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
        'progress_hooks': [show_progress],
        # 'prefer_ffmpeg': True, --> optional
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    return youtube_dl_options
################################################################################################################################


################################# PROGRESS BAR ##################################################################

def show_progress(data):
    global root, PROGRESS_BAR

    try:
        # creating progress bar
        PROGRESS_BAR = Progressbar(root, length=250, s='black.Horizontal.TProgressbar')
        PROGRESS_BAR['value'] = 0
        PROGRESS_BAR.place(x=125, y=175)

        if data['status'] == 'finished':
            mp3_file_name = path.split(path.abspath(data['filename']))
            PROGRESS_BAR['value'] = 0
            show_info_message(
                'THE MP3 FILE HAS BEEN DOWNLOADED SUCCESSFULLY!',
                f'MP3 file {mp3_file_name} downloaded successfully!'
                f'\n MP3 file is downloaded on the DESKTOP.'
            )
        if data['status'] == 'downloading':
            p = data['_percent_str']
            p = p.replace('%', '').strip()
            PROGRESS_BAR['value'] = float(p)
            print(data['filename'], data['_percent_str'], data['_eta_str'])

    except Exception as e:
        show_error_message(str(e))
        PROGRESS_BAR.destroy()

###################################################################################################


########################################## HANDLING ERROR MESSAGES AND CHECK FOR YOUTUBE URL VALIDITY #####################
def destory_err_message():
    global ERR_MSG
    if ERR_MSG:
        ERR_MSG.destroy()


def show_info_message(title, msg):
    Tk().wm_withdraw()  # to hide the main window
    messagebox.showinfo(f'{title}' if title else 'DOWNLOAD PROGRESS INFO', f'{msg}')


def show_error_message(msg="Please provide a youtube URL."):
    Tk().wm_withdraw()  # to hide the main window
    messagebox.showerror('SOMETHING WENT WRONG',
                         f'{msg}')


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
    global BTN_START_DOWNLOAD
    if BTN_START_DOWNLOAD:
        if BTN_START_DOWNLOAD['state'] == tk.NORMAL:
            BTN_START_DOWNLOAD['state'] = tk.DISABLED
        else:
            BTN_START_DOWNLOAD['state'] = tk.NORMAL


##################################### HANDLE SINGLE URL DOWNLOAD AND MULTIPLE URLS DOWNLOADS LOGIC ###############
def start_download():
    try:
        vid_url = get_url_from_textbox()
        vid_dest = get_download_destination_path()

        if url_check(vid_url) is False:
            return

        toggle_download_btns_state()

        show_info_message(
            'DOWNLOADING THE MP3 FILE',
            'Please wait until the mp3 file has been downloaded successfully. \n'
            'If video is long, then this may take couple of minutes. \n'
            'Notification will pop up when download is finished!'
        )

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
    global root, BTN_START_DOWNLOAD, BTN_SELECT_DIR
    BTN_START_DOWNLOAD = tk.Button(
        master=root,
        text="Start download",
        width=25,
        height=5,
        command=convert_video_to_mp3
    )
    BTN_START_DOWNLOAD.pack()


def create_root_textboxes():
    global TB_URL, TB_DESTINATION_PATH
    # create url label and textbox
    url_label = tk.Label(text="Youtube Video URL (required)")
    TB_URL = tk.Entry(width=80)
    url_label.pack()
    TB_URL.pack()

    # create destination label and textbox
    destination_label = tk.Label(text="You can find mp3 file on DESKTOP after downloading is finished.")
    TB_DESTINATION_PATH = tk.Entry(state=tk.NORMAL, width=80)
    TB_DESTINATION_PATH.insert(0, DESKTOP_PATH)
    TB_DESTINATION_PATH['state'] = tk.DISABLED
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
    root.minsize(500, 205)
    root.maxsize(500, 210)

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
