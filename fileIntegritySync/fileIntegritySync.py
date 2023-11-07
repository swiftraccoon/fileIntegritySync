import os
import paramiko
import json
import argparse
import logging
import concurrent.futures
from tqdm import tqdm

# Initialize logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration from a JSON file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Set up command-line argument parsing
parser = argparse.ArgumentParser(
    description='Synchronize files based on size differences.')
parser.add_argument('--local-path', help='Local directory path',
                    required=True)
parser.add_argument(
    '--remote-path', help='Remote directory path', required=True)
args = parser.parse_args()


# Function to get local files and their sizes
def get_local_files(local_path):
    for root, dirs, files in os.walk(local_path):
        for name in files:
            file_path = os.path.join(root, name)
            yield file_path, os.path.getsize(file_path)


# Function to get remote files and their sizes using SSH
def get_remote_files(ssh_client, remote_path):
    stdin, stdout, stderr = ssh_client.exec_command(
        f'find {remote_path} -type f')
    file_paths = stdout.read().splitlines()
    file_sizes = {}
    for file_path in file_paths:
        stdin, stdout, stderr = ssh_client.exec_command(
            f'stat -c %s "{file_path.decode()}"')
        file_sizes[file_path.decode()] = int(stdout.read().strip())
    return file_sizes


# Function to compare local and remote files
def compare_files(local_files, remote_files):
    diff_files = {}
    for local_path, local_size in local_files:
        filename = os.path.basename(local_path)
        remote_file = remote_files.get(filename)
        if remote_file and local_size != remote_file['size']:
            diff_files[filename] = (
                local_size, remote_file['size'], remote_file['path'])
    return diff_files


# Function to download files from remote
def download_file(sftp_client, local_file, remote_file):
    sftp_client.get(remote_file, local_file)
    logging.info(f"Downloaded {remote_file} to {local_file}")


# Main function
def main():
    local_path = args.local_path
    remote_path = args.remote_path
    hostname = config['hostname']
    port = config.get('port', 22)
    username = config['username']
    ssh_key_path = config['ssh_key_path']

    # Establish SSH connection
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(hostname, port, username=username,
                           key_filename=ssh_key_path)
        sftp_client = ssh_client.open_sftp()

        # Get local and remote files
        local_files = list(get_local_files(local_path))
        remote_files = get_remote_files(ssh_client, remote_path)

        # Compare files
        diff_files = compare_files(local_files, remote_files)
        if diff_files:
            logging.info("Files with different sizes:")
            for index, (filename, (local_size, remote_size, remote_path)) \
                    in enumerate(diff_files.items(), start=1):
                logging.info(f"{index}. {filename} - Local size: "
                             f"{local_size} bytes, Remote size: "
                             f"{remote_size} bytes")

            # Ask user for action
            files_to_download = []
            while True:
                user_input = input("Enter the numbers of the files you want "
                                   "to download (e.g., 1-5,6-10), or 'all' to "
                                   "download all files: ")
                if user_input.lower() == 'all':
                    files_to_download = [
                        (os.path.join(local_path, filename), remote_path)
                        for filename, (_, _, remote_path)
                        in diff_files.items()
                    ]
                    break
                else:
                    try:
                        ranges = [range_str.split('-')
                                  for range_str in user_input.split(',')]
                        for range_str in ranges:
                            if len(range_str) == 1:
                                index = int(range_str[0]) - 1
                                filename, (_, _, remote_path) = list(
                                    diff_files.items())[index]
                                files_to_download.append(
                                    (os.path.join(local_path, filename),
                                     remote_path))
                            else:
                                start, end = map(int, range_str)
                                files_to_download.extend(
                                    [(os.path.join(local_path, filename),
                                      remote_path)
                                     for filename, (_, _, remote_path)
                                     in list(diff_files.items())[start-1:end]]
                                )
                        break
                    except (ValueError, IndexError):
                        logging.error("Invalid input. Please enter a valid "
                                      "range or 'all'.")

            # Download files with progress bar and concurrency
            with concurrent.futures.ThreadPoolExecutor(
                    max_workers=4) as executor:
                futures = [
                    executor.submit(download_file, sftp_client, local_file,
                                    remote_file)
                    for local_file, remote_file in files_to_download
                ]

                for future in tqdm(concurrent.futures.as_completed(futures),
                                   total=len(futures), desc="Downloading"):
                    future.result()  # Raises exceptions from download_file

            logging.info("Selected files have been downloaded.")
        else:
            logging.info("All files are synchronized in size.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        if 'sftp_client' in locals():
            sftp_client.close()
        if 'ssh_client' in locals():
            ssh_client.close()


if __name__ == '__main__':
    main()
