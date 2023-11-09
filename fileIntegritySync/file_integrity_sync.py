"""This module synchronizes files based on size differences."""

import os
import json
import argparse
import logging
import concurrent.futures
from tqdm import tqdm
import paramiko

# Set up detailed logging for Paramiko
paramiko.sftp_file.SFTPFile.MAX_REQUEST_SIZE = pow(2, 22)
paramiko.util.log_to_file('paramiko.log')

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration from a JSON file
script_dir = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_dir, 'config.json')
with open(config_path, 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)

# Set up command-line argument parsing
parser = argparse.ArgumentParser(
    description='Synchronize files based on size differences.')
parser.add_argument('--local-path', help='Local directory path',
                    required=True)
parser.add_argument('--remote-path', help='Remote directory path',
                    required=True)
args = parser.parse_args()


def get_local_files(local_path):
    """Function to get local files and their sizes."""
    for root, _, files in os.walk(local_path):
        for name in files:
            file_path = os.path.join(root, name)
            yield file_path, os.path.getsize(file_path)


def get_remote_files(ssh_client, remote_path, local_filenames):
    """Function to get remote files and their sizes using SSH."""
    file_sizes = {}
    for filename in local_filenames:
        # Escape single quotes for use in the shell command
        escaped_filename = filename.replace("'", "'\\''")
        find_command = (
            f"find {remote_path} -type f -name '{escaped_filename}'"
        )
        logging.info("Executing remote find command for %s", filename)
        _, stdout, _ = ssh_client.exec_command(find_command)
        result = stdout.read().splitlines()
        if result:
            remote_file_path = result[0].decode()
            stat_command = f"stat -c %s '{remote_file_path}'"
            _, stdout, _ = ssh_client.exec_command(stat_command)
            file_sizes[filename] = {
                'size': int(stdout.read().strip()),
                'path': remote_file_path
            }
    return file_sizes


def compare_files(local_files, remote_files):
    """Function to compare local and remote files."""
    diff_files = {}
    for local_path, local_size in local_files:
        filename = os.path.basename(local_path)
        remote_file = remote_files.get(filename)
        if remote_file and local_size != remote_file['size']:
            diff_files[filename] = (
                local_size, remote_file['size'], remote_file['path']
            )
    return diff_files


def download_file(sftp_client, local_file, remote_file):
    """Function to download files from remote."""
    sftp_client.get(remote_file, local_file)
    logging.info("Downloaded %s to %s", remote_file, local_file)


def main():
    """Main function."""
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
        local_filenames = [os.path.basename(f[0]) for f in local_files]
        remote_files = get_remote_files(ssh_client, remote_path,
                                        local_filenames)

        # Compare files
        diff_files = compare_files(local_files, remote_files)
        if diff_files:
            logging.info("Files with different sizes:")
            for index, (filename, file_details) in enumerate(
                    diff_files.items(), start=1):
                logging.info(
                    "%d. %s - Local size: %d bytes, Remote size: %d bytes",
                    index, filename, file_details[0], file_details[1]
                )

            # Ask user for action
            files_to_download = []
            while True:
                user_input = input("Enter the numbers of the files you want "
                                   "to download (e.g., 1-5,6-10), or 'all' to "
                                   "download all files: ")
                if user_input.lower() == 'all':
                    files_to_download = [
                        (os.path.join(local_path, filename), file_details[2])
                        for filename, file_details in diff_files.items()
                    ]
                    break
                else:
                    try:
                        ranges = [range_str.split('-')
                                  for range_str in user_input.split(',')]
                        for range_str in ranges:
                            if len(range_str) == 1:
                                index = int(range_str[0]) - 1
                                filename, file_details = list(
                                    diff_files.items())[index]
                                files_to_download.append(
                                    (os.path.join(local_path, filename),
                                     file_details[2]))
                            else:
                                start, end = map(int, range_str)
                                files_to_download.extend(
                                    [(os.path.join(local_path, filename),
                                      file_details[2])
                                     for filename, file_details
                                     in list(diff_files.items())
                                     [start-1:end]]
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

    except paramiko.SSHException as ssh_exc:
        logging.error("SSH error occurred: %s", ssh_exc)
    except Exception as exc:
        logging.error("An error occurred: %s", exc)
    finally:
        if 'sftp_client' in locals():
            sftp_client.close()
        if 'ssh_client' in locals():
            ssh_client.close()


if __name__ == '__main__':
    main()
