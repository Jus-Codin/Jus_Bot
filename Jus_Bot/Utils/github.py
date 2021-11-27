from aiohttp import ClientSession
from gidgethub.aiohttp import GitHubAPI

async def getgithub(url):
  async with ClientSession() as session:
    gh = GitHubAPI(session)

    data = await gh.getitem(url)

  return data

async def getuser(username):
  return await getgithub(f'/users/{username}')