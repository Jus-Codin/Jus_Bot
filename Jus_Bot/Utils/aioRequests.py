"""
A wrapper for Aiohttp
"""
from aiohttp import ClientSession

async def _defaultReturn(result):
  return await result.text()

async def get(url: str, method=_defaultReturn, params: dict=None, headers: dict=None):
  async with ClientSession() as session:
    async with session.get(url, params=params, headers=headers) as r:
      result = await method(r)
  return result

async def post(url: str, method=_defaultReturn, params: dict=None, headers: dict=None):
  async with ClientSession() as session:
    async with session.post(url, params=params, headers=headers) as r:
      result = await method(r)
  return result