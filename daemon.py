'''COSC364 RIP Assignment
Jordan Chubb
Vincent Zong
29/04/2025
'''

import argparse
from functools import partial
import json
import selectors
import socket
import time

from configmanager import read_config_file
from ripmanager import RipManager


MAX_PACKET_SIZE = 4 + 20 * 25 # header + rip entry * max number of rip entries


parser = argparse.ArgumentParser()
parser.add_argument("config", help="filename of the configuration file")
parser.add_argument("-d", "--debug", help="print debugging information", action="store_true")
parser.add_argument("--autotesting", help="for automatic testing", action="store_true")
args = parser.parse_args()


if args.autotesting:
    """Force all print calls to flush immediately. Required for
    automatic testing's reading of stdout.
    """
    print = partial(print, flush=True)


def main():
    config = read_config_file(args.config)
    debug(config)

    sockets = get_sockets(config)
    selector = selectors.DefaultSelector()
    for sock in sockets:
        selector.register(sock, selectors.EVENT_READ)

    rip = RipManager(debug, config, sockets[0])

    next_print_time = time.time()
    while True:
        next_print = max(0, next_print_time - time.time())
        next_timeout = min(next_print, rip.next_timeout())
        events = selector.select(timeout=next_timeout)

        for key, _ in events:
            sock = key.fileobj
            message = sock.recv(MAX_PACKET_SIZE)
            rip.incoming_message(message)
        rip.send_any_updates()

        if time.time() >= next_print_time:
            next_print_time = time.time() + 1
            if args.autotesting:
                print(json.dumps(rip.table_list()))
            else:
                print(rip)


def debug(line):
    if args.debug:
        print(line)


def get_sockets(config):
    """Return a socket for each input port."""
    sockets = []
    for port in config.input_ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('127.0.0.1', port))
        sockets.append(sock)
    return sockets


if __name__ == "__main__":
    main()
