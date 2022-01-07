"""
POST FORMAT:
    data = {"data":"send from data"}
    notification = {"notification":"send from notification"}
    profile = {
        "profile":
            {
                "UUID": "thisisuuid",
                "name": "myname",
                "description": "helloworld"
            }
    }
----------------------------------------------------------------
GET FORMAT:
    data = "data"
    notification = "notification"
    profile = {"profile": "my_uuid"}
"""

import json
import logging
from socket import gethostbyname, gethostname

from serial import Serial

from serialtools import *

logger.level = logging.DEBUG
appname = "blinkpie"
authorname = "jamestansx"
iplink = gethostbyname(gethostname())
server = "https://" + iplink + ":443"
port = Serial(port="COM2", baudrate=9600, timeout=0.1, write_timeout=0.1)
SUCCESS_CODE = "200"


def init():
    print(f"IP Address: {server}")
    print("-------------------------------")
    res = input("Generate new Arduino UUID?[y/n] ")
    while res not in {"y", "n"}:
        res = input("Generate new Arduino UUID?[y/n] ")
    if res == "y":
        uuid = genUUID()
        print(f"Arduino new UUID: {uuid}")
        setProfile(uuid)
    print("-------------------------------")


def setProfile(uuid):
    name = input("Arduino name? ")
    description = input("Description[optional]: ")
    dicts = {
        "profile": {"UUID": uuid, "name": name, "description": description},
    }

    return do_post(server, json.dumps(dicts))


def connect(get_data:str):
    logger.debug(f"Connecting to Arduino: {get_data}")
    data = do_get(server, json.loads(get_data))
    content = json.loads(data.text)
    status = data.status_code
    if status == 200:
        logger.info("Connected to device:")
        logger.info(f"Name: {content['name']}")
        logger.info(f"Description: {content['description']}")
        do_write(port, SUCCESS_CODE)
        return True
    elif status == 404:
        logger.warning("Arduino is not registered.. Please setup again")
        return False


def main():
    try:
        while True:
            readData = do_read(port)
            if "profile" in readData:
                if not connect(readData):
                    setProfile(genUUID())
                continue
            is_GET = parse_data(readData)
            if is_GET:
                logger.info("GET <--- SERVER")
                getData = do_get(server, readData)
                do_write(port, getData.text)
                status = ""
                while status != SUCCESS_CODE:
                    status = do_read(port)
                    if "profile" in status:
                        if not connect(status):
                            setProfile(genUUID())
                        break
            else:
                logger.info("POST ---> SERVER")
                _ = do_post(server, json.loads(readData))
                do_write(port, SUCCESS_CODE)
    except KeyboardInterrupt:
        inputs = input("Exit?[y|n(restart)] ")
        if inputs == "n":
            main()
        logger.info("exiting virtual ports handler...")
        exit(0)


if __name__ == "__main__":
    init()
    main()
