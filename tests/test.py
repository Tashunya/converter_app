import unittest
import time
import urllib.request
import threading
import json

from http.server import HTTPServer
from converter_app.main import ConverterHandler

server_address = ('', 8009)


class TestRequests(unittest.TestCase):

    def SetUp(self):
        server = HTTPServer(server_address, ConverterHandler)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.start()
        time.sleep(1)

    def test_head_request(self):
        request = \
            urllib.request.Request('http://localhost:8009', method='HEAD')
        response = urllib.request.urlopen(request)
        self.assertEqual(response.code, 200, 'Should be 200')
        self.assertEqual(response.getheader("Content-type"),
                         'application/json',
                         "Should be application/json")

        print('HEAD test passed.')

    def test_get_request(self):
        response = urllib.request.urlopen("http://localhost:8009")
        self.assertEqual(response.code, 200, 'Should be 200')
        response = json.loads(response.read().decode('utf-8'))
        self.assertEqual(response["success"], False, 'Unsuccessful Request')
        self.assertEqual(response["error"]["code"], 0, "Method Not Allowed")
        print('GET test passed.')

    def test_post_request(self):
        correct_request = urllib.request.\
            Request('http://localhost:8009',
                    method='POST',
                    headers={"Content-Type": "application/json"},
                    data=json.dumps({"usd": 300}).encode('utf-8'))
        response = urllib.request.urlopen(correct_request)

        self.assertEqual(response.code, 200, 'Should be 200')
        self.assertEqual(response.getheader("Content-type"),
                         'application/json',
                         "Should be application/json")
        response = json.loads(response.read().decode('utf-8'))
        self.assertEqual(response["success"], True, "Incorrect Request")
        self.assertEqual(response['data']['exchange rate'] != None, True)

        request = urllib.request.\
            Request('http://localhost:8009',
                    method='POST',
                    data=json.dumps({"usd": 300}).encode('utf-8'))
        response = urllib.request.urlopen(request)
        self.assertEqual(response.code, 200, 'Should be 200')
        self.assertEqual(response.getheader("Content-type"),
                         'application/json',
                         "Should be application/json")
        response = json.loads(response.read().decode('utf-8'))
        self.assertEqual(response["success"], False, "Should be False")
        self.assertEqual(response['error']['code'], 1, "Error code 1")

        request = urllib.request.\
            Request('http://localhost:8009',
                    method='POST',
                    headers={"Content-Type": "application/json"},
                    data=json.dumps({"rub": 300}).encode('utf-8'))
        response = urllib.request.urlopen(request)
        self.assertEqual(response.code, 200, 'Should be 200')
        response = json.loads(response.read().decode('utf-8'))
        self.assertEqual(response["success"], False, "Should be False")
        self.assertEqual(response['error']['code'], 3, "Error code 3")

        request = urllib.request.\
            Request('http://localhost:8009',
                    method='POST',
                    headers={"Content-Type": "application/json"},
                    data=json.dumps({"usd": "string"}).encode('utf-8'))
        response = urllib.request.urlopen(request)
        self.assertEqual(response.code, 200, 'Should be 200')
        response = json.loads(response.read().decode('utf-8'))
        self.assertEqual(response["success"], False, "Should be False")
        self.assertEqual(response['error']['code'], 4, "Error code 4")

        request = urllib.request.\
            Request('http://localhost:8009',
                    method='POST',
                    headers={"Content-Type": "application/json"},
                    data=("usd").encode('utf-8'))
        response = urllib.request.urlopen(request)
        self.assertEqual(response.code, 200, 'Should be 200')
        self.assertEqual(response.getheader("Content-type"),
                         'application/json',
                         "Should be application/json")
        response = json.loads(response.read().decode('utf-8'))
        self.assertEqual(response["success"], False, "Should be False")
        self.assertEqual(response['error']['code'], 2, "Error code 2")

        print("POST test passed")


if __name__ == '__main__':
    unittest.main()
