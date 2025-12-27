import os
import zipfile

BUILD_DIR = os.path.join(os.path.dirname(__file__), "yomitan_build")
OUTPUT_ZIP = os.path.join(os.path.dirname(__file__), "french_frequency_dictionary.zip")

def package_dictionary():
    if not os.path.exists(BUILD_DIR):
        print(f"Error: {BUILD_DIR} does not exist.")
        return

    print(f"Packaging {BUILD_DIR} into {OUTPUT_ZIP}...")
    
    with zipfile.ZipFile(OUTPUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(BUILD_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, BUILD_DIR)
                zipf.write(file_path, arcname)
                
    print(f"Successfully created {OUTPUT_ZIP}")

if __name__ == "__main__":
    package_dictionary()
