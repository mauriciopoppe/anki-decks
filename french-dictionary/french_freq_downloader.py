import urllib.request
import urllib.error
import os

DATA_URL = "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/fr/fr_50k.txt"
OUTPUT_FILE = "french-dictionary/fr_50k.txt"

def download_frequency_data(url=DATA_URL, output_path=OUTPUT_FILE):
    """
    Downloads French word frequency data from HermitDave's FrequencyWords repository.
    The data is based on OpenSubtitles 2018.
    """
    if os.path.exists(output_path):
        print(f"File {output_path} already exists. Skipping download.")
        return

    print(f"Downloading frequency data from {url}...")
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response, open(output_path, 'wb') as f:
            while True:
                chunk = response.read(8192)
                if not chunk:
                    break
                f.write(chunk)
        print(f"Successfully downloaded to {output_path}")
    except urllib.error.URLError as e:
        print(f"Failed to download frequency data: {e}")

if __name__ == "__main__":
    download_frequency_data()