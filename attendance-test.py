import time
import requests
import urllib.parse
import unittest

def urljoin(scheme, netloc, path):
    return f'{scheme}://{netloc}/{path}'

class AttendanceTest(unittest.TestCase):
    SCHEME = 'https'
    NETLOC = 'umaru.work'
    PATH = 'face-io-web/attendance/in'

    def test_post_attendance_success(self):
        url = urljoin(AttendanceTest.SCHEME, AttendanceTest.NETLOC, AttendanceTest.PATH)
        unixtime = time.time()
        data = {'label': 1, 'date': unixtime}
        res = requests.post(url, data=data)

if __name__ == '__main__':
    unittest.main()