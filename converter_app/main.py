"""
Simple service for USD => RUB converting

curl http://localhost:8009
{
    "success": false,
    "error": {
        "code": 0,
        "status": 405,
        "name": "Method Not Allowed",
        "message": "GET method is not allowed"
    }
}

curl --data '{"usd": 300.00}' --header 'Content-Type: application/json'
                                                        http://localhost:8009

{
    "success": true,
    "data": {
        "requested currency": "usd",
        "result currency": "rub",
        "exchange rate": 66.4437,
        "requested value": 300.00,
        "result value": 19933.11
    }
}

Currency source: https://www.cbr-xml-daily.ru/daily_json.js

"""

import json
import logging
import socket
import urllib.error
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Union, Dict

from converter_app.errors import ERRORS

HOST = ''
PORT = 8009
CURRENCY_SERVICE = 'https://www.cbr-xml-daily.ru/daily_json.js'

logger = logging.getLogger("ConverterApp")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)


class ConverterHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()
        return

    def do_GET(self):
        self._set_headers()
        response = self.return_error(code=0)
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return

    def do_POST(self):
        if self.headers.get_content_type() != 'application/json':
            self._set_headers()
            response = self.return_error(code=1)
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return

        length = int(self.headers['content-length'])
        try:
            message = json.loads(self.rfile.read(length))
        except json.decoder.JSONDecodeError:
            self._set_headers()
            response = self.return_error(code=2)
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return

        check_params_result = self.check_params(message)
        if check_params_result["correct"]:
            exchange_rate = self.get_exchange_rate()
            if exchange_rate != None:
                response = {"success": True,
                            "data": self.get_data(message, exchange_rate)}
                self._set_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                log_msg = f"{self.client_address[0]} - 200 - " \
                          f"USD {message['usd']} => " \
                          f"RUB {response['data']['result value']}"
                logger.info(log_msg)
                return
            else:
                self._set_headers()
                response = self.return_error(code=5)
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return

        else:
            error_code = check_params_result["code"]
            self._set_headers()
            response = self.return_error(code=error_code)
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return

    def get_data(self, message, exchange_rate):
        """
        Return data section for json response
        {
            "requested currency": "usd",
            "result currency": "rub",
            "exchange rate": 66.4437,
            "requested value": 300.00,
            "result value": 19933.11
        }
        :param message:
        :param exchange_rate:
        :return: data: dict
        """
        data = {
            "requested currency": "usd",
            "result currency": "rub",
            "exchange rate": exchange_rate,
            "requested value": message["usd"],
            "result value": round(exchange_rate * message['usd'], 2)
        }
        return data

    def return_error(self, code: int) -> dict:
        """
        Return error msg in dict and write log message to logger
        {
            "success": false,
            "data": {
                "code": 0,
                "name": "Method Not Allowed",
                "message": "GET method is not allowed"
                "status": 405,
            }
        }
        :param code: int in range (0, 6)
        :return: response: dict
        """
        response = {"success": False, "error": ERRORS[code]}
        log_msg = f"{self.client_address[0]} - {code} - " \
                  f"{ERRORS[code]['message']}"
        logger.info(log_msg)
        return response

    def check_params(self, data) -> dict:
        """
        Check if request parameters are correct and return correct = True
        otherwise correct = False and error code
        :param data:
        :return: dict
        """
        if not isinstance(data, Dict) or 'usd' not in data:
            return {"correct": False, "code": 3}
        if not isinstance(data['usd'], (float, int)):
            return {"correct": False, "code": 4}
        return {"correct": True}

    def get_exchange_rate(self) -> Union[float, int, None]:
        """
        Send request to exchange rate service and return current exchange rate
        if service is available otherwise None
        :return: float, int, None
        """
        try:
            response = urllib.request.urlopen(CURRENCY_SERVICE)
            if response.code == 200:
                response = json.loads(response.read().decode('utf-8'))
                exchange_rate = response["Valute"]["USD"]["Value"]
                return exchange_rate

            else:
                logger.warning(f"{response.code} from exchange rate service")
                return

        except urllib.error.HTTPError:
            logger.error("Incorrect address for exchange rate service")
            return

    # kill default logging
    def log_message(self, format, *args):
        pass


def run(server_class=HTTPServer, handler_class=ConverterHandler,
        addr=HOST, port=PORT):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)
    host_name = socket.gethostname()
    ipaddress = socket.gethostbyname_ex(host_name)[2][0]
    logger.info(f"Starting server on {ipaddress}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
