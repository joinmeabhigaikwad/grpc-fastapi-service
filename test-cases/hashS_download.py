import requests
import os
import zipfile
import gzip
import shutil

# URL to the FastAPI list files endpoint
list_files_url = "http://localhost:8101/files"

# Directory to save downloaded files
save_directory = "./downloaded_files"

# Specify the hash to filter files
target_hash = "123431234"  # Replace with the actual hash you want to filter by

# Ensure the save directory exists
os.makedirs(save_directory, exist_ok=True)

# Fetch the list of files
response = requests.get(list_files_url)
if response.status_code == 200:
    files = response.json().get("files", [])
    # Filter files by the hash
    matching_files = [file_name for file_name in files if target_hash in file_name]

    if matching_files:
        for file_name in matching_files:
            download_url = f"http://localhost:8101/document_store_download/{file_name}"
            file_response = requests.get(download_url)

            if file_response.status_code == 200:
                save_path = os.path.join(save_directory, file_name)

                # Save the file first
                with open(save_path, 'wb') as file:
                    file.write(file_response.content)
                print(f"File '{file_name}' downloaded successfully and saved to {save_path}")

                # Check if the file is a zip file and unzip it
                if file_name.endswith('.zip'):
                    try:
                        with zipfile.ZipFile(save_path, 'r') as zip_ref:
                            # Create a directory for unzipped content
                            unzip_dir = os.path.join(save_directory, file_name.replace('.zip', ''))
                            os.makedirs(unzip_dir, exist_ok=True)
                            # Extract all contents
                            zip_ref.extractall(unzip_dir)
                            print(f"File '{file_name}' unzipped successfully to {unzip_dir}")
                        # Optionally, remove the zip file after extraction
                        os.remove(save_path)
                    except zipfile.BadZipFile:
                        print(f"Failed to unzip '{file_name}'. It may not be a valid zip file.")

                # Check if the file is a gz file and decompress it
                elif file_name.endswith('.gz'):
                    try:
                        decompressed_path = os.path.join(save_directory, file_name.replace('.gz', ''))
                        with gzip.open(save_path, 'rb') as gz_file:
                            with open(decompressed_path, 'wb') as decompressed_file:
                                shutil.copyfileobj(gz_file, decompressed_file)
                        print(f"File '{file_name}' decompressed successfully to {decompressed_path}")
                        # Optionally, remove the gz file after decompression
                        os.remove(save_path)
                    except OSError:
                        print(f"Failed to decompress '{file_name}'. It may not be a valid gz file.")
            else:
                print(f"Failed to download file '{file_name}'. Status code: {file_response.status_code}")
    else:
        print(f"No files found with hash '{target_hash}'.")
else:
    print(f"Failed to fetch file list. Status code: {response.status_code}")
