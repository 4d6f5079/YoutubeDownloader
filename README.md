# YoutubeDownloader

---

# Requirements

1. Python 3.3 or higher (preferably version 3.8)
2. Git Bash
3. FFMpeg.exe file in the same folder as youtube-dl package in virtualenv directory.
4. (OPTIONAL) FFProbe.exe file
5. (OPTIONAL, does not work in exe file of the youtube downloader!) To be able to download via TOR network you have to have downloaded and started the Tor Windows Expert Bundle = https://www.torproject.org/download/tor/

---

# Installation

```
./build_env.sh
```

## After this set python interpreter to python.exe in the generated venv directory (if coding in VSCode)

---

## List of some features

- Playlist download functionality
- Downloads via TOR network (Optional)
- Supports mp4 youtube videos

## TODOS

1. Show the error messages properly with red color and on top of all the other components of the gui
2. Make use of the Tkinter Grid to make components more responsive
3. Use event listener of the youtube url entry to constantly check whether the input is acceptable or not and show error messages accordingaly
4. Make use of text areas that are not editable, as now the error messages is editable by the user
5. Make it possible for the user to provide his/her own name of the mp3 file, instead of always using the default name of the video itself. Make it so that if no name is provided that the video name is used for the mp3 filename.
6. Include a logo for the y2mp3 converter on the front-page on top of al lthe components that come after. Also make background black-grey-ish instead of white.
7. Make TOR work in the executable file.