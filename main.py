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


def start_download(start=0, end=None):
    assert os.stat("./conf.txt").st_size > 0, "No destination folder set"
    start = int(start)
    if start > 0:
        start -= 1
    if end is not None:
        end = int(end)
        assert end >= 0, "The end value cannot be negative"
        assert end >= start, "The end value cannot lower to the start one"
    assert start >= 0, "The start value cannot be negative"

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FitGirl Fast Scraper CLI")

    parser.add_argument("command", choices=["start_download", "set_path"], help="Choose an action")
    parser.add_argument("--start", default=0, help="Used to start downloading at a specific index")
    parser.add_argument("--end", default=None, help="Used to stop downloading at a specific index")
    parser.add_argument("--path", default="", help="Set the path to save the files to")

    args = parser.parse_args()

    if args.command == "start_download":
        start_download(args.start, args.end)
    elif args.command == "set_path":
        set_path(args.path)
