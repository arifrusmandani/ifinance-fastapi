import httpx
import logging
from contextlib import asynccontextmanager
from app.src.core.config import WSO_API_KEY


class BaseHttpxClient:
    def __init__(self):
        self.__headers = (
            {
                "content-type": "application/json",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/44.0.2403.89 Safari/537.36",
            }
        )

    @property
    def header(self):
        return self.__headers

    @header.setter
    def header(self, headers: dict):
        for key, value in headers:
            self.__headers[key] = value

    async def async_client(self):
        transport = httpx.AsyncHTTPTransport(verify=False)
        httpx_client = httpx.AsyncClient(
            transport=transport,
            headers={},
            trust_env=False,
            verify=False
        )
        return httpx_client


@asynccontextmanager
async def httpx_context():
    client = await BaseHttpxClient().async_client()
    client.headers = {
        "APIKey": WSO_API_KEY
    }
    try:
        yield client
    except ValueError as error:
        logging.error("APIKey WSO2 not working")
    finally:
        await client.aclose()
