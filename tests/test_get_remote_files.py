import unittest
from unittest.mock import MagicMock, patch
from fileIntegritySync import get_remote_files


class TestGetRemoteFiles(unittest.TestCase):
    @patch('paramiko.SSHClient')
    def test_get_remote_files(self, mock_ssh_client):
        # Mock the SSHClient and its methods
        mock_exec_command = MagicMock()
        mock_ssh_client.return_value = MagicMock(
            exec_command=mock_exec_command)

        # Mock the response of exec_command for 'find' and 'stat' commands
        mock_exec_command.side_effect = [
            (None, MagicMock(read=MagicMock(
                return_value=b'/remote_dir/file1.txt\n/remote_dir/file2.txt')), None),
            (None, MagicMock(read=MagicMock(return_value=b'100')), None),
            (None, MagicMock(read=MagicMock(return_value=b'200')), None)
        ]

        # Instantiate the SSHClient
        ssh_client = mock_ssh_client()

        # Call the function
        remote_files = get_remote_files(ssh_client, '/remote_dir')

        # Assertions to check if the remote files and sizes are correctly retrieved
        expected_files = {
            '/remote_dir/file1.txt': 100,
            '/remote_dir/file2.txt': 200
        }
        self.assertEqual(remote_files, expected_files)

    @patch('paramiko.SSHClient')
    def test_get_remote_files_ssh_error(self, mock_ssh_client):
        # Mock the SSHClient to raise an exception on connect
        mock_ssh_client.return_value = MagicMock(
            exec_command=MagicMock(side_effect=Exception("SSH Error"))
        )

        # Instantiate the SSHClient
        ssh_client = mock_ssh_client()

        # Call the function and assert an exception is raised
        with self.assertRaises(Exception) as context:
            get_remote_files(ssh_client, '/remote_dir')

        self.assertTrue('SSH Error' in str(context.exception))

# More tests would be added here for different scenarios.


if __name__ == '__main__':
    unittest.main()
