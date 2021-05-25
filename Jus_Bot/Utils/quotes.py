from .aioRequests import get
import os

async def tss_qod(category):
  url = f'https://QuotesApi.juscodin.repl.co/get_qod/{category}'
  return await get(url)

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