from modules.AxiHttp import AxiClient
import time
import asyncio
import aiohttp

async def main():
    """
    Пример использования AxiHttp
    """
    # Тест вашего клиента
    async with AxiClient() as client:  # Теперь с контекстным менеджером
        payload = {
            "test": 123
        }
        get_response = await client.get("https://echo.free.beeceptor.com")
        post_response = await client.post("https://echo.free.beeceptor.com", data=payload)

        print("=" * 20)
        print("GET REQUEST ->")
        print(get_response.json())
        # print(get_response.text)
        print(get_response.status_code)

        print("=" * 20)
        print("POST REQUEST ->")
        # print(post_response.text)
        print(post_response.json())
        print(post_response.status_code)

if __name__ == '__main__':
    asyncio.run(main())

