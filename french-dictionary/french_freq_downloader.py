import requests
import os

DATA_URL = "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/fr/fr_50k.txt"
OUTPUT_FILE = "french-dictionary/fr_50k.txt"

def download_frequency_data(url=DATA_URL, output_path=OUTPUT_FILE):
    """
    Downloads French word frequency data from HermitDave's FrequencyWords repository.
    The data is based on OpenSubtitles 2018.
    """
    # Ensure the directory exists (relative to script execution if not absolute)
    # But here output_path is just a filename, so it saves in CWD.
    
    if os.path.exists(output_path):
        print(f"File {output_path} already exists. Skipping download.")
        return

    print(f"Downloading frequency data from {url}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Successfully downloaded to {output_path}")

if __name__ == "__main__":
    download_frequency_data()
