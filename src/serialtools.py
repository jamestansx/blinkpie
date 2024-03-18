import json
import logging
from typing import Any
from uuid import uuid4

import requests
from requests.packages import urllib3
from serial import Serial
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)


class SerialTools:
    def __init__(self):
        logging.basicConfig(
            format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
            handlers=[logging.StreamHandler()],
        )
        self.logger = logging.requests.getLogger()

    def genUUID(self):
        return uuid4().hex

    def do_read(self, port: Serial) -> str:
        while True:
            read_data = port.readline().decode().strip(" \r\n\b")
            if not read_data:
                continue
            self.logger.debug("Read: %s", read_data)
            return read_data

    def do_write(self, port: Serial, write_data: str):
        port.write(f"{write_data}\r\n".encode())
        self.logger.debug("Write: %s", write_data)

    def parse_data(self, string) -> bool:
        string = json.loads(string.strip(" \r\t\n$0"))
        return False if isinstance(string[next(iter(string))], dict) else True

    def do_get(self, server: str, params: dict = None):
        get_data = requests.get(server, verify=False, params=params)
        self.logger.debug("GET data: %s", get_data.text)
        return get_data

    def do_post(self, server: str, post_data: dict[str, Any]):
        self.logger.debug("POST: %s", post_data)
        return requests.post(server, verify=False, json=post_data)
