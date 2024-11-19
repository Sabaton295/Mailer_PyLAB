#!/usr/bin/env python
import asyncio
import subprocess
import signal
import sys
import os

from src.collector import collector

processes = []

def start():
    print("----- [ ▶ ] Mailer is STARTING -----\n")
    server = subprocess.Popen([sys.executable, 'src/server.py'])
    client = subprocess.Popen([sys.executable, 'src/client.py'])
    asyncio.run(collector())
    processes.extend([server, client])
    for p in processes:
        p.wait()


def signal_handler(sig, frame):
    for p in processes:
        try:
            os.kill(p.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    print('----- [||] Mailer has STOPPED  -----')
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    start()