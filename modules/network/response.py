from modules.exceptions.base import *
from typing import Dict, Literal
import json

class Response:
    def __init__(self, raw_response: bytes, method: Literal["GET", "POST"]):
        self.raw = raw_response
        self.method = method
        self._parse_response()

    def _parse_response(self):
        if self.method == "GET":
            header_body = self.raw.split(b'141\r\n', 1)
        elif self.method == "POST":
            header_body = self.raw.split(b'\r\n\r\n1ad', 1)

        headers_part = header_body[0]
        self.body = header_body[1] if len(header_body) > 1 else b""

        headers_lines = headers_part.split(b'\r\n')
        status_line = headers_lines[0].decode()
        self.http_version, status_code, self.reason = status_line.split(' ', 2)
        self.status_code = int(status_code)

        self.headers = {}
        for line in headers_lines[1:]:
            if b':' in line:
                key, value = line.split(b':', 1)
                self.headers[key.strip().decode()] = value.strip().decode()

    @property
    def content(self) -> bytes:
        return self.body

    @property
    def text(self) -> str:
        return self.body.decode('utf-8').replace("\r\n0\r\n\r\n", "")

    def json(self) -> Dict:
        try:
            return json.loads(self.text)
        except json.JSONDecodeError as e:
            raise JsonNotFoundError(self.headers['Content-Type'], e)

    def __repr__(self) -> str:
        return f"<Response [{self.status_code}]>"

