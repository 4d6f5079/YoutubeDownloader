from os import path
from tkinter.filedialog import askdirectory, askopenfile
from tkinter.ttk import Progressbar
from tkinter import Menu, messagebox
import threading
import youtube_dl
import tkinter as tk
import re
import random
from tor_handler import TorHandler

import logging
logging.basicConfig(
    filename='logs.log',
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

root = None
TB_URL = None
TB_DESTINATION_PATH = None
BTN_START_DOWNLOAD = None
BTN_SELECT_DIR = None
BTN_DOWNLOAD_FROM_TXT = None
RIGHT_CLICK_MENU = None
PROXY_BUTTON = None
TOPLEVEL_WINDOW = None
CONVERSION_MODE_BTN = None
TOR_HANDLER = TorHandler()

USING_PROXY = False
TOR_PROXY_CHECKED = 0
CAN_CONNECT_TO_TOR = False

CONVERSION_MODE = 'mp3'
USERAGENTS_FILEPATH = './useragents.txt'
CURRENT_SCRIPT_PATH = path.abspath(path.dirname(__file__))
UNEXPCTED_ERR_MSG = 'Unexpected error occured. Please check logs for more info.'

threads = []

# mp4 video quality enum class
# class VideoQuality:
#     _1080P = '137' # mp4, no audio
#     _720P = '136' # mp4, no audio
#     _480P = '135' # mp4, no audio
#     _360P = '134' # mp4, no audio
#     _240P = '133' # mp4, no audio
#     _m4a_256k = '141' # m4a [256k] (DASH Audio)
#     _m4a_128k = '140' # m4a [128k] (DASH Audio)
#     _m4a_48k = '139' # m4a [48k] (DASH Audio)

# this regex matches youtube urls with optional 'www.' behind 'youtube'
# alternative complicated regex: ^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$
YOUTUBE_URL_REGEX = re.compile('^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$')
YOUTUBE_PLAYLIST_URL_REGEX = re.compile('^(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?.*?(?:v|list)=(.*?)(?:&|$)|^(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?(?:(?!=).)*\/(.*)$')

################################# PROGRESS BAR ##################################################################
def create_toplevel_tk_window(label_text=None):
    global root, TOPLEVEL_WINDOW

    newWindow = tk.Toplevel(root)
    newWindow.title("Downloading...")
    newWindow.geometry("275x125")

    if label_text:
        label = tk.Label(master=newWindow, text=label_text, wraplength=newWindow.winfo_width())
        label.grid(row=0,column=0)

    TOPLEVEL_WINDOW = newWindow

def show_progress(data):
    global TOPLEVEL_WINDOW
    
    try:
        # creating progress bar
        progress_bar = Progressbar(TOPLEVEL_WINDOW, length=250, s='black.Horizontal.TProgressbar')
        progress_bar['value'] = 0
        progress_bar.grid(row=1,column=0)

        if data['status'] == 'finished':
            progress_bar['value'] = 100
            progress_bar.destroy()
            TOPLEVEL_WINDOW.destroy()
            TOPLEVEL_WINDOW = None

        if data['status'] == 'downloading':
            p = data['_percent_str']
            p = p.replace('%', '')
            progress_bar['value'] = float(p)

    except Exception:
        show_error_message(UNEXPCTED_ERR_MSG)
        logging.exception(UNEXPCTED_ERR_MSG)
        progress_bar.destroy()
        if TOPLEVEL_WINDOW:
            TOPLEVEL_WINDOW.destroy()
            TOPLEVEL_WINDOW = None
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
    if TB_DESTINATION_PATH and download_dir:
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

################################## PROXY STUFF $##########################
# def get_random_ua():
#     # if file can be loaded in memory use: random.choice(open("useragents.txt").readlines())
#     # Waterman's "Reservoir Algorithm" to get 1 line from file randomly in memory efficient way
#     with open('useragents.txt') as f:
#         line = next(f)
#         for num, aline in enumerate(f, 2):
#             if random.randrange(num):
#                 continue
#             line = aline
#         return line

def get_proxy():
    # TODO: get random proxy if tor is not working
    return TOR_HANDLER.socks5_url
##################################################################################

##################### YOUTUBE-DL YOUTUBE TO MP3 CONVERSION FOR GETTING VIDEO INFO AND OPTIONS THAT YOUTUBE-DL NEEDS ############
def get_vid_info(vid_url):
    with youtube_dl.YoutubeDL() as ydl:
        vid_info = ydl.extract_info(
            url=vid_url, download=False
        )
    return vid_info


def get_video_options(vid_dest, progress_bar=True):
    global USING_PROXY, CONVERSION_MODE

    vid_name = '%(title)s.%(ext)s'

    if CONVERSION_MODE == 'mp3':
        youtube_dl_options = {
            'format': 'bestaudio/best',
            'outtmpl': path.join(vid_dest, vid_name),
            'keepvideo': False,
            'quiet': True,
            # 'prefer_ffmpeg': True, # --> optional
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    else:
        # TODO: make user choose from the available quality format of the video
        # if no format specified, youtube_dl will download the best video+audio of the video
        youtube_dl_options = {
            'outtmpl': path.join(vid_dest, vid_name),
            'quiet': True
        }

    if USING_PROXY:
        proxy = get_proxy()
        if proxy:
            youtube_dl_options['proxy'] = proxy
            youtube_dl_options['nocheckcertificate'] = True

    if progress_bar:
        youtube_dl_options['progress_hooks'] = [show_progress]

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
            for vid_info in vids_info:
                # create toplevel window to show download progress for each download
                create_toplevel_tk_window(vid_info['title'])
                ydl.download([vid_info['webpage_url']])

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
    global TOPLEVEL_WINDOW
    try:
        vid_url = get_url_from_textbox()
        vid_dest = get_download_destination_path()

        if url_check(vid_url) is False:
            return

        toggle_download_btns_state()
        
        vids_info = get_vid_info(vid_url)

        # if link consists of multiple videos (playlist) then vids_info contains 'entries' otherwise there is 1 video
        if 'entries' in vids_info:
            vids_options = get_video_options(vid_dest, progress_bar=False)
        else:
            vids_options = get_video_options(vid_dest)
            create_toplevel_tk_window(vids_info['title'])

        with youtube_dl.YoutubeDL(vids_options) as ydl:
            ydl.download([
                vids_info['webpage_url']
            ])

        toggle_download_btns_state()

        if 'entries' in vids_info:
            show_info_message(
                f'Playlist {vids_info["title"]} downloaded successfully!',
                'PLAYLIST DOWNLOADED SUCCESSFULLY!'
            )
        else:
            show_info_message(
                f'MP3 file {vids_info["title"]} downloaded successfully!',
                'THE MP3 FILE HAS BEEN DOWNLOADED SUCCESSFULLY!'
            )

    except Exception as e:
        show_error_message(UNEXPCTED_ERR_MSG)
        logging.exception(UNEXPCTED_ERR_MSG)
        toggle_download_btns_state()
    
def handle_proxy_btn():
    global PROXY_BUTTON, USING_PROXY, TOR_PROXY_CHECKED, CAN_CONNECT_TO_TOR
    if PROXY_BUTTON:
        if PROXY_BUTTON.config('text')[-1] == 'Currently NOT using proxy':
            TOR_PROXY_CHECKED += 1

            if TOR_PROXY_CHECKED % 5 == 0: # check TOR connection after every 5 clicks on the button 
                try:
                    CAN_CONNECT_TO_TOR, ip, tor_ip = TOR_HANDLER.test_tor_proxy_connection()
                except Exception:
                    show_error_message(UNEXPCTED_ERR_MSG)
                    logging.error(UNEXPCTED_ERR_MSG)
                    return
            if CAN_CONNECT_TO_TOR:
                show_info_message(f'Testing TOR Proxy\nYour IP:\n{ip}\nTor IP:\n{tor_ip}\nTor IP working correctly!')
                PROXY_BUTTON.config(text='Currently using TOR proxy')
                USING_PROXY = True
            else:
                show_info_message('Your IP and Tor IP are the same: check whether you are running tor from commandline')
        
        else:
            PROXY_BUTTON.config(text='Currently NOT using proxy')
            USING_PROXY = False

def toggle_download_mode():
    global CONVERSION_MODE_BTN, CONVERSION_MODE
    if CONVERSION_MODE_BTN:
        if CONVERSION_MODE_BTN.config('text')[-1] == 'Current conversion mode: mp3':
            CONVERSION_MODE_BTN.config(text='Current conversion mode: mp4')
            CONVERSION_MODE = 'mp4'
        else:
            CONVERSION_MODE_BTN.config(text='Current conversion mode: mp3')
            CONVERSION_MODE = 'mp3'
##########################################################################################


###################################### WIDGETS CREATION (Buttons and Textboxes) #####################
def create_root_buttons():
    global root, BTN_START_DOWNLOAD, BTN_SELECT_DIR, BTN_DOWNLOAD_FROM_TXT, PROXY_BUTTON, CONVERSION_MODE_BTN 
    PROXY_BUTTON = tk.Button(
        master=root,
        text="Currently NOT using proxy",
        command=handle_proxy_btn
    )
    CONVERSION_MODE_BTN = tk.Button(
        master=root,
        text="Current conversion mode: mp3",
        command=toggle_download_mode
    )
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
    BTN_START_DOWNLOAD.pack(pady=5)
    BTN_SELECT_DIR.pack(pady=5)
    BTN_DOWNLOAD_FROM_TXT.pack(pady=5)
    PROXY_BUTTON.pack(pady=5)
    CONVERSION_MODE_BTN.pack(pady=5)


def create_root_textboxes():
    global TB_URL, TB_DESTINATION_PATH
    # create url label and textbox
    url_label = tk.Label(text="Youtube Video URL (required)")
    TB_URL = tk.Entry(width=80)
    url_label.pack()
    TB_URL.pack()

    # create destination label and textbox
    destination_label = tk.Label(text="Destination path (where to download the video/mp3).")
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


def main(size_width=575, size_height=475):
    init_tkinter_root(f'{size_width}x{size_height}')


if __name__ == '__main__':
    main()
    
