from modules.exceptions.base import SocketEstablishedError
from modules.network.response import Response, RawResponse
from typing import Literal, Dict, Tuple
from modules.utils import extract_url
from collections import defaultdict
import asyncio
import json
import ssl


class ConnectionPool:
    def __init__(self):
        """
        Connection pool
        """
        self.__pool: Dict[Tuple[str, int, bool], asyncio.Queue] = defaultdict(asyncio.Queue)
        self._max_size = 10

    async def get_connection(self, host: str, port: int, use_ssl: bool) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """
        Получает соединение
        :param host: Адрес
        :param port: Порт
        :param use_ssl: Использовать SSL шифрование
        :return: StreamReader, StreamWriter
        """
        key = (host, port, use_ssl)

        if not self.__pool[key].empty():
            return await self.__pool[key].get()

        ssl_context = None
        if use_ssl:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        reader, writer = await asyncio.open_connection(
            host=host,
            port=port,
            ssl=ssl_context
        )
        return reader, writer

    async def return_connection(self, host: str, port: int, use_ssl: bool, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """
        Возвращает конкретное соединение
        :param host: Адрес
        :param port: Порт
        :param use_ssl: Использовать SSL шифрование
        :param reader: StreamReader
        :param writer: StreamWriter
        """
        key = (host, port, use_ssl)

        if writer.is_closing():
            return

        if self.__pool[key].qsize() < self._max_size:
            await self.__pool[key].put((reader, writer))
        else:
            writer.close()
            await writer.wait_closed()

    async def close_all(self):
        """
        Закрывает все соединения
        """

        for queue in self.__pool.values():
            while not queue.empty():
                reader, writer = await queue.get()
                if not writer.is_closing():
                    writer.close()
                    await writer.wait_closed()

class NetworkProtocol:
    def __init__(self):
        """
        Класс для низкоуровневой работы с сетью
        """
        self.__pool = ConnectionPool()

    async def __fetch(
            self,
            host: str,
            path: str,
            method: Literal["GET", "POST"],
            use_ssl: bool = False,
            json_data: bytes = None,
            headers: dict = None
    ) -> bytes:
        """
        Основная функция для выполнения HTTP/HTTPS запросов.
        :param host: Доменное имя сервера (ex. "api.example.com")
        :param path: Путь и параметры запроса
        :param method: Метод запроса (ex. "GET")
        :param use_ssl: Использовать SSL/TLS шифрование (ex. "True" для HTTPS)
        :param headers: Заголовки запроса
        :param json_data: Тело запроса (используется для запросов по типу POST)
        :return: Сырой ответ в байтах
        """
        port = 443 if use_ssl else 80

        reader, writer = await self.__pool.get_connection(host, port, use_ssl)

        try:
            request_lines = [
                f"{method} {path} HTTP/1.1",
                f"Host: {host}",
                "Connection: keep-alive",
                "User-Agent: AxiHTTP/1.0",
                "Accept: */*"
            ]

            if headers:
                for key, value in headers.items():
                    request_lines.append(f"{key}: {value}")
            if json_data:
                if "Content-Type" not in headers and "content-type" not in headers and method == "POST":
                    request_lines.append("Content-Type: application/json")
                elif "Content-Type" not in headers and "content-type" not in headers and method == "GET":
                    request_lines.append("Content-Type: */*")

                request_lines.append(f"Content-Length: {len(json_data)}")

            request_lines.extend(["", ""])
            request = "\r\n".join(request_lines)

            writer.write(request.encode())

            if json_data:
                writer.write(json_data)

            await writer.drain()

            headers = await reader.readuntil(b"\r\n\r\n")

            content_length = None
            headers_text = headers.decode('utf-8')
            for line in headers_text.split('\r\n'):
                if line.lower().startswith('content-length:'):
                    content_length = int(line.split(':')[1].strip())
                    break

            body = b""
            if content_length:
                body = await reader.readexactly(content_length)
            else:
                try:
                    while True:
                        chunk = await asyncio.wait_for(reader.read(4096), timeout=2.0)
                        if not chunk:
                            break
                        body += chunk
                except asyncio.TimeoutError:
                    pass

            return RawResponse(body, headers)

        except Exception as e:
            writer.close()
            await writer.wait_closed()
            raise SocketEstablishedError()
        finally:
            if 'writer' in locals() and not writer.is_closing():
                await self.__pool.return_connection(host, port, use_ssl, reader, writer)

    async def close(self):
        """Закрывает все соединения при завершении"""
        await self.__pool.close_all()

    async def __get(self, url: str, headers: dict) -> bytes:
        """
        Низкоуровневая функция для выполнения GET запроса
        :param url: Адрес сайта
        :param headers: Заголовки запроса
        :return: Сырой ответ в байтах
        """
        url_parts = extract_url(url)

        use_ssl = url_parts.get("protocol") == "https"

        response = await self.__fetch(
            host=url_parts["host"],
            path=url_parts["path"],
            method="GET",
            use_ssl=use_ssl,
            headers=headers
        )

        return response

    async def get(self, url: str, headers: dict) -> Response:
        """
        Функция для выполнения GET запроса
        :param url: Адрес сайта
        :param headers: Заголовки запроса
        :return: Объект <Response>
        """
        response_data = await self.__get(url, headers)

        return Response(response_data, "GET")

    async def __post(self, url: str, data: dict, headers: dict) -> bytes:
        """
        Низкоуровневая функция для выполнения POST запроса
        :param url: Адрес сайта
        :param data: Json тело запроса
        :param headers: Заголовки запроса
        :return: Сырой ответ в байтах
        """
        json_bytes = json.dumps(data).encode('utf-8')
        url_parts = extract_url(url)

        use_ssl = url_parts.get("protocol") == "https"

        response = await self.__fetch(
            host=url_parts["host"],
            path=url_parts["path"],
            method="POST",
            use_ssl=use_ssl,
            json_data=json_bytes,
            headers=headers
        )

        return response

    async def post(self, url: str, data: dict, headers: dict) -> Response:
        """
        Функция для выполнения POST запроса
        :param url: Адрес сайта
        :param data: Json тело запроса
        :param headers: Заголовки запроса
        :return: Объект <Response>
        """
        response_data = await self.__post(url, data, headers)

        return Response(response_data, "POST")
