import unittest
from fileIntegritySync import compare_files


class TestCompareFiles(unittest.TestCase):
    def test_compare_files_with_differences(self):
        # Mock local and remote files with different sizes
        local_files = [
            ('/local_dir/file1.txt', 100),
            ('/local_dir/file2.txt', 200),
        ]
        remote_files = {
            'file1.txt': {'size': 100, 'path': '/remote_dir/file1.txt'},
            'file2.txt': {'size': 300, 'path': '/remote_dir/file2.txt'},
            'file3.txt': {'size': 150, 'path': '/remote_dir/file3.txt'},
        }

        # Call the function
        diff_files = compare_files(local_files, remote_files)

        # Assertions to check if the differences are correctly identified
        expected_diff = {
            'file2.txt': (200, 300, '/remote_dir/file2.txt')
        }
        self.assertEqual(diff_files, expected_diff)

    def test_compare_files_no_differences(self):
        # Mock local and remote files with no size differences
        local_files = [
            ('/local_dir/file1.txt', 100),
            ('/local_dir/file2.txt', 200),
        ]
        remote_files = {
            'file1.txt': {'size': 100, 'path': '/remote_dir/file1.txt'},
            'file2.txt': {'size': 200, 'path': '/remote_dir/file2.txt'},
        }

        # Call the function
        diff_files = compare_files(local_files, remote_files)

        # Assertions to check if no differences are found
        self.assertEqual(diff_files, {})

    def test_compare_files_missing_files(self):
        # Mock local files missing in remote and vice versa
        local_files = [
            ('/local_dir/file1.txt', 100),
        ]
        remote_files = {
            'file2.txt': {'size': 200, 'path': '/remote_dir/file2.txt'},
        }

        # Call the function
        diff_files = compare_files(local_files, remote_files)

        # Assertions to check if missing files are not considered as differences
        self.assertEqual(diff_files, {})

# More tests would be added here for different scenarios.


if __name__ == '__main__':
    unittest.main()
