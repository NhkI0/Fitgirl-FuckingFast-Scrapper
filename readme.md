# <img src="https://i1.sndcdn.com/artworks-d8IEGpJtVDjlQ76b-wfBUFA-t500x500.jpg" width="50"> Fitgirl Repacks Fucking Fast Scrapper 

This CLI scrapper allows you to download free games from 
<a href="https://fitgirl-repacks.site" target="_blank">FitGirl Repacks</a>
using the FuckingFast file hosting service. This is intended to be a download manager if you want a more complete 
solution you should try the <a href="https://github.com/CarrotRub/Fit-Launcher" target="_blank">Fit Launcher</a>.
<br>**⚠️I am not affiliated with FitGirl Repacks nor anyone⚠️** I am just a student who wanted to bypass my school
network policies while not installing everything file by file :)
## Why should you use this program ?
**⚠️Pirating games is bad you shouldn't do it, support the original creators of the games if you can⚠️**,
however this being said:

|                                             Pros ✅                                              |                       Cons ❌                       |
|:-----------------------------------------------------------------------------------------------:|:--------------------------------------------------:|
|                                    Faster than most Torrents                                    |      Old games don't have FuckingFast hosting      |
|                         Not blocked by school or work network policies                          |      Still need to install it the regular way      |
|                               Allows you to download part by part                               | Need to do selective download manually *(For now)* |
| No need to setup everything after the start of the download, even after restarting the computer | Must copy paste the links by hand <br>(For now)
## Configuration
### 1. Open a terminal inside the cloned folder.<br>
### 2. Install the requirements.
`````shell
pip install -r ./requirements.txt
`````
### 3. Set a destination folder<br>
The destination path is set inside a file so the program can remind it for next times.
To set the destination folder you can either run one of the following:
````shell
python main.py set_path --path C:/MyPath
python main.py set_path -p C:/MyPath
````
***
Or set it yourself inside ***conf.txt***, please note that you need to have only one line with the correct path for it to work 
properly.<br>
If the destination folder doesn't exist it will be created once the program start.
### 4. Add the links
For the same reason as before the links need to be  inside a folder, this time regarding the high number of links in 
some game you need to copy-paste everything inside ***links.txt***. To do so you have two easy ways:

![Screen of the PasteBin to FuckingFast](https://nguengant.fr/file-hosting/fuckingFast_img.png)<br>
Either click on the **Raw text** button and copy-paste everything inside ***links.txt***.

Or click on the **Save Paste** one and rename the downloaded file ***links.txt*** then move it inside the project 
folder.
## Run
Project CLI helper:
````shell
FitGirl Fast Scraper CLI

positional arguments:
  {start_download,resume_download,set_path}

options:
  -h, --help            show this help message and exit
  -s START, --start START
                        The index of the first link to download. 0 by default.
  -e END, --end END     The index of the last link to download. Will go to the end by default.
  -p PATH, --path PATH  Set the path to save the files to
  -sl, --skip_last      If True avoid re-downloading the last file. If False re-download and overwrite it to ensure it
                        has been well downloaded and not corrupted.
````
Once everything before is done you just have to use the following command:
````shell
python main.py start_download
````
The following exemple will start downloading the 2nd link and all the others until it reach the 11th:
````shell
python main.py start_download -s 2 -e 11
````
***
If you have already started the download before you can try using:
````shell
python main.py resume_download
````
This will automatically start the download at the current index.<br>
⚠️For this to work you need to have only the other parts in your directory !⚠️


The following exemple will continue the previous download without re-downloading the last element and stop 
at the 3rd link:
````shell
python main.py resume_download -e 3 -sl
````

#### By default, it will re-download the last element to ensure it hasn't been corrupted, in the case of a crash or manual interruption. However, if you are sure it was well downloaded you can specify the *-sl* argument.

## How to do selective download
For now there is no automated selective download. But it is still possible to set it manually for so, just count index
of the dlc or language pack you don't want and set the previous one as the --end argument. If you want to only download
a dlc you can use its first and last index in the --start and --end arguments.