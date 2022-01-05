from serial import Serial
from requests import post,get
from requests.packages.urllib3 import disable_warnings
import time
from socket import gethostbyname, gethostname

disable_warnings()

#TODO Add logging function

iplink = gethostbyname(gethostname())
server = 'https://' + iplink + ':443'

port = Serial(
        port="COM2", baudrate=9600, timeout=.1, write_timeout=.1
)

i = 1

def blockPrint():
    import sys, os
    sys.stdout = open(os.devnull, 'w')

def enablePrint():
    import sys, os
    sys.stdout = sys.__stdout__

def do_read():
    read_data = port.readline().decode()
    print(str(i) + " read: " + read_data)
    return read_data

def do_write(write_data):
    port.write(f"{write_data}\r\n".encode())
    print(str(i) + " write: " + write_data)

def do_get():
    get_data = get(server,verify=False).text
    print(str(i) + " get: " + get_data)
    return get_data

def do_post(post_data):
    _,_,post_data = post_data.partition("POST")
    post_data = post_data.strip(' \t\n\r')
    post(server, verify=False, data=post_data)
    print(str(i) + " post: " + post_data)

def init():
    print(f"Your ip address is: {iplink}")
    input("Please enter to Pyduino App: [Enter]")

def main():
    global i
    tmp = ""
    try:
        while True:
            readData = do_read()
            if "POST" in str(readData):
                print(str(i) + " posting...")
                do_post(readData)
            elif "GET" in str(readData):
                print(str(i) + " getting...")
                getData = do_get()
                do_write(getData)
                while("200" not in do_read()):
                    ...
                continue
            else:
                i += 1
                continue
            do_write("200")
            i += 1

    except KeyboardInterrupt:
        enablePrint()
        inputs = input("Exit?[y|n(restart)] ")
        
        if inputs == 'n':
            blockPrint()
            main()
        print("exiting virtual ports handler...")
        exit(0)

if __name__ == "__main__":
    init()
    blockPrint()
    main()
