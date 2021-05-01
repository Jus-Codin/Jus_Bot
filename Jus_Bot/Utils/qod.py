from .aioRequests import get

async def tss_qod(category):
  url = f'https://QuotesApi.juscodin.repl.co/get_qod/{category}'
  return await get(url)

