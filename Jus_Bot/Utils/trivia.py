from .aioRequests import get

categories = {
  'All Categories': None,
  'General Knowledge': 9,
  'Entertainment: Books': 10,
  'Entertainment: Film': 11,
  'Entertainment: Music': 12,
  'Entertainment: Musicals & Theatres': 13,
  'Entertainment: Television': 14,
  'Entertainment: Video Games': 15,
  'Entertainment: Board Games': 16,
  'Science & Nature': 17,
  'Science: Computers': 18,
  'Science: Mathematics': 19,
  'Mythology': 20,
  'Sports': 21,
  'Geography': 22,
  'History': 23,
  'Politics': 24,
  'Art': 25,
  'Celebrities': 26,
  'Animals': 27,
  'Vehicles': 28,
  'Entertainment: Comics': 29,
  'Science: Gadgets': 30,
  'Entertainment: Japanese Anime & Manga': 31,
  'Entertainment: Cartoon & Animations': 32
}

class TriviaError(Exception):
  pass

class TriviaClient:
  def __init__(self):
    self.token = None
    self.baseurl = 'https://opentdb.com/'

  async def response_handler(self, result) -> dict:
    result = await result.json()
    if result['response_code'] != 0:
      raise TriviaError(f'Received non-zero response code "{result["response_code"]}"\n{result.get("response_message")}')
    else:
      return result

  async def update_token(self):
    url = self.baseurl + 'api_token.php?command=request'
    res = await get(url, self.response_handler)
    self.token = res['token']

  async def trivia(self, amount, *, category=None, difficulty=None, type=None):
    if self.token is None:
      await self.update_token()
    url = self.baseurl + f'api.php?amount={amount}&'
    if category:
      url += f'category={category}&'
    if difficulty:
      url += f'difficulty={difficulty.lower()}&'
    if type:
      url += f'type={type.lower()}&'
    url += f'encode=base64&token={self.token}'
    res = await get(url, self.response_handler)
    return res['results']