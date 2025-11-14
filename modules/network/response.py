from typing import Dict
import email
import email.policy

class Response:
    def __init__(self, raw_response: bytes):
        self.raw = raw_response
        self._parse_response()

    def _parse_response(self):
        header_body = self.raw.split(b'\r\n\r\n', 1)
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
        return self.body.decode('utf-8')

    def json(self) -> Dict:
        import json
        return json.loads(self.text)

    def __repr__(self) -> str:
        return f"<Response [{self.status_code}]>"