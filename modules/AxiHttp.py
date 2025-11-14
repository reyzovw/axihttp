from modules.network.protocols import NetworkProtocol
from modules.network.response import Response

class AxiClient:
    def __init__(self):
        """
        Основной экземпляр клиента для запросов
        """
        self.__protocol = NetworkProtocol()

    async def get(self, url: str) -> Response:
        """
        Функция для выполнения GET запроса
        :param url: Адрес сайта
        :return: Объект <Response>
        """
        return await self.__protocol.get(url)
