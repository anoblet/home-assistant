"""Stock HisenseB2B BKLV transport for Home Assistant's Python runtime."""

import argparse
import socket
import time


def request(host, command):
    body = command.encode("ascii")
    packet = body + bytes([-sum(body) % 256, 13])
    deadline = time.monotonic() + 5
    with socket.create_connection((host, 7310), timeout=5) as connection:
        connection.sendall(packet)
        received = b""
        while len(received) <= 4096:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("TV response timed out")
            connection.settimeout(remaining)
            chunk = connection.recv(4096)
            if not chunk:
                raise RuntimeError("TV closed connection before replying")
            received += chunk
            if len(received) > 4096:
                break
            start = received.find(b"ALL:")
            if start < 0 or len(received) < start + 15:
                continue
            frame = received[start : start + 15]
            if frame[13:] != b"\r\n" or sum(frame[:13]) % 256:
                raise RuntimeError("Invalid TV response framing or checksum")
            if frame[4:8] != b"OkAY":
                raise RuntimeError("TV rejected command")
            return frame[8:12].decode("ascii")
    raise RuntimeError("Oversized TV response")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host")
    parser.add_argument("level", type=int, choices=range(101), metavar="0-100")
    args = parser.parse_args()
    request(args.host, f"SALLBKLV{args.level:04d}")
    time.sleep(0.7)
    value = request(args.host, "QALLBKLV????")
    if len(value) != 4 or not value.isascii() or not value.isdigit():
        raise RuntimeError("Invalid backlight reading")
    if int(value) != args.level:
        raise RuntimeError(f"Backlight readback {value} differs from {args.level}")
    print(f"Backlight: {int(value)}")


if __name__ == "__main__":
    main()
