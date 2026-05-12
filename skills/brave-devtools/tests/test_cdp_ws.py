#!/usr/bin/env python3
import unittest
import socket
import threading
import struct
import json
import base64
import time

class MockCDPServer:
    def __init__(self):
        self.running = False
        self.server = None
        self.thread = None

    def start(self, port=9223):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('localhost', port))
        self.server.listen(1)
        self.running = True
        self.thread = threading.Thread(target=self._serve, daemon=True)
        self.thread.start()

    def _serve(self):
        while self.running:
            try:
                self.server.settimeout(1)
                conn, addr = self.server.accept()
                threading.Thread(target=self._handle, args=(conn,), daemon=True).start()
            except socket.timeout:
                continue

    def _handle(self, conn):
        data = b''
        while b'\r\n\r\n' not in data:
            data += conn.recv(4096)
            if not data:
                conn.close()
                return

        if b'Upgrade: websocket' in data:
            resp = "HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: test\r\n\r\n"
            conn.send(resp.encode())

            MASK_KEY = bytes([0x0B, 0xAD, 0xBE, 0xEF])

            while self.running:
                try:
                    header = b''
                    while len(header) < 2:
                        chunk = conn.recv(2 - len(header))
                        if not chunk:
                            return
                        header += chunk

                    opcode = header[0] & 0x0F
                    length = header[1] & 0x7F

                    if length == 126:
                        ext = conn.recv(2)
                        length = struct.unpack('!H', ext)[0]
                    elif length == 127:
                        ext = conn.recv(8)
                        length = struct.unpack('!Q', ext)[0]

                    if header[1] & 0x80:
                        mask = conn.recv(4)
                    else:
                        mask = None

                    payload = b''
                    while len(payload) < length:
                        chunk = conn.recv(length - len(payload))
                        if not chunk:
                            break
                        payload += chunk

                    if mask:
                        payload = bytes([payload[i] ^ mask[i % 4] for i in range(len(payload))])

                    if opcode == 0x8:
                        break

                    msg = json.loads(payload.decode())

                    resp_data = {'id': msg.get('id'), 'result': {'result': {'type': 'string', 'value': 'mock'}}}
                    resp_text = json.dumps(resp_data).encode()
                    resp_len = len(resp_text)
                    resp_header = struct.pack('!BB', 0x81, resp_len) if resp_len <= 125 else struct.pack('!BBH', 0x81, 126, resp_len)
                    conn.sendall(resp_header + resp_text)

                except (socket.timeout, ConnectionError, json.JSONDecodeError):
                    break

        conn.close()

    def stop(self):
        self.running = False
        if self.server:
            self.server.close()


class TestWebSocketFraming(unittest.TestCase):
    def test_frame_encode_7bit_length(self):
        data = b'Hello'
        length = len(data)
        header = struct.pack('!BB', 0x81, length)
        self.assertEqual(header[0], 0x81)
        self.assertEqual(header[1], 5)

    def test_frame_encode_16bit_length(self):
        data = b'Hello World ' * 100
        length = len(data)
        self.assertGreater(length, 125)
        self.assertLess(length, 65536)
        header = struct.pack('!BBH', 0x81, 126, length)
        self.assertEqual(header[0], 0x81)
        self.assertEqual(header[1], 126)
        self.assertEqual(struct.unpack('!H', header[2:4])[0], length)

    def test_frame_encode_64bit_length(self):
        data = b'x' * 70000
        length = len(data)
        self.assertGreater(length, 65535)
        header = struct.pack('!BBQ', 0x81, 127, length)
        self.assertEqual(header[0], 0x81)
        self.assertEqual(header[1], 127)
        self.assertEqual(struct.unpack('!Q', header[2:10])[0], length)

    def test_masking_and_unmasking(self):
        payload = b'Test message for masking'
        mask = bytes([0x12, 0x34, 0x56, 0x78])
        masked = bytes([payload[i] ^ mask[i % 4] for i in range(len(payload))])
        self.assertNotEqual(masked, payload)
        unmasked = bytes([masked[i] ^ mask[i % 4] for i in range(len(masked))])
        self.assertEqual(unmasked, payload)

    def test_jsonserialization_7bit_id(self):
        msg = json.dumps({'id': 999999999, 'method': 'test'})
        self.assertIn('999999999', msg)
        parsed = json.loads(msg)
        self.assertEqual(parsed['id'], 999999999)

    def test_jsonserialization_32bit_id(self):
        msg = json.dumps({'id': 2147483647, 'method': 'test'})
        self.assertIn('2147483647', msg)


if __name__ == '__main__':
    unittest.main()