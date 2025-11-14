from modules.network.response import Response
from modules.utils import extract_url
from typing import Literal
import asyncio
import ssl


class NetworkProtocol:
    def __init__(self):
        """
        Класс для низкоуровневой работы с сетью
        """
        pass

    async def __fetch(
            self,
            host: str,
            path: str,
            method: Literal["GET", "POST"],
            use_ssl: bool = False
    ) -> bytes:
        """
        Основная функция для выполнения HTTP/HTTPS запросов.
        :param host: Доменное имя сервера (ex. "api.example.com")
        :param path: Путь и параметры запроса
        :param method: Метод запроса (ex. "GET")
        :param use_ssl: Использовать SSL/TLS шифрование (ex. "True" для HTTPS)
        :return: Сырой ответ в байтах
        """
        port = 443 if use_ssl else 80

        ssl_context = None
        if use_ssl:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE  # для тестирования

        try:
            reader, writer = await asyncio.open_connection(
                host=host,
                port=port,
                ssl=ssl_context
            )

            request_lines = [
                f"{method} {path} HTTP/1.1",
                f"Host: {host}",
                "Connection: close",
                "User-Agent: AxiomHTTP/1.0",
                "",  # разделяет headers и body
                ""   # конец тела запроса
            ]

            request = "\r\n".join(request_lines)
            writer.write(request.encode())
            await writer.drain()

            response = b""
            while True:  # читаем ответ
                chunk = await reader.read(4096)
                if not chunk:
                    break
                response += chunk

            return response

        except Exception as e:
            raise Exception(f"Network error: {e}")
        finally:
            if 'writer' in locals():
                writer.close()
                await writer.wait_closed()

    async def __get(self, url: str) -> bytes:
        """
        Низкоуровневая функция для выполнения GET запроса
        :param url: Адрес сайта
        :return: Сырой ответ в байтах
        """
        url_parts = extract_url(url)

        use_ssl = url_parts.get("protocol") == "https"

        response = await self.__fetch(
            host=url_parts["host"],
            path=url_parts["path"],
            method="GET",
            use_ssl=use_ssl
        )

        return response

    async def get(self, url: str) -> Response:
        """
        Функция для выполнения GET запроса
        :param url: Адрес сайта
        :return: Объект <Response>
        """
        response_data = await self.__get(url)

        return Response(response_data)

