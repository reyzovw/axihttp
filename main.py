from modules.AxiHttp import AxiClient
import time
import asyncio
import aiohttp

async def main():
    async with AxiClient() as client:
        response = await client.post(
            url="https://example.com",
        )

        print(response.json())

if __name__ == '__main__':
    asyncio.run(main())

