import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from os import makedirs
from os.path import exists, join
from pathlib import Path
from ssl import wrap_socket
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
    if not Path(path).is_dir():
        makedirs(path, exist_ok=True)
    return path


def is_file_exist(fpath: str):
    if not exists(fpath):
        with open(fpath, "w+"):
            ...
    return fpath


class BlinkpieHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.database = is_file_exist(
            join(
                is_path_exist(user_data_dir(appname, authorname)),
                dbpath,
            )
        )
        self.profiledb = is_file_exist(
            join(
                is_path_exist(user_data_dir(appname, authorname)),
                profilepath,
            )
        )
        self.params = {
            "data": "data",
            "notification": "notification",
            "profile": "profile",
        }
        super(BlinkpieHandler, self).__init__(*args, **kwargs)

    def _set_response(self, response=200):
        self.send_response(response)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def _check_content_validity(self, params: str):
        for param in self.params:
            if self.params[param] in params:
                return True
        else:
            logger.error("Invalid GET/POST parameters!")
            return False

    def do_GET(self):
        params = urlparse(self.path).query
        if not self._check_content_validity(params):
            self.send_response(400)
            return
        try:
            # PROFILE
            params = dict(qc.split("=") for qc in params.split("&"))
            with open(self.profiledb, "r") as f:
                content = json.loads(f.read())
                content = content[self.params["profile"]]
                for profiles in content:
                    if profiles["UUID"] == params["profile"]:
                        self._set_response()
                        self.wfile.write(json.dumps(profiles).encode())
                        return
                else:
                    logger.error("No such profile")
                    self._set_response(404)
        except ValueError as e:
            # NOTIFICATION or DATA
            with open(self.database, "r") as f:
                try:
                    content = json.loads(f.read())
                    self._set_response()
                    self.wfile.write(content[params].encode())
                except json.JSONDecodeError as e:
                    logger.warning("File is empty: %s" % e)
                    self._set_response(404)
                    return

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        content = json.loads(str(self.rfile.read(content_length).decode()))
        if not self._check_content_validity(content):
            self._set_response(400)
            return
        try:
            for data in content:
                self._write_content(content, data)
            self._set_response()
        except Exception as e:
            self._set_response(400)

    def _write_content(self, content: dict, mode: str):
        filepath = self.database
        data = {}
        if mode == self.params["profile"]:
            filepath = self.profiledb

        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError as e:
                # New File
                logger.warning("File is not valid JSON: %s", e)
                if mode == self.params["profile"]:
                    data = {"profile": []}
                else:
                    data = {"data": "", "notification": ""}
            finally:
                if mode == self.params["profile"]:
                    dat = data["profile"]
                    if isinstance(dat, list):
                        dat.append(content[self.params["profile"]])
                    else:
                        dat = [content[self.params["profile"]]]
                else:
                    for key, value in content.items():
                        data[key] = value
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


def main(serveraddress: Tuple, certfile: str):

    httpd = HTTPServer(serveraddress, BlinkpieHandler)
    httpd.socket = wrap_socket(
        httpd.socket, certfile=certfile, server_side=True
    )
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        logger.info("Server terminated")


if __name__ == "__main__":
    serveraddress = ("0.0.0.0", 443)
    certfile = ".\\server.pem"
    main(serveraddress, certfile)
