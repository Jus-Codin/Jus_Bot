"""
A method wrapper for aiohttp
"""

from aiohttp import ClientSession

async def get(url: str, params: dict=None, headers: dict=None):
  result = None
  async with ClientSession() as session:
    async with session.get(url, params=params, headers=headers) as r:
      result = r
  return result

async def post(url: str, params: dict=None, headers: dict=None):
  result = None
  async with ClientSession() as session:
    async with session.post(url, params=params, headers=headers) as r:
      result = r
  return result