# fileIntegritySync
[![Bandit](https://github.com/swiftraccoon/fileIntegritySync/actions/workflows/bandit.yml/badge.svg)](https://github.com/swiftraccoon/fileIntegritySync/actions/workflows/bandit.yml)[![CodeQL](https://github.com/swiftraccoon/fileIntegritySync/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/swiftraccoon/fileIntegritySync/actions/workflows/github-code-scanning/codeql)[![Pylint](https://github.com/swiftraccoon/fileIntegritySync/actions/workflows/pylint.yml/badge.svg)](https://github.com/swiftraccoon/fileIntegritySync/actions/workflows/pylint.yml)[![Python Tests](https://github.com/swiftraccoon/fileIntegritySync/actions/workflows/python-tests.yml/badge.svg)](https://github.com/swiftraccoon/fileIntegritySync/actions/workflows/python-tests.yml)

`fileIntegritySync` is a tool designed to synchronize files between a local and a remote directory, ensuring integrity by comparing file sizes and allowing for selective re-downloading of files.

## Features

- Recursively scans a local directory for files and their sizes.
- Compares local files with their remote counterparts on an SFTP server.
- Identifies files with mismatched sizes and presents them to the user.
- Offers the option to selectively download files from the remote server.
- Supports batch downloading based on user selection.

## Requirements

- Python 3.6 or higher
- Paramiko for SFTP operations
- PyTest for running tests (optional for development)

## Installation

Clone the repository to your local machine:

- `git clone https://github.com/swiftraccoon/fileIntegritySync.git`
- `cd fileIntegritySync`

Install the required dependencies:

- `pip install -r requirements.txt`

## Usage

Run the script with the following command:

- `python fileIntegritySync.py`

Follow the interactive prompts to specify local and remote directories for file synchronization.

## Configuration

Create a `config.json` file based on the `config.json.example` template with your server details.

## Contributing

Contributions are welcome!
