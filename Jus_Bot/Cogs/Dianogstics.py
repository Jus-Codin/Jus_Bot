import humanize
from discord.ext import commands

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

def setup(bot):
  bot.add_cog(Diagnostics(bot))