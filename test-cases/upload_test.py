import os
import zipfile
import requests

# Directory containing folders to be zipped and uploaded
directory_path = "/home/abhishek/Desktop"

# URL for the upload endpoint
upload_url = "http://localhost:8101/document_store"

def zip_folder(folder_path, output_path):
    """
    Zips the contents of a folder.
    Args:
        folder_path (str): Path to the folder to be zipped.
        output_path (str): Path to save the zip file.
    """
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)
    print(f"Folder '{folder_path}' zipped to '{output_path}'")

def upload_file(file_path, upload_url):
    """
    Uploads a file to the given URL.
    Args:
        file_path (str): Path to the file to be uploaded.
        upload_url (str): URL of the upload endpoint.
    """
    file_name = os.path.basename(file_path)
    with open(file_path, 'rb') as f:
        files = {'files': (file_name, f)}
        response = requests.post(upload_url, files=files)
        if response.status_code == 200:
            print(f"File '{file_name}' uploaded successfully. Response: {response.json()}")
        else:
            print(f"Failed to upload file '{file_name}'. Status code: {response.status_code}, Response: {response.text}")

# Ensure the directory exists
if not os.path.exists(directory_path):
    print(f"Directory '{directory_path}' does not exist.")
else:
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        if os.path.isdir(item_path):  # Check if it's a directory
            zip_file_path = f"{item_path}.zip"
            zip_folder(item_path, zip_file_path)  # Zip the folder
            upload_file(zip_file_path, upload_url)  # Upload the zip file
            # Optionally, delete the zip file after upload
            os.remove(zip_file_path)
            print(f"Temporary zip file '{zip_file_path}' removed.")
        else:
            print(f"Skipping '{item_path}' as it is not a folder.")
