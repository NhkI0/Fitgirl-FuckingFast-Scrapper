import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import os


def extract_download_link(script_content):
    # Pattern to match window.open with a direct URL
    scriptPattern = r'window\.open\("(https://[^"]+)"'
    scriptMatch = re.search(scriptPattern, script_content)

    if scriptMatch:
        return scriptMatch.group(1)
    return None

def get_download_link_from_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    for script in soup.find_all('script'):
        if script.string:
            link = extract_download_link(script.string)
            if link:
                return link
    return None

def download_with_requests(url, save_path):
    """
    Download a file using the requests library with progress tracking
    and error handling.

    Args:
        url (str): URL of the file to download
        save_path (str): Local path where the file should be saved
    """
    try:
        # Send a GET request with stream=True to handle large files
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Get the total file size if available
        total_size = int(response.headers.get('content-length', 0))

        # Create directory if it doesn't exist
        Path(os.path.dirname(save_path)).mkdir(parents=True, exist_ok=True)

        # Open the local file to write the downloaded content
        with open(save_path, 'wb') as file:
            if total_size == 0:
                file.write(response.content)
            else:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        # Calculate download progress
                        progress = (downloaded / total_size) * 100
                        print(f"\rDownload Progress: {progress:.1f}%", end="")
        print("\nDownload completed!")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return False
    except IOError as e:
        print(f"Error saving file: {e}")
        return False
    return True


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