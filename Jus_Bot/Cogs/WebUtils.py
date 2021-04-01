import discord
from discord.ext import commands
from ..Utils import get, WolframClient, PaginatorInterface, Paginator
import os

class WebUtils(commands.Cog):
  """Commands to get info from the internet"""

  def __init__(self, bot):
    self.bot: commands.Bot = bot
    self.client = WolframClient(os.getenv('APPID'))

  @commands.command()
  async def wolfram(self, ctx, *args):
    embeds = []
    res = await self.client.query(' '.join(args))
    if assumptions := res.assumptions:
      assumption = next(assumptions)['assumption']
      text = assumption.get('@template')
      text = text.replace('${desc1}', assumption['value'][0]['@desc'])
      try:
        text = text.replace('${word}', assumption['@word'])
      except Exception:
        pass
    for pod in res.pods:
      embed = discord.Embed(title='Results from Wolfram|Alpha',
                            description='Powered by Wolfram|Alpha v2.0 API',
                            url='https://www.wolframalpha.com/')
      embed.add_field(name='Assumption', value=text[:text.index('. ')+1])
      embeds.append(embed.add_field(name=pod.title, value=pod.text, inline=False))
    paginator = PaginatorInterface(self.bot, Paginator(pages=embeds))
    await paginator.send_to(ctx)
    #await ctx.send(next(res.results).text)

def setup(bot):
  bot.add_cog(WebUtils(bot))