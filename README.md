# axihttp

Современный асинхронный HTTP/HTTPS клиент для Python, написанный на чистом asyncio. Быстрый, простой и эффективный для работы с частыми запросами к веб-API.

## Ключевые моменты
* Полностью асинхронный
* Простой API
* Высокая производительность при многих запросах
* Использует нативные библиотеки
* Подробные исключения
* Connection pooling

## Стек
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![SSL](https://img.shields.io/badge/SSL-%230070D1.svg?style=for-the-badge&) ![Socket](https://img.shields.io/badge/Socket-%232596BE.svg?style=for-the-badge)

## Установка

```shell
git clone https://github.com/reyzovw/axihttp/
```

```shell
cd axihttp
```

```shell
pip install -r requirements.txt
```

## Быстрый старт
```python
import asyncio
from axihttp import AxiClient

async def main():
    async with AxiClient() as client:
        # GET запрос
        response = await client.get("https://httpbin.org/json")
        print(f"Status: {response.status_code}")
        print(f"JSON: {response.json()}")
        
        # POST запрос с Json
        data = {"name": "test", "email": "test@example.com"}
        response = await client.post_json("https://httpbin.org/post", data)
        print(f"Response: {response.text}")

asyncio.run(main())
```

## Требования
* Python 3.12+
* Не требует внешних зависимостей


