import os
import server_operation
import unittest
import tempfile


class AppTestCase(unittest.TestCase):

    def testSSH(self):
        server_operation.test_ssh()


if __name__ == '__main__':
    unittest.main()
