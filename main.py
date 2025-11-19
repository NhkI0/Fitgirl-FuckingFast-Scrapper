import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
import time
import argparse
import re
import download
from typing import Optional, List


def chrome_connect(hl: bool) -> WebDriver:
    """
    Initialize and return a Chrome WebDriver instance.

    Args:
        hl: If True, run browser in headless mode

    Returns:
        WebDriver: Configured Chrome WebDriver instance
    """
    chrome_options: Options = Options()
    if hl:
        chrome_options.add_argument('--headless=new')
    driver: WebDriver = webdriver.Chrome(options=chrome_options)
    return driver


def set_links(start_url: str, hl: bool) -> None:
    """
    Navigate to FitGirl REPACK page and extract FuckingFast download links.

    Args:
        start_url: The FitGirl repacks URL to scrape
        hl: If True, run browser in headless mode
    """
    target_link_text: str = "Filehoster: FuckingFast"
    driver: WebDriver = chrome_connect(hl)
    try:
        print(f"Navigating to {start_url}")
        driver.get(start_url)
        time.sleep(1)

        link_element = driver.find_element(By.LINK_TEXT, target_link_text)
        print(f"Found link: {target_link_text}")
        link_url: str = link_element.get_attribute('href')
        driver.get(link_url)
        time.sleep(1)

        print(f"New page URL: {driver.current_url}\n")

        # Pattern to validate links
        link_pattern: str = r"^https://fuckingfast\.co/\S+"

        with open("./links.txt", "w") as f:
            # Check if current URL is a single fuckingfast link
            if re.match(link_pattern, driver.current_url):
                print(f"1: {driver.current_url}")
                f.write(driver.current_url + "\n")
            else:
                # Multiple links in plaintext div
                div = driver.find_element(By.ID, 'plaintext')
                links: List[str] = div.text.split('\n')

                for link in links:
                    link = link.strip()  # Remove whitespace
                    # Only write if it matches the pattern
                    if re.match(link_pattern, link):
                        f.write(link + "\n")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()
        print("\nBrowser is now closed\n")
        show_links()


def show_links() -> None:
    """
    Display all links found in the links.txt file.
    """
    try:
        with open("./links.txt", "r") as f:
            links: List[str] = f.readlines()

        if not links:
            print("=== NO LINKS FOUND IN FILE ===")
            return

        print(f"=== FOUND {len(links)} LINK{"S" if len(links) >= 2 else ""} ===\n")
        for i, link in enumerate(links, start=1):
            print(f"{i}: {link}", end="")
        print(f"\n=== END OF LINKS ===\n")

    except FileNotFoundError:
        print("Error: links.txt file not found")
    except Exception as e:
        print(f"Error: {e}")


def set_path(path: str) -> None:
    """
    Set the destination folder path for downloads.

    Args:
        path: The directory path where files should be saved
    """
    with open("./conf.txt", 'w') as file:
        file.write(path)


def start_download(
        start: int = 0,
        end: Optional[int] = None,
        url: Optional[str] = None,
        hl: Optional[bool] = None,
        links_list: Optional[List[str]] = None
) -> None:
    """
    Start download of the given links in the given directory.

    Args:
        start: The index of the first link to download (1-indexed, default 0)
        end: The index of the last link to download (goes to end by default)
        url: Optional FitGirl URL to scrape links from
        hl: If True, run browser in headless mode
        links_list: Pre-loaded list of links (if None, will read from file)
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
        set_links(url, hl if hl is not None else False)

    # We don't read again the links if we've already done it before
    if links_list is None:
        links_list = get_links()
    assert start <= len(links_list), \
        f"The start index {start + 1} is out of range\nMaximum possible index is {len(links_list)}"

    # We get the download path from the file
    with open("./conf.txt", "r") as file:
        save_path_base: str = file.read()

    if end is None or end > len(links_list):
        end = len(links_list)

    # Calculate download range
    total_files: int = end - start
    completed: int = 0
    failed: int = 0

    # Display download information header
    print("\n" + "=" * 80)
    print(f"{'DOWNLOAD SESSION':^80}")
    print("=" * 80)
    print(f"Total links available: {len(links_list)}")
    print(f"Download range: {start + 1} → {end}")
    print(f"Files to download: {total_files}")
    print(f"Destination: {save_path_base}")
    print("=" * 80 + "\n")

    for i in range(start, end):
        save_path: str = save_path_base
        pattern: str = r"#(.*)$"
        match: Optional[re.Match] = re.search(pattern, links_list[i])

        if match:
            filename: str = match.group(1)[1:] if match.group(1)[0] == "#" else match.group(1)
            save_path = save_path + f"\\{filename}"

            # Display current download info
            print("─" * 80)
            print(f"📦 [{i + 1}/{len(links_list)}] Downloading...")
            print(f"File: {filename}")
            print("─" * 80)

            download_url: Optional[str] = download.get_download_link_from_page(links_list[i])
            success: bool = download.download_with_requests(download_url, save_path)

            if success:
                completed += 1
                print(f"✓ Saved to: {save_path}")
                print(f"✓ Progress: {completed}/{total_files} files completed\n")
            else:
                failed += 1
                print(f"✗ Failed to download")
                print(f"✗ Progress: {completed}/{total_files} completed, {failed} failed\n")
        else:
            failed += 1
            print(f"[{i + 1}/{len(links_list)}] ✗ Couldn't find the name of the file\n")

    # Final summary
    print("\n" + "=" * 80)
    print(f"{'DOWNLOAD COMPLETE':^80}")
    print("=" * 80)
    print(f"✓ Successfully downloaded: {completed}/{total_files}")
    if failed > 0:
        print(f"✗ Failed downloads: {failed}/{total_files}")
    print(f"Range completed: {start + 1} → {end}")
    print("=" * 80 + "\n")


def get_links() -> List[str]:
    """
    Read and parse links from the links.txt file.

    Returns:
        List of valid FuckingFast URLs
    """
    links_list: List[str] = []
    with open("./links.txt", "r") as file:
        links: List[str] = file.readlines()

    pattern: str = r"(https:\/\/fuckingfast\.co\/\S+)"
    found: bool = False
    is_empty: bool = True

    for line in links:
        is_empty = False
        match: Optional[re.Match] = re.search(pattern, line)
        if match:
            found = True
            links_list.append(match.group(1))

    if is_empty:
        print("The given file is empty")
    elif not found:
        print("No links were found inside the file")

    return links_list


def resume_download(skip_last: bool, end: Optional[int]) -> None:
    """
    Resume the download of the given links in the given directory.

    Args:
        skip_last: If True, avoid re-downloading the last file.
                   If False, re-download and overwrite to ensure integrity.
        end: The index of the last link to download (goes to end by default)
    """
    links_list: List[str] = get_links()

    with open("./conf.txt", "r") as file:
        directory: str = file.read()

    start: int = len([name for name in os.listdir(directory)
                      if os.path.isfile(os.path.join(directory, name))])

    if skip_last:
        start += 1
    if end is None:
        end = len(links_list)

    start_download(start, end, None, None, links_list)


if __name__ == "__main__":
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="FitGirl Fast Scraper CLI"
    )

    parser.add_argument(
        "command",
        choices=["start_download", "resume_download", "set_path", "get_links", "show_links"]
    )
    parser.add_argument(
        "-s", "--start",
        default=0,
        help="The index of the first link to download. 0 by default."
    )
    parser.add_argument(
        "-e", "--end",
        default=None,
        help="The index of the last link to download. Will go to the end by default."
    )
    parser.add_argument(
        "-p", "--path",
        default="",
        help="Set the path to save the files to"
    )
    parser.add_argument(
        "-sl", "--skip_last",
        action="store_true",
        help="If True avoid re-downloading the last file. "
             "If False re-download and overwrite it to ensure it has been well downloaded and not corrupted."
    )
    parser.add_argument(
        "-u", "--url",
        help="Set the https://fitgirl-repacks.site link"
    )
    parser.add_argument(
        "-hl", "--headless",
        action="store_true",
        help="Use the browser headless mode"
    )

    args: argparse.Namespace = parser.parse_args()

    if args.command == "start_download":
        start_download(args.start, args.end, args.url, args.headless)
    elif args.command == "set_path":
        set_path(args.path)
    elif args.command == "resume_download":
        resume_download(args.skip_last, args.end)
    elif args.command == "get_links":
        set_links(args.url, args.headless)
    elif args.command == "show_links":
        show_links()
