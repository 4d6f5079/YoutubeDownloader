# YoutubeToMp3-GUI  

## NOTE: Make sure that ffmpeg exe file is in the same folder as youtube-dl package (python Scripts folder) or if you are using virtualenv then in the Scripts folder of that env folder.

## IMPORTANT TODOS  
1. Correctly align progress bar in new tkinter window - DONE
2. add playlist download functionality
3. make it optional to also be able to download via TOR network - DONE  
4. Add exceptions logger - DONE
5. Support mp4 youtube videos download option
6. Make possible for user to choose video quality when downloading videos in mp4

## NOTE 2: To be able to download via TOR network you have to have downloaded and started the Tor Windows Expert Bundle = https://www.torproject.org/download/tor/ 

# NOTE 3: downloading video twice overrides the old first download! (applies to mp3 and mp4 downloads)

## TODOS  
1. Show the error messages properly with red color and on top of all the other components of the gui  
2. Make use of the Tkinter Grid to make components more responsive  
3. Use event listener of the youtube url entry to constantly check whether the input is acceptable or not and show error messages accordingaly  
4. Make use of text areas that are not editable, as now the error messages is editable by the user  
5. Make it possible for the user to provide his/her own name of the mp3 file, instead of always using the default name of the video itself. Make it so that if no name is provided that the video name is used for the mp3 filename.  
6. Include a logo for the y2mp3 converter on the front-page on top of al lthe components that come after. Also make background black-grey-ish instead of white.