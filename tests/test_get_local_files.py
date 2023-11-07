import unittest
from unittest.mock import patch
from fileIntegritySync import get_local_files
import os


class TestGetLocalFiles(unittest.TestCase):
    @patch('os.walk')
    def test_get_local_files_non_empty_directory(self, mock_walk):
        # Mock the os.walk to simulate a directory with files
        mock_walk.return_value = [
            ('/fake_dir', ('subdir',), ('file1.txt', 'file2.txt')),
            ('/fake_dir/subdir', (), ('file3.txt',)),
        ]

        # Mock os.path.getsize to return a fixed file size
        with patch('os.path.getsize') as mock_getsize:
            mock_getsize.return_value = 100

            # Call the function and collect results
            files = list(get_local_files('/fake_dir'))

            # Assert that we have the correct number of files
            self.assertEqual(len(files), 3)

            # Assert that we have the correct file paths and sizes
            expected_files = [
                ('/fake_dir/file1.txt', 100),
                ('/fake_dir/file2.txt', 100),
                ('/fake_dir/subdir/file3.txt', 100),
            ]
            self.assertEqual(files, expected_files)

    @patch('os.walk')
    def test_get_local_files_empty_directory(self, mock_walk):
        # Mock the os.walk to simulate an empty directory
        mock_walk.return_value = []

        # Call the function and collect results
        files = list(get_local_files('/fake_dir'))

        # Assert that we have no files
        self.assertEqual(len(files), 0)

# More tests would be added here for symbolic links, etc.


if __name__ == '__main__':
    unittest.main()
