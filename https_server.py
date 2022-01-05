import json
from pathlib import Path
from os import makedirs
from appdirs import user_data_dir
from os.path import join, abspath
from http.server import HTTPServer, BaseHTTPRequestHandler
from ssl import wrap_socket

class ArduinoServer(BaseHTTPRequestHandler):


    def _set_response(self):
        self.send_response(200)
        self.end_headers()

    def _is_path_exist(self,path):
        if not Path(path).is_dir():
            makedirs(path, exist_ok=True)
        return str(path)

    def do_GET(self):
        tmp_path = join(self._is_path_exist(user_data_dir('pyduino', 'jamestansx')),'data.txt')
        self._set_response()
        with open(tmp_path, 'r') as f:
            self.wfile.write(f.read().encode())

    def do_POST(self):
        tmp_path = join(self._is_path_exist(user_data_dir('pyduino', 'jamestansx')),'data.txt')
        content_length = int(self.headers['Content-Length'])
        data = self.rfile.read(content_length)
        with open(tmp_path, 'w') as f:
            f.write(data.decode())
        self._set_response()


httpd = HTTPServer(('0.0.0.0',443), ArduinoServer)
httpd.socket = wrap_socket(httpd.socket, certfile=".\\server.pem", server_side=True)

try:
    httpd.serve_forever()
except KeyboardInterrupt:
    httpd.server_close()
    print("server closed")

