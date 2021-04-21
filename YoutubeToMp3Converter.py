from os import path
from tkinter.filedialog import askdirectory, askopenfile
from tkinter.ttk import Progressbar
import threading
from tkinter import StringVar, Menu, messagebox
import youtube_dl
import tkinter as tk
import re

import logging
logging.basicConfig(
    filename='logs.log',
    level=logging.DEBUG
)

root = None
TB_URL = None
TB_DESTINATION_PATH = None
BTN_START_DOWNLOAD = None
BTN_SELECT_DIR = None
BTN_DOWNLOAD_FROM_TXT = None
RIGHT_CLICK_MENU = None
CURRENT_SCRIPT_PATH = path.abspath(path.dirname(__file__))
UNEXPCTED_ERR_MSG = 'Unexpected error occured. Please check logs for more info.'

threads = []

# this regex matches youtube urls with optional 'www.' behind 'youtube'
# alternative complicated regex: ^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$
YOUTUBE_URL_REGEX = re.compile('^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$')
YOUTUBE_PLAYLIST_URL_REGEX = re.compile('^(https|http):\/\/(?:www\.)?youtube\.com\/watch\?(?:&.*)*((?:v=([a-zA-Z0-9_\-]{11})(?:&.*)*&list=([a-zA-Z0-9_\-]{18}))(?:list=([a-zA-Z0-9_\-]{18})(?:&.*)*&v=([a-zA-Z0-9_\-]{11})))(?:&.*)*(?:\#.*)*$')

################################# PROGRESS BAR ##################################################################

def show_progress(data):
    global root

    try:
        # creating progress bar
        PROGRESS_BAR = Progressbar(root, length=250, s='black.Horizontal.TProgressbar')
        PROGRESS_BAR['value'] = 0
        PROGRESS_BAR.place(x=125, y=175)

        if data['status'] == 'finished':
            PROGRESS_BAR['value'] = 100
            PROGRESS_BAR.destroy()

        if data['status'] == 'downloading':
            p = data['_percent_str']
            p = p.replace('%', '')
            PROGRESS_BAR['value'] = float(p)

    except Exception:
        show_error_message(UNEXPCTED_ERR_MSG)
        logging.exception(UNEXPCTED_ERR_MSG)
        PROGRESS_BAR.destroy()

###################################################################################################

##################################### UTILITIES #########################
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
###########################################################################


########################### THREADS ###################################
def convert_multiple_youtube_to_mp3():
    t = threading.Thread(target=start_convert_multiple_youtube_to_mp3, args=())
    t.start()
    threads.append(t)


def convert_video_to_mp3():
    t_d = threading.Thread(target=start_download, args=())
    t_d.start()
    threads.append(t_d)
#######################################################################

################################## PROXY GETTER HELPER $##########################
def get_proxy():
    # TODO: get random proxy that is safe, trusted and working
    # Example: 'socks5://127.0.0.1:1080'
    return None
##################################################################################

##################### YOUTUBE-DL YOUTUBE TO MP3 CONVERSION FOR GETTING VIDEO INFO AND OPTIONS THAT YOUTUBE-DL NEEDS ############
def get_vid_info(vid_url):
    with youtube_dl.YoutubeDL() as ydl:
        vid_info = ydl.extract_info(
            url=vid_url, download=False
        )
    return vid_info


def get_video_options(vid_dest, use_proxy=False):
    vid_name = '%(title)s.%(ext)s'
    youtube_dl_options = {
        'format': 'bestaudio/best',
        'outtmpl': path.join(vid_dest, vid_name),
        'progress_hooks': [show_progress],
        'keepvideo': False,
        'quiet': True,
        # 'prefer_ffmpeg': True, # --> optional
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    if use_proxy:
        proxy = get_proxy()
        if proxy:
            youtube_dl_options['proxy'] = proxy

    return youtube_dl_options
################################################################################################################################


########################################## HANDLING ERROR MESSAGES AND CHECK FOR YOUTUBE URL VALIDITY #####################
def show_info_message(msg, title='Information'):
    messagebox.showinfo(title, msg)

def show_error_message(msg, title='Error'):
    messagebox.showerror(title, msg)

def url_check(url):
    if url == "":
        show_error_message('Youtube URL not provided!')
        return False
    elif url is None:
        show_error_message('Unknown Youtube URL!')
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
        
        show_info_message(
            f'MP3 files downloaded successfully!',
            'THE MP3 FILES HAVE BEEN DOWNLOADED SUCCESSFULLY!'
        )

    except Exception as e:
        show_error_message(UNEXPCTED_ERR_MSG)
        logging.exception(UNEXPCTED_ERR_MSG)
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

        # start download 1 video
        with youtube_dl.YoutubeDL(vid_options) as ydl:
            ydl.download([
                vid_info['webpage_url']
            ])
        ############################################################################
        # TODO: example download playlist list or list of videos
        # with ydl:
        # result = ydl.extract_info(
        #     'http://www.youtube.com/watch?v=BaW_jenozKc',
        #     download=False # We just want to extract the info
        # )

        # if 'entries' in result:
        #     # Can be a playlist or a list of videos
        #     video = result['entries'][0]
        # else:
        #     # Just a video
        #     video = result

        # print(video)
        # video_url = video['url']
        # print(video_url)
        ############################################################################

        toggle_download_btns_state()

        show_info_message(
            f'MP3 file {vid_info["title"]} downloaded successfully!',
            'THE MP3 FILE HAS BEEN DOWNLOADED SUCCESSFULLY!'
        )

    except Exception as e:
        show_error_message(UNEXPCTED_ERR_MSG)
        logging.exception(UNEXPCTED_ERR_MSG)
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
    destination_label = tk.Label(text="Destination path (where to download the mp3 file).")
    TB_DESTINATION_PATH = tk.Entry(state=tk.NORMAL, width=80)

    # insert current directory for the user for convinience
    TB_DESTINATION_PATH.insert(0, CURRENT_SCRIPT_PATH)
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
    if dest == '' or dest is None:
        return CURRENT_SCRIPT_PATH

    return TB_DESTINATION_PATH.get()
##############################################################################################


########################################## SHOW RIGHT CLICK MENU ###############################
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


#################################### HANDLE CLOSING OF TKINTER WINDOW ######################
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
    root.minsize(400, 350)
    root.maxsize(1000, 600)

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
