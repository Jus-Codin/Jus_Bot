import typing

class ErrorDict(typing.TypedDict):
  code: int
  message: str

class Response(typing.TypedDict):
  success: dict
  contents: dict
  baseurl: str
  copyright: dict
  error: ErrorDict

class QuoteResponse:
  def __init__(self, data: Response):
    self.raw = data
    self.quotes: typing.List[Quote] = []
    for quote in data["contents"]["quotes"]:
      self.quotes.append(Quote(quote))
    

class Quote:
  """Represents a quote"""

  def __init__(self, data: dict):
    self.raw = data
    self.quote: str = data["quote"]
    self.length: int = int(data["length"])
    self.author: str = data["author"]
    self.tags: typing.List[str] = data["tags"]
    self.link: str = data["permalink"]

  def __str__(self):
    return self.quote

  def __repr__(self):
    return self.quote