from discord.ext import commands, tasks
from ..Utils import quotes
from datetime import datetime, timedelta
import aiofiles
import json

class Quotes(commands.Cog):
  """> Get quotes from various APIs"""

  def __init__(self, bot):
    self.bot: commands.Bot = bot
    self.hidden = False
#    self.last_qod_update = None
#    self.update_qod.start()
  
#  def cog_unload(self):
#    self.update_qod.stop()

#  @tasks.loop(hours=1)
#  async def update_qod(self):
#    print('Updating qod...')
#    self.last_qod_update = datetime.now()
#    try:
#      quote = await quotes.tss_qod()
#    except quotes.qodError:
#      print('Update failed, error from http request')
#      return
#    async with aiofiles.open('Jus_Bot/Data/quotes.json', 'r') as file:
#      await file.truncate(0)
#      await file.seek(0)
#      await file.close()
#    async with aiofiles.open('Jus_Bot/Data/quotes.json', 'w') as file:
#      await file.write(json.dumps(quote))
#    return

#  @commands.command(help='> Get the quote of the day')
#  async def qod(self, ctx, category='inspire'):
#    with open('Jus_Bot/Data/quotes.json', 'r') as file:
#      quote = json.loads(file.read())
#    q = quote.get(category, None)
#    if q is None:
#      await ctx.send('There is no such category')
#    else:
#      qdate = datetime.fromisoformat(q['date']).date()
#      if datetime.today().date() == qdate or self.last_qod_update is None:
#        # We do not know if we hit the rate limit, so we just use old quotes for now
#        qoute, author = q['qoute'], q['author']
#        await ctx.send(f'{quote}\n~{author}')
#      elif datetime.now() - self.last_qod_update < timedelta(hours=1, minutes=1):
#        # Can't update or will hit rate limit...
#        qoute, author = q['qoute'], q['author']
#        await ctx.send(f'{quote}\n~{author}')
#      else:
#        # We should be able to update...
#        await self.update_qod.__call__()
#        await self.qod.__call__(ctx, category)

  @commands.command(help='> Get a inspirational quote')
  async def inspquote(self, ctx):
    quote = await quotes.forismatic()
    await ctx.send(quote)
  
  @commands.command(help='> Get a random paper quote')
  async def paperquote(self, ctx, language='en'):
    quote = await quotes.paper(language)
    await ctx.send(quote)

def setup(bot):
  bot.add_cog(Quotes(bot))