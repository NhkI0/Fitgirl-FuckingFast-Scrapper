import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import argparse
import re
import download


def chrome_connect(hl):
    chrome_options = Options()
    if hl:
        chrome_options.add_argument('--headless=new')
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def set_links(start_url, hl):
    target_link_text = "Filehoster: FuckingFast" # To locate the Filehoster link
    driver = chrome_connect(hl)
    try:
        # Navigate to the starting webpage
        print(f"Navigating to {start_url}")
        driver.get(start_url)

        # Wait for the page to load
        time.sleep(1)
        link_element = driver.find_element(By.LINK_TEXT, target_link_text)
        print(f"Found link: {target_link_text}")
        link_url = link_element.get_attribute('href')
        print(f"Clicked on link, now navigating to {link_url}")
        driver.get(link_url)
        # Wait for the page to load
        time.sleep(1)
        print(f"New page title: {driver.title}")
        print(f"Current URL: {driver.current_url}\n")

        div = driver.find_element(By.ID, 'plaintext')
        links = div.text.split('\n')
        f = open("./links.txt", "w")
        for link in links:
            print(link)
            f.write(link+"\n")
        f.close()
        print(f"Saved links to {f.name}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the browser
        driver.quit()
        print("\nBrowser is now closed\n")


def set_path(path):
    file = open("./conf.txt", 'w')
    file.write(path)
    file.close()


def start_download(start=0, end=None, url=None, hl=None,links_list=None):
    """
    Start download of the given links in the given directory.
    :param links_list:
    :param hl:
    :param url:
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

    if url is not None:
        set_links(url, hl)

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
    pattern = r"(https:\/\/fuckingfast\.co\/\S+)"
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
    dirt = file.read()
    file.close()
    start = len([name for name in os.listdir(dirt) if os.path.isfile(os.path.join(dirt, name))])
    if skip_last:
        start += 1
    if end is None:
        end = len(links_list)
    start_download(start, end, None, None, links_list)  # 2 None because of the other arguments


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FitGirl Fast Scraper CLI")

    parser.add_argument("command", choices=["start_download", "resume_download", "set_path", "get_links"])
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
    parser.add_argument("-u", "--url", help="Set the https://fitgirl-repacks.site link")
    parser.add_argument("-hl", "--headless", action="store_true", help="Use the browser headless mode")

    args = parser.parse_args()

    if args.command == "start_download":
        start_download(args.start, args.end, args.url, args.headless)
    elif args.command == "set_path":
        set_path(args.path)
    elif args.command == "resume_download":
        resume_download(args.skip_last, args.end)
    elif args.command == "get_links":
        set_links(args.url, args.headless)
