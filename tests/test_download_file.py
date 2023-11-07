import unittest
from unittest.mock import patch, MagicMock
from fileIntegritySync import download_file


class TestDownloadFile(unittest.TestCase):
    @patch('paramiko.SFTPClient')
    def test_download_file_success(self, mock_sftp_client):
        # Mock the SFTPClient and its methods
        mock_sftp_client.return_value = MagicMock(get=MagicMock())

        # Instantiate the SFTPClient
        sftp_client = mock_sftp_client()

        # Call the function
        download_file(sftp_client, '/local_dir/file1.txt',
                      '/remote_dir/file1.txt')

        # Assert that the get method was called with the correct arguments
        sftp_client.get.assert_called_once_with(
            '/remote_dir/file1.txt', '/local_dir/file1.txt')

    @patch('paramiko.SFTPClient')
    def test_download_file_failure(self, mock_sftp_client):
        # Mock the SFTPClient to raise an IOError on file download
        mock_sftp_client.return_value = MagicMock(
            get=MagicMock(side_effect=IOError("Failed to download")))

        # Instantiate the SFTPClient
        sftp_client = mock_sftp_client()

        # Call the function and assert an exception is raised
        with self.assertRaises(IOError) as context:
            download_file(sftp_client, '/local_dir/file1.txt',
                          '/remote_dir/file1.txt')

        self.assertTrue('Failed to download' in str(context.exception))

# More tests would be added here for different scenarios.


if __name__ == '__main__':
    unittest.main()
