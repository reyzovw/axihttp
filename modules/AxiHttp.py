from modules.network.protocols import NetworkProtocol
from modules.network.response import Response

class AxiClient:
    def __init__(self):
        """
        Основной экземпляр клиента для запросов
        """
        self.__protocol = NetworkProtocol()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.__protocol.close()

    async def get(self, url: str, headers: dict | None = None) -> Response:
        """
        Функция для выполнения GET запроса
        :param url: Адрес сайта
        :param headers: Заголовки запроса
        :return: Объект <Response>
        """
        return await self.__protocol.get(url, headers)

    async def post(self, url: str, data: dict | None = None, headers: dict | None = None) -> Response:
        """
        Функция для выполнения POST запроса
        :param url: Адрес сайта
        :param data: Json тело запроса
        :param headers: Заголовки запроса
        :return: Объект <Response>
        """
        if data is None:
            data = {}
        if headers is None:
            headers = {}

        return await self.__protocol.post(url, data, headers)
