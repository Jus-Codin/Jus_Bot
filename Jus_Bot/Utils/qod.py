from .aioRequests import get

CATEGORIES = ['inspire', 'management', 'sports', 'life', 'funny', 'love', 'art', 'students', 'all']
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

async def update_qod(category):
  print('Updating qod...')
  if category in CATEGORIES:
    if category == 'all':
      pass