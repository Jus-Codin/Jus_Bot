from aiohttp import ClientSession

from .models import Quote, QuoteResponse, Response
from .exceptions import RateLimitExceeded, UnknownError

import typing

class QODClient:

  BASE_URL = "https://quotes.rest/qod"
  ENDPOINTS = (
    "categories",
    "languages"
  )

  def __init__(self):
    self._categories: list = None
    self._languages: list = None

  async def _get_response(self, url: str) -> Response:
    async with ClientSession() as session:
      async with session.get(url) as res:
        data: Response = await res.json()
        if res.status == 429:
          raise RateLimitExceeded(data["error"]["message"])
        elif res.status != 200:
          raise UnknownError(data["error"]["message"])
    return data

  async def qod(self, language: str = "en", category: typing.Optional[str] = None) -> Quote:
    url = f"{self.BASE_URL}?language={language}"
    if category is not None:
      url += f"&category={category}"
    data = await self._get_response(url)
    data = QuoteResponse(data)
    return data.quotes[0]

  async def get_categories(self, language: str = "en") -> typing.List[str]:
    url = f"{self.BASE_URL}/categories?detailed=false&language={language}"
    data = await self._get_response(url)
    return list(data["contents"]["categories"].keys())

  async def get_languages(self) -> typing.List[str]:
    url = self.BASE_URL + "/languages"
    data = await self._get_response(url)
    return data["contents"]["languages"]

  async def categories(self) -> typing.List[str]:
    categories = self._categories or await self.get_categories()
    self._categories = categories
    return categories

  async def languages(self) -> typing.List[str]:
    languages = self._languages or await self.get_languages()
    self._languages = languages
    return languages

