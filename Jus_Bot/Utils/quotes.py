from .aioRequests import get
import os

class qodError(Exception):
  pass

async def json_handler(result):
  return await result.json()

async def tss_qod():
  quotes = {
    'inspire' : None,
    'management' : None,
    'sports' : None,
    'life' : None,
    'funny' : None,
    'love' : None,
    'art' : None,
    'students' : None
  }
  for i in quotes.keys():
    print(i)
    url = f'https://quotes.rest/qod?catergory={i}&language=en'
    r = await get(url, method=json_handler, headers={'content_type':'application.json'})
    if r.get('error', None) is not None:
      raise qodError
    quotes[i] = r['contents']['quotes'][0]
  print(quotes)
  return quotes

async def forismatic():
  url = 'https://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=en'
  async def handler(result):
    result = await result.json()
    quote = result.get('quoteText')
    author = result.get('quoteAuthor')
    if not author:
      author = 'Unknown'
    return f'"{quote}"\n~{author}'
  return await get(url, method=handler)

async def paper(language='en'):
  url  = f'https://api.paperquotes.com/apiv1/quotes/?lang={language}&limit=1&offset=1'
  headers = {'Authorization' : os.getenv('PAPERTOKEN')}
  async def handler(result):
    return (await result.json())['results'][0]['quote']
  return await get(url, method=handler, headers=headers)