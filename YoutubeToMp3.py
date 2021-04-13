from os import path, environ
from tkinter.filedialog import askdirectory
from tkinter.ttk import Progressbar
import threading
from tkinter import messagebox, Tk, Menu
import youtube_dl
import tkinter as tk
import re

root = None
TB_URL = None
TB_DESTINATION_PATH = None
BTN_START_DOWNLOAD = None
ERR_MSG = None
PROGRESS_BAR = None
RIGHT_CLICK_MENU = None
YOUTUBE_URL_REGEX = re.compile('^(https\:\/\/)?(www\.youtube\.[a-z]{2,4}|youtu\.?be)\/.+[_]*$')
DESKTOP_PATH = path.join(path.join(environ['USERPROFILE']), 'Desktop')

threads = []
proxy = 'socks5://176.9.75.42:1080'

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
    global threads
    t_d = threading.Thread(target=start_download, args=())
    t_d.start()
    threads.append(t_d)
#######################################################################


##################### YOUTUBE-DL YOUTUBE TO MP3 CONVERSION FOR GETTING VIDEO INFO AND OPTIONS THAT YOUTUBE-DL NEEDS ############
def get_vid_info(vid_url):
    vid_info = youtube_dl.YoutubeDL({'quiet': True}).extract_info(
        url=vid_url, download=False
    )
    return vid_info


def get_video_options(vid_dest, proxy=None):
    vid_name = '%(title)s.%(ext)s'
    youtube_dl_options = {
        'format': 'bestaudio/best',
        'outtmpl': path.join(vid_dest, vid_name),
        'keepvideo': False,
        'quiet': True,
        'progress_hooks': [show_progress],
        # 'proxy': 'socks5://127.0.0.1:1080', --> specify proxy
        # 'postprocessor_args': '-hide_banner -loglevel warning',
        'prefer_ffmpeg': True, # --> optional
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }
    if proxy:
        youtube_dl_options['proxy'] = proxy
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
            PROGRESS_BAR['value'] = 0

        if data['status'] == 'downloading':
            p = data['_percent_str']
            p = p.replace('%', '')
            PROGRESS_BAR['value'] = float(p)

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


########################################## SHOW RIGHT CLICK MENU ###################################
def right_click_menu():
    global root, RIGHT_CLICK_MENU
    if root:
        RIGHT_CLICK_MENU = Menu(root, tearoff=0)
        RIGHT_CLICK_MENU.add_command(label="Cut", command=lambda: root.focus_get().event_generate('<<Cut>>'))
        RIGHT_CLICK_MENU.add_command(label="Copy", command=lambda: root.focus_get().event_generate('<<Copy>>'))
        RIGHT_CLICK_MENU.add_command(label="Paste", command=lambda: root.focus_get().event_generate('<<Paste>>'))
        root.bind("<Button-3>", right_click_handler)


def right_click_handler(event):
    global RIGHT_CLICK_MENU
    try:
        RIGHT_CLICK_MENU.tk_popup(event.x_root, event.y_root)
    finally:
        RIGHT_CLICK_MENU.grab_release()
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
def youtube_dl_download(vid_info, vid_dest, with_proxy=False, retries=0):
    global proxy

    if with_proxy:
        vid_options = get_video_options(vid_dest, proxy=proxy)
    else:
        vid_options = get_video_options(vid_dest)

    try:
        with youtube_dl.YoutubeDL(vid_options) as ydl:
            ydl.download([
                vid_info['webpage_url']
            ])
    except Exception as e:
        print(str(e))
        # if retries <= 3:
        #     youtube_dl_download(vid_info, vid_dest, with_proxy=True, retries=retries+1)


def start_download():
    global proxy
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

        # start download
        # TODO: test this new functionality
        youtube_dl_download(vid_info, vid_dest)

        toggle_download_btns_state()

        show_info_message(
            'THE MP3 FILE HAS BEEN DOWNLOADED SUCCESSFULLY!',
            f'MP3 file {vid_info["title"]} downloaded successfully!'
            f'\n MP3 file is downloaded on the DESKTOP.'
        )

    except Exception as e:
        show_error_message(str(e))
        toggle_download_btns_state()
##########################################################################################


###################################### WIDGETS CREATION (Buttons and Textboxes) #####################
def create_root_buttons():
    global root, BTN_START_DOWNLOAD
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


#################################### HANDLE CLOSING OF TKINTER WINDOW #############################################
def exit_handler():
    global threads, root
    for t in threads:
        if not t.is_alive():
            t.handled = True
        else:
            t.handled = False
    threads = [t for t in threads if not t.handled]
    if not threads:
        root.destroy()
##############################################################################################


########################################## MAIN GUI ##########################################
def init_tkinter_root(size):
    global root
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", exit_handler)
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
    right_click_menu()

    root.mainloop()


def main(size_width=575, size_height=350):
    init_tkinter_root(f'{size_width}x{size_height}')


if __name__ == '__main__':
    main()