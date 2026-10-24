#!/usr/bin/env python3
"""End-to-end smoke test for the fake-TCP transport (Linux, needs root).

Starts a TCP echo target, kcpraw_server and kcpraw_client on loopback in
fake-TCP mode (the default transport, NOT --udp), pushes data through the
tunnel and checks it comes back identical. Also verifies that the iptables
RST-drop rules installed by the raw-socket layer are removed on exit.

Usage:
    go build -o kcpraw_client ./client && go build -o kcpraw_server ./server
    python3 scripts/smoke_faketcp.py [--scenario http,nohttp,expire,mulcon]

Must be run as root or as a user with passwordless sudo.
"""
import argparse
import os
import signal
import socket
import subprocess
import sys
import threading
import time

ECHO_PORT = 19001
KCP_PORT = 29901
LOCAL_PORT = 12949
KEY = "smoketest"
SUDO = [] if os.geteuid() == 0 else ["sudo", "-n"]


def handle(c):
    with c:
        while True:
            d = c.recv(65536)
            if not d:
                return
            c.sendall(d)


def start_echo():
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", ECHO_PORT))
    srv.listen(5)

    def loop():
        while True:
            c, _ = srv.accept()
            threading.Thread(target=handle, args=(c,), daemon=True).start()

    threading.Thread(target=loop, daemon=True).start()


def roundtrip(payloads):
    s = None
    deadline = time.time() + 30
    while time.time() < deadline:
        try:
            s = socket.create_connection(("127.0.0.1", LOCAL_PORT), timeout=2)
            break
        except OSError:
            time.sleep(0.5)
    if s is None:
        raise RuntimeError("client local port never came up")
    with s:
        s.settimeout(20)
        for payload in payloads:
            s.sendall(payload)
            got = b""
            while len(got) < len(payload):
                chunk = s.recv(65536)
                if not chunk:
                    break
                got += chunk
            if got != payload:
                raise RuntimeError(
                    "echo mismatch: sent %d bytes, got %d" % (len(payload), len(got)))


def count_iptables_rules():
    n = 0
    for chain in ("OUTPUT", "INPUT"):
        out = subprocess.run(SUDO + ["iptables", "-S", chain],
                             capture_output=True, text=True).stdout
        n += sum(1 for line in out.splitlines() if str(KCP_PORT) in line)
    return n


class Proc:
    def __init__(self, args, logfile):
        self.logfile = logfile
        self.p = subprocess.Popen(args, stdout=open(logfile, "wb"),
                                   stderr=subprocess.STDOUT)



def run_scenario(name, server_extra, client_extra, check_expire=False):
    print("== scenario:", name, flush=True)
    srvlog, clilog = "/tmp/kcpraw_srv.log", "/tmp/kcpraw_cli.log"
    srv = Proc(SUDO + ["./kcpraw_server", "-l", "127.0.0.1:%d" % KCP_PORT,
                       "-t", "127.0.0.1:%d" % ECHO_PORT, "--key", KEY] + server_extra, srvlog)
    time.sleep(1.5)
    cli = Proc(SUDO + ["./kcpraw_client", "-l", "127.0.0.1:%d" % LOCAL_PORT,
                       "-r", "127.0.0.1:%d" % KCP_PORT, "--key", KEY] + client_extra, clilog)
    try:
        payloads = [b"hello fake tcp!\n", b"FAKETCP-" * 12000 + bytes(range(256)) * 30]
        roundtrip(payloads)
        if check_expire:
            # wait past --autoexpire, reconnect (old conn goes to the
            # scavenger), then only the fresh conn's iptables rule may remain
            time.sleep(4)
            roundtrip([b"after expire\n"])
            deadline = time.time() + 8
            while time.time() < deadline:
                out = subprocess.run(SUDO + ["iptables", "-S", "OUTPUT"],
                                     capture_output=True, text=True).stdout
                client_rules = [l for l in out.splitlines()
                                if "--dport %d" % KCP_PORT in l]
                if len(client_rules) == 1:
                    break
                time.sleep(0.5)
            else:
                raise RuntimeError("expired conn iptables rule leaked: %r" % client_rules)
        print("   ok")
    except Exception:
        for f in (srvlog, clilog):
            print("---- tail of", f)
            try:
                print(open(f).read()[-2000:])
            except OSError:
                pass
        raise
    finally:
        for proc, pat in ((cli, "kcpraw_client"), (srv, "kcpraw_server")):
            subprocess.run(SUDO + ["pkill", "-TERM", "-x", pat],
                           check=False, capture_output=True)
        time.sleep(1)
    leftover = count_iptables_rules()
    if leftover != 0:
        raise RuntimeError("%d iptables rules leaked after exit" % leftover)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default="http,nohttp,expire,mulcon")
    args = ap.parse_args()
    start_echo()
    scenarios = {
        "http":   lambda: run_scenario("fake-tcp + http obfs", [], []),
        "nohttp": lambda: run_scenario("fake-tcp --nohttp", ["--nohttp"], ["--nohttp"]),
        "expire": lambda: run_scenario("fake-tcp autoexpire scavenger",
                                       [], ["--autoexpire", "2"], check_expire=True),
        "mulcon": lambda: run_scenario("fake-tcp mulcon x2",
                                       ["--usemul"], ["--mulconn", "2"]),
    }
    for name in args.scenario.split(","):
        scenarios[name]()
    print("ALL FAKETCP SMOKE OK")


if __name__ == "__main__":
    main()
