import argparse
import json
import logging
import socket
import sys

import serial

from serialtools import SerialTools

appname = "blinkpie"
authorname = "jamestansx"
iplink = socket.gethostbyname(socket.gethostname())
server = "https://" + iplink + ":443"
SUCCESS_CODE = "200"

logging.basicConfig(
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger()
logger.level = logging.DEBUG


def init(st):
    print(f"IP Address: {server}")
    print("-------------------------------")
    res = input("Generate new Arduino UUID?[y/n] ")
    while res not in {"y", "n"}:
        res = input("Generate new Arduino UUID?[y/n] ")
    if res == "y":
        uuid = st.genUUID()
        print(f"Arduino new UUID: {uuid}")
        setProfile(uuid)
    print("-------------------------------")


def setProfile(st, uuid):
    name = input("Arduino name? ")
    description = input("Description[optional]: ")
    dicts = {
        "profile": {"UUID": uuid, "name": name, "description": description},
    }
    return st.do_post(server, dicts)


def connect(st, get_data: str):
    logger.debug(f"Connecting to Arduino: {get_data}")
    data = st.do_get(server, json.loads(get_data))
    logger.debug(f"data {data}")
    content = json.loads(data.text)
    status = data.status_code
    if status == 200:
        logger.info("Connected to device:")
        logger.info(f"Name: {content['name']}")
        logger.info(f"Description: {content['description']}")
        st.do_write(port, "200")
        return True
    elif status == 404:
        logger.warning("Arduino is not registered.. Please setup again")
        return False


def is_available(st):
    status = ""
    while status != SUCCESS_CODE:
        logger.debug("checking handshake")
        status = st.do_read(port)
        if "profile" in status:
            if not connect(status):
                setProfile(st.genUUID())
            break


def main(st):
    while True:
        try:
            readData = st.do_read(port)
            if "profile" in readData:
                if not connect(st, readData):
                    setProfile(st, st.genUUID())
                continue
            is_GET = st.parse_data(st, readData)
            if is_GET:
                logger.info("GET <--- SERVER")
                getData = st.do_get(server, json.loads(readData))
                if getData.status_code == 404:
                    st.do_write(port, "404")
                else:
                    st.do_write(port, getData.text)
                is_available()
            else:
                logger.info("POST ---> SERVER")
                _ = st.do_post(server, json.loads(readData))
                st.do_write(port, SUCCESS_CODE)
        except KeyboardInterrupt:
            inputs = input("Exit?[y|r(restart)|n] ")
            if inputs == "r":
                logger.info("restarting virtual ports handler")
                continue
            elif inputs == "n":
                continue
            elif inputs == "y":
                logger.info("exiting virtual ports handler...")
                exit(0)
        except Exception as e:
            logger.exception("Oh no! Something's wrong!")
            continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--port",
        nargs="?",
        default="COM1",
        help="specify port number to use (COM1)",
        type=str,
    )
    parser.add_argument(
        "--baudrate",
        nargs="?",
        default="9600",
        help="specify baudrate (9600)",
        type=str,
    )
    parser.add_argument(
        "--timeout",
        nargs="?",
        default=0.1,
        help="specify port read/write timeout (0.1)",
        type=float,
    )
    parser.add_argument(
        "--write_timeout",
        nargs="?",
        default=0.1,
        help="specify write timeout (0.1)",
        type=float,
    )
    args = parser.parse_args()

    try:
        port = serial.Serial(
            port=args.port,
            baudrate=args.baudrate,
            timeout=args.timeout,
            write_timeout=args.write_timeout,
        )
    except Exception as e:
        logger.exception("Port not found!")
        input("Press Enter to continue...")
        sys.exit(1)

    tools = SerialTools()
    init(tools)
    main(tools)
