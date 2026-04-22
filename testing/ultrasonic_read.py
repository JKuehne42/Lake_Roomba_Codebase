"""Minimal SEN0599 reader (procedural, compact).

Sends 0x55 and parses 4-byte frames (0xFF MSB LSB CS).
"""

import argparse
import time
from datetime import datetime
import serial
from serial.tools import list_ports

PORT = "/dev/serial0"
BAUD = 115200
TIMEOUT = 0.5
INTERVAL = 0.5
CMD = b"\x55"


def send_ping(ser, debug=False):
    try:
        ser.reset_input_buffer()
    except Exception:
        pass
    ser.write(CMD)
    if debug:
        print(f"[{datetime.utcnow().isoformat()}] sent: {CMD!r}")


def read_frame(ser, timeout=TIMEOUT):
    end = time.time() + timeout
    while time.time() < end:
        b = ser.read(1)
        if not b:
            continue
        if b[0] != 0xFF:
            continue
        rest = ser.read(3)
        if len(rest) != 3:
            return None
        return bytes([0xFF]) + rest
    return None


def parse_frame(frame):
    if not frame or len(frame) != 4:
        return None, 'invalid'
    msb, lsb, cs = frame[1], frame[2], frame[3]
    calc = (0xFF + msb + lsb) & 0xFF
    if cs != calc:
        return None, f'badcs {cs:02X}!={calc:02X}'
    dist = (msb << 8) | lsb
    if dist == 0:
        return None, 'no-echo'
    return dist, 'ok'


def once(ser, debug=False):
    send_ping(ser, debug=debug)
    frame = read_frame(ser, timeout=ser.timeout)
    if frame is None:
        if debug:
            print(f"[{datetime.utcnow().isoformat()}] no reply")
        return
    dist, reason = parse_frame(frame)
    hexdump = ' '.join(f"{b:02X}" for b in frame)
    ts = datetime.utcnow().isoformat(timespec='milliseconds') + 'Z'
    if dist is not None:
        print(f"{ts} Distance:{dist} mm  raw={hexdump}")
    else:
        print(f"{ts} no-distance reason={reason} raw={hexdump}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--port', default=PORT)
    p.add_argument('--baud', type=int, default=BAUD)
    p.add_argument('--timeout', type=float, default=TIMEOUT)
    p.add_argument('--interval', type=float, default=INTERVAL)
    p.add_argument('--debug', action='store_true')
    p.add_argument('--once', action='store_true')
    p.add_argument('--list-ports', action='store_true')
    args = p.parse_args()

    if args.list_ports:
        for x in list_ports.comports():
            print(x)
        return

    ser = serial.Serial(args.port, baudrate=args.baud, timeout=args.timeout)
    print(f"Opened serial port {args.port} @ {args.baud} baud")

    try:
        if args.once:
            once(ser, debug=args.debug)
            return
        while True:
            once(ser, debug=args.debug)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            ser.close()
        except Exception:
            pass


if __name__ == '__main__':
    main()
