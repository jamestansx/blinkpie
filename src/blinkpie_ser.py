"""
POST
 FORMAT:
    data = { "data": { "parameter": "value" } }

    data = {
        "data":
            {
                "parameter": "value"
            }
    }
    notification = {
        "notification":
            {
                "title": "message"
            }
    }
    profile = {
        "profile":
            {
                "UUID": "uuid",
                "name": "hardwarename",
                "description": "description",
            }
    }
 STORAGE:
    "data": {
            "parameter1": "value",
            "parameter2": "value"
    }

    "notification": {
            "title1": "message",
            "title2": "message"
    }

    "profile": [
        {
            "UUID": "uuid1",
            "name": "hardwarename1",
            "description": "description1",
        },
        {
            "UUID": "uuid2",
            "name": "hardwarename2",
            "description": "description2",
        }
    ]

----------------------------------------------------------------
GET FORMAT:
    data = {"data" : "parameter"}
    notification = {"notification": "title"}
    profile = {"profile": "my_uuid"}
"""

import argparse
import json
import logging
import os
import pathlib
import ssl
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Tuple
from urllib.parse import urlparse

from appdirs import user_data_dir

appname = "blinkpie"
authorname = "jamestansx"
dbpath = "blinkpiedb.json"
profilepath = "blinkpieprofile.json"
logging.basicConfig(
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    level=logging.DEBUG,
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger()


def is_path_exist(path: str):
    if not pathlib.Path(path).is_dir():
        os.makedirs(path, exist_ok=True)
    return path


def is_file_exist(fpath: str):
    if not os.exists(fpath):
        with open(fpath, "w+"):
            ...
    return fpath


class BlinkpieHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.database = is_file_exist(
            os.join(
                is_path_exist(user_data_dir(appname, authorname)),
                dbpath,
            )
        )
        self.profiledb = is_file_exist(
            os.join(
                is_path_exist(user_data_dir(appname, authorname)),
                profilepath,
            )
        )
        self.params = {
            "data": self.database,
            "notification": self.database,
            "profile": self.profiledb,
        }
        super(BlinkpieHandler, self).__init__(*args, **kwargs)

    def _set_response(self, response=200):
        self.send_response(response)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def _check_content_validity(self, params: dict):
        for param in self.params:
            if param in params:
                return True
        else:
            logger.error("Invalid GET/POST parameters!")
            return False

    def do_GET(self):
        logger.debug(self.path)
        params = urlparse(self.path).query
        logger.debug(params)
        params = dict(qc.split("=") for qc in params.split("&"))
        if not self._check_content_validity(params):
            self.send_response(400)
            return
        with open(self.params[next(iter(params))], "r") as f:
            content: list = json.loads(f.read())[next(iter(params))]
            for key in content:
                if (next(iter(params)) == "profile") and self._check_profile(
                    key, params
                ):
                    return
                else:
                    if params[next(iter(params))] in key:
                        self._set_response()
                        self.wfile.write(content[key].encode())
                        return
            else:
                self._set_response(404)

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        content: dict = json.loads(
            str(self.rfile.read(content_length).decode())
        )
        logger.info(content)
        if not self._check_content_validity(content):
            self._set_response(400)
            return
        try:
            if next(iter(content)) == "profile":
                self._write_profile(self.params[next(iter(content))], content)
            else:
                self._write_content(self.params[next(iter(content))], content)
            self._set_response()
        except Exception as e:
            logger.error("Error in POST: %s", e)
            self._set_response(400)

    def _write_content(self, filepath: str, content: dict):
        data = dict()
        if os.stat(filepath).st_size == 0:
            data = {"data": dict(), "notification": dict()}
        else:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        with open(filepath, "w", encoding="utf-8") as f:
            update_content = content[next(iter(content))]
            data[next(iter(content))].update(update_content)
            json.dump(data, f, ensure_ascii=False, indent=4)

    def _write_profile(self, filepath: str, content: dict):
        data = dict()
        if os.stat(filepath).st_size == 0:
            data = {"profile": list()}
        else:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        with open(filepath, "w", encoding="utf-8") as f:
            update_content = content[next(iter(content))]
            for i in data[next(iter(content))]:
                if i["UUID"] == content[next(iter(content))]["UUID"]:
                    i.update(update_content)
                    break
            else:
                data[next(iter(content))].append(update_content)
            json.dump(data, f, ensure_ascii=False, indent=4)

    def _check_profile(self, key: dict, params: dict) -> bool:
        if key[next(iter(key))] == params[next(iter(params))]:
            self._set_response()
            self.wfile.write(json.dumps(key).encode())
            return True
        return False


def main(serveraddress: Tuple, certfile: str):

    httpd = HTTPServer(serveraddress, BlinkpieHandler)
    httpd.socket = ssl.wrap_socket(
        httpd.socket, certfile=certfile, server_side=True
    )
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        logger.info("Server terminated")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        nargs="?",
        default="..\\server.pem",
        help="Path to ssl certfile [..\\server.pem]",
        type=str,
    )
    args = parser.parse_args()
    serveraddress = ("0.0.0.0", 443)
    main(serveraddress, args.path)
