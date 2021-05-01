"""
A wrapper for the Wolfram|Alpha v2.0 API
"""
from .aioRequests import get
from wolframalpha import Result

class WolframClient:

  def __init__(self, appid: str):
    self.appid = appid

  async def query(self, input):
    """
    Query Wolfram|Alpha using the v2.0 API
    """

    async def _returnHandler(resp):
      assert resp.headers["Content-Type"] == 'text/xml;charset=utf-8'
      return Result(await resp.text('utf-8'))

    data = dict(input=input, appid=self.appid)
    query = tuple(data.items())
    url = 'https://api.wolframalpha.com/v2/query?'
    return await get(url, _returnHandler, params=query)