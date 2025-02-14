import os

import requests
from bs4 import BeautifulSoup
import argparse
import re
import download


def set_path(path):
    file = open("./conf.txt", 'w')
    file.write(path)
    file.close()


def start_download(start=0, end=None, links_list=None):
    """
    Start download of the given links in the given directory.
    :param start: The index of the first link to download. 0 by default.
    :param end: The index of the last link to download. Will go to the end by default.
    """
    # Basic assertion to ensure the good work of the download
    assert os.stat("./conf.txt").st_size > 0, "No destination folder set"
    start = int(start)
    if start > 0:
        start -= 1
    if end is not None:
        end = int(end)
        assert end >= 0, "The end value cannot be negative"
        assert end >= start, "The end value cannot lower to the start one"
    assert start >= 0, "The start value cannot be negative"

    # We don't read again the links if we've already done it before
    if links_list is None:
        links_list = get_links()
    assert start <= len(links_list), \
        f"The start index {start+1} is out of range\nMaximum possible index is {len(links_list)}"
    # We get the download path from the file
    file = open("./conf.txt", "r")
    save_path_base = file.read()
    file.close()

    if end is None or end > len(links_list):
        end = len(links_list)
    for i in range(start, end):
        save_path = save_path_base
        pattern = r"#(.*)$"
        match = re.search(pattern, links_list[i])
        if match:
            if match.group(1)[0] == "#":
                save_path = save_path + f"\\{match.group(1)[1:]}"
            else:
                save_path = save_path + f"\\{match.group(1)}"
            download_url = download.get_download_link_from_page(links_list[i])
            print(f"Downloading {i + 1} of {len(links_list)} : {match.group(1)}")
            success = download.download_with_requests(download_url, save_path)
            if success:
                print(f"File saved to: {save_path}\n")
        else:
            print("Couldn't find the name of the file")
    print("All files have been downloaded")


def get_links():
    # Path to the links file
    links_list = []
    file = open("./links.txt", "r")
    links = file.readlines()
    file.close()
    pattern = r"^- (https:\/\/fuckingfast\.co\/\S+)"
    found = False
    isEmpty = True
    for line in links:
        isEmpty = False
        match = re.search(pattern, line)
        if match:
            found = True
            links_list.append(match.group(1))
    if isEmpty:
        print("The given file is empty")
    elif not found:
        print("No links were found inside the file")
    return links_list


def resume_download(skip_last, end):
    """
    Resume the download of the given links in the given directory.
    :param skip_last: If True avoid re-downloading the last file.
    If False re-download and overwrite it to ensure it has been well downloaded and not corrupted.
    :param end: The index of the last link to download. Will go to the end by default.
    """
    links_list = get_links()
    file = open("./conf.txt", "r")
    DIR = file.read()
    file.close()
    start = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])
    if skip_last:
        start += 1
    if end is None:
        end = len(links_list)
    start_download(start, end, links_list)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FitGirl Fast Scraper CLI")

    parser.add_argument("command", choices=["start_download", "resume_download", "set_path"])
    parser.add_argument("-s", "--start", default=0,
                        help="The index of the first link to download. 0 by default.")
    parser.add_argument("-e", "--end", default=None,
                        help="The index of the last link to download. Will go to the end by default.")
    parser.add_argument("-p", "--path", default="",
                        help="Set the path to save the files to")
    parser.add_argument("-sl", "--skip_last", action="store_true",
                        help="If True avoid re-downloading the last file. "
                             "If False re-download and overwrite it to ensure it has been well"
                             " downloaded and not corrupted.")

    args = parser.parse_args()

    if args.command == "start_download":
        start_download(args.start, args.end)
    elif args.command == "set_path":
        set_path(args.path)
    elif args.command == "resume_download":
        resume_download(args.skip_last, args.end)
