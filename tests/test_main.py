import unittest
from unittest.mock import patch, MagicMock, mock_open
from fileIntegritySync import main


class TestMainFunction(unittest.TestCase):
    @patch('builtins.input', side_effect=['all'])
    @patch('fileIntegritySync.download_file')
    @patch('fileIntegritySync.compare_files', return_value={'file1.txt': (100, 200, '/remote_dir/file1.txt')})
    @patch('fileIntegritySync.get_remote_files', return_value={'file1.txt': {'size': 200, 'path': '/remote_dir/file1.txt'}})
    @patch('fileIntegritySync.get_local_files', return_value=[('/local_dir/file1.txt', 100)])
    @patch('paramiko.SSHClient')
    def test_main_all_files_download(self, mock_ssh_client, mock_get_local_files, mock_get_remote_files, mock_compare_files, mock_download_file, mock_input):
        # Mock the SSHClient and its methods
        mock_ssh_client.return_value = MagicMock()

        # Mock the configuration file opening
        with patch('builtins.open', mock_open(read_data='hostname: localhost\nusername: user\nssh_key_path: /path/to/key')):
            # Call the main function
            main()

            # Assert that the download_file function was called
            mock_download_file.assert_called_once()

    # More tests would be added here for different user inputs and scenarios.


if __name__ == '__main__':
    unittest.main()
