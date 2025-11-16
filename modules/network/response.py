from modules.exceptions.base import *
from typing import Dict, Literal
import json

class RawResponse:
    def __init__(self, raw_response_body: bytes, raw_headers_body: bytes):
        """
        Класс для нормализации сырых данных полученных в результате запроса
        :param raw_response_body: Сырой ответ
        :param raw_headers_body: Сырые заголовки
        """
        self.__response_body: bytes = raw_response_body
        self.__headers_body: bytes = raw_headers_body
        self.status_code: int = 0
        self.headers = self.__parse_response_headers()
        self.response_data = self.__parse_response_payload()

    def __parse_response_payload(self) -> str:
        """
        Грамотная распаковка Json
        :return: Нормализованный ответ от сервера
        """

        return self.__response_body.decode('utf-8').split("\r\n")[1]

    def __parse_response_headers(self) -> dict[str, str]:
        """
        Грамотная распаковка Headers
        :return: Headers приведенные к Json
        """
        raw_data = self.__headers_body.decode('utf-8').split("\r\n")
        self.status_code = int(raw_data[0].split(" ")[1])
        result = {}

        for line in raw_data[1:-2]:  # обрезаем окончание заголовков
            extracted = line.split(": ", 2)

            result[extracted[0]] = extracted[1]

        return result


class Response:
    def __init__(self, raw_response: RawResponse, method: Literal["GET", "POST"]):
        """
        Класс в котором содержится данные ответа от сервера
        :param raw_response: Сырые данные RawResponse
        :param method: Метод запроса
        """
        self.__raw_response = raw_response
        self.method = method
        self.headers = self.__raw_response.headers
        self.text = raw_response.response_data
        self.status_code = self.__raw_response.status_code

    def json(self) -> Dict:
        try:
            return json.loads(self.text)
        except json.JSONDecodeError as e:
            raise JsonNotFoundError(self.headers['Content-Type'], e)

    def __repr__(self) -> str:
        return f"<Response [{self.status_code}]>"

