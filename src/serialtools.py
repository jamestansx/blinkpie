import logging
from typing import Any
import json

from requests import get, post
from requests.packages import urllib3
from serial import Serial
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)

logging.basicConfig(
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger()


def genUUID():
    from uuid import uuid4

    return uuid4().hex


def do_read(port: Serial) -> str:
    while True:
        read_data = port.readline().decode().strip(" \r\n\b")
        if read_data == "":
            continue
        logger.debug("Read: %s", read_data)
        return read_data


def do_write(port: Serial, write_data: str):
    port.write(f"{write_data}\r\n".encode())
    logger.debug("Write: %s", write_data)


def parse_data(string) -> bool:
    string = json.loads(string.strip(" \r\t\n$0"))
    if isinstance(string[next(iter(string))], dict):
        return False  # GET
    return True  # POST


def do_get(server: str, params: dict = None):
    get_data = get(server, verify=False, params=params)
    logger.debug("GET data: %s", get_data.text)
    return get_data


def do_post(server: str, post_data: dict[str, Any]):
    logger.debug("POST: %s", post_data)
    return post(server, verify=False, json=post_data)
