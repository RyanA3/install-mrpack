# Created by RyanA3
# Use at your own risk
# Provided with NO WARRANTY

import os
import platform
from pathlib import Path
import json
import requests
from zipfile import ZipFile
import shutil

def linux():
    return platform.system().lower() == 'linux'
def microbesoft():
    return platform.system().lower() == 'windows'
def thievesos():
    return platform.system().lower() == 'darwin'

def downloadFile(url, path):
    with requests.get(url, stream=True) as request:
        request.raise_for_status()
        with open(path, 'wb') as file:
            for chunk in request.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)

def tryDownloadFile(url, path):
    try:
        downloadFile(url, path)
        return True
    except Exception as error:
        print(error)
        return False

VERSION = '0.0.1'

LICENSE = '''1. USE AT YOUR OWN RISK.\n2. MODIFY COPY & REDISTRIBUTE THIS SOURCE CODE AS YOU WISH.\n3. I AM NOT LIABLE FOR ANY DAMAGES TO YOUR COMPUTER'''
print(LICENSE)

GREETING = '\n\n---\ndownload-mrpack v{}\n---\n'.format(VERSION)
print(GREETING)

# Get environment variables
HOME_PATH = str(Path.home())

# Setup defaults
DEFAULT_INSTALL_PATH = '{}/.minecraft'.format(HOME_PATH)
DEFAULT_DOWNLOADS_PATH = '{}/Downloads'.format(HOME_PATH)
USE_CACHE = True
REQUIRE_CONFIRMATIONS = True

def doConfirm(message = 'Are you ABSOLUTELY SURE? (y/N): ', defaultValue = 'N', successValue = 'y'):
    return not REQUIRE_CONFIRMATIONS or (input(message) or defaultValue) == successValue

# Get required values to run
INSTALL_PATH = str(input('Select installation path (your root game folder) ({}): '.format(DEFAULT_INSTALL_PATH)).strip() or DEFAULT_INSTALL_PATH)
DOWNLOADS_PATH = str(input('Select downloads folder ({}): '.format(DEFAULT_DOWNLOADS_PATH)).strip() or DEFAULT_DOWNLOADS_PATH)
MRPACK_DOWNLOAD_URL = str(input('Select url to download mrpack: '))
MRPACK_DOWNLOAD_PATH = '{}/modpack.mrpack'.format(DOWNLOADS_PATH)
UNPACKED_PATH = '{}/modpack'.format(DOWNLOADS_PATH)
UNPACKED_INDEX_PATH = '{}/modrinth.index.json'.format(UNPACKED_PATH)
UNPACKED_OVERRIDES_PATH = '{}/overrides'.format(UNPACKED_PATH)

# Download the file
downloadFile(MRPACK_DOWNLOAD_URL, MRPACK_DOWNLOAD_PATH)

# Extract the file
os.system('mkdir {}'.format(UNPACKED_PATH))
with ZipFile(MRPACK_DOWNLOAD_PATH, 'r') as mrpack:
    mrpack.extractall(UNPACKED_PATH)

# Load the index
pack_index_file = open(UNPACKED_INDEX_PATH, 'r')
pack_index = json.loads(pack_index_file.read())
pack_index_file.close()

# Print header info
num_mods = len(pack_index['files'])
files = [file for file in pack_index['files']]
filesize = sum([int(file['fileSize']) for file in pack_index['files']])
input('Installing {} mods @ est filesize of {} bytes, press ENTER to continue'.format(num_mods, filesize))

# Attempt to install a mod from a json object
def tryDownloadMod(file):
    relative_path = file['path']
    hashes = file['hashes']
    downloads = file['downloads']

    file['nice_name'] = relative_path.split('/')[-1]

    download_path = os.path.join(INSTALL_PATH, relative_path) 
    result = False

    if not USE_CACHE or not os.path.isfile(download_path):
        print('Installing {}...'.format(download_path))
        for download in downloads:
            print('from {}...'.format(download))
            result = tryDownloadFile(download, download_path)
            if result:
                break
    else:
        print('Already installed {}'.format(download_path))
        result = True

    return result

# Install the mods
failed = []
for file in files:
    result = tryDownloadMod(file)
    
    if not result:
        print('Failed to install {}'.format(file['nice_name']))
        failed.append(file)

# Print installation status
print('Successfully downloaded {} mods'.format(num_mods - len(failed)))
print('Failed mods: {}'.format([file['nice_name'] for file in failed]))

# Copy overrides into game folder
print('Copying overrides...')
for item_name in os.listdir(UNPACKED_OVERRIDES_PATH):
    item_path = os.path.join(UNPACKED_OVERRIDES_PATH, item_name)
    if not os.path.isdir(item_path):
        continue

    source_folder_path = item_path
    dest_folder_path = os.path.join(INSTALL_PATH, item_name)

    print('Copying {} into {}...'.format(source_folder_path, dest_folder_path))
    confirm = doConfirm()
    if not confirm:
        print('Cancelled copy operation')
        continue

    shutil.copytree(source_folder_path, dest_folder_path, dirs_exist_ok=True)
        
print('Done')
