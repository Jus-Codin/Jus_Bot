import humanize
import discord
from discord.ext import commands
from ..Utils import Paginator, PaginatorInterface

class Diagnostics(commands.Cog):
  """Commands to get info about the bot"""

  def __init__(self, bot):
    self.bot: commands.Bot = bot

  @commands.command(help='Check if the bot is ready')
  async def ready(self, ctx):
    await ctx.send('Bot has connected to discord!')

  @commands.command(hidden=True)
  @commands.is_owner()
  async def kill(self, ctx):
    await ctx.send('Bot dead')
    await self.bot.logout()
    self.bot.loop.close()

  @commands.command(help='Get the websocket latency')
  async def ping(self, ctx):
    await ctx.send(f'Pong! {round(self.bot.latency*1000,1)}ms')
  
  @commands.command()
  async def test(self, ctx):
    paginator = Paginator(['test1', 'test2', discord.Embed(title='Test', description='This is a test')])
    interface = PaginatorInterface(self.bot, paginator)
    await interface.send_to(ctx)

def setup(bot):
  bot.add_cog(Diagnostics(bot))