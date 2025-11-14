from modules.AxiHttp import AxiClient
import asyncio

async def main():
    """
    Пример использования AxiHttp
    """
    client = AxiClient()

    response = await client.get("https://api.ipify.org")

    print(response.text)  # Отдает ответ текстом
    print(response.json())  # Форматирует ответ в Json

if __name__ == '__main__':
    asyncio.run(main())

