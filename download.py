import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import os
from tqdm import tqdm


def extract_download_link(script_content: str) -> str | None:
    # Pattern to match window.open with a direct URL
    script_pattern = r'window\.open\("(https://[^"]+)"'
    script_match = re.search(script_pattern, script_content)

    if script_match:
        return script_match.group(1)
    return None


def get_download_link_from_page(page_url: str) -> str | None:
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    for script in soup.find_all('script'):
        if script.string:
            link = extract_download_link(script.string)
            if link:
                return link
    return None


def download_with_requests(page_url: str, download_path: str) -> bool:
    """
    Download a file using the request library with progress tracking
    and error handling.

    Args:
        page_url (str): URL of the file to download
        download_path (str): Local path where the file should be saved
    """
    try:
        response = requests.get(page_url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))

        Path(os.path.dirname(download_path)).mkdir(parents=True, exist_ok=True)

        # Use tqdm for progress bar
        with open(download_path, 'wb') as file:
            with tqdm(total=total_size, unit='B', unit_scale=True,
                      unit_divisor=1024, desc="Downloading") as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        pbar.update(len(chunk))

        print("✓ Download completed!")
        return True

    except requests.exceptions.RequestException as e:
        print(f"✗ An error occurred: {e}")
        return False
    except IOError as e:
        print(f"✗ Error saving file: {e}")
        return False


# Example usage
if __name__ == "__main__":
    # Example URL and save path
    url = "https://fuckingfast.co/gmfdxt072jq5#FF7RI_--_fitgirl-repacks.site_--_.part017.rar"
    save_path = "C:/Users/eezle/Downloads"
    pattern = r"#(.*)$"
    match = re.search(pattern, url)
    if match:
        save_path = save_path+f"/{match.group(1)[1:]}"
        download_url = get_download_link_from_page(url)
        print(f"Starting download of {match.group(1)[1:]}")
        # Using requests (recommended for more features)
        success = download_with_requests(download_url, save_path)

        if success:
            print(f"File saved to: {save_path}")
    else:
        print("Couldn't find the name of the file")
