import humanize
import psutil
import sys
import discord
from discord.ext import commands
from ..Utils import Paginator, PaginatorInterface, get
from ..__init__ import __version__

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

  @commands.command()
  async def rtest(self, ctx, url):
    async def returner(result):
      return result.status, await result.text()
    r = await get(url, returner)
    await ctx.send('\n'.join(map(str, (f'Response from {url}:', *r))))

  @commands.command()
  async def botinfo(self, ctx):
    message = [
      f'JusBot v{__version__}, discord.py `{discord.__version__}`',
      f'Python {sys.version} on {sys.platform}'.replace('\n', '')
    ]

    proc = psutil.Process()

    with proc.oneshot():

      mem = proc.memory_full_info()
      message.append(
        f'Using {humanize.naturalsize(mem.rss)} physical memory and '
        f'{humanize.naturalsize(mem.vms)} virtual memory, '
        f'{humanize.naturalsize(mem.uss)} of which is unique to this process'
      )

      name = proc.name()
      pid = proc.pid
      threads = proc.num_threads()
      message.append(f'Running on PID {pid} (`{name}`) with {threads} thread(s)')

      message.append('')

      cache = f"{len(self.bot.guilds)} guild(s) and {len(self.bot.users)} user(s)"

      if isinstance(self.bot, discord.AutoShardedClient):
          message.append(f"This bot is automatically sharded and can see {cache}.")
      elif self.bot.shard_count:
          message.append(f"This bot is manually sharded and can see {cache}.")
      else:
          message.append(f"This bot is not sharded and can see {cache}.")

      if self.bot._connection.max_messages:
          message_cache = f"Message cache capped at {self.bot._connection.max_messages}"
      else:
          message_cache = "Message cache is disabled"

      if discord.version_info >= (1, 5, 0):
          presence_intent = f"presence intent is {'enabled' if self.bot.intents.presences else 'disabled'}"
          members_intent = f"members intent is {'enabled' if self.bot.intents.members else 'disabled'}"

          message.append(f"{message_cache}, {presence_intent} and {members_intent}.")
      else:
          guild_subscriptions = f"guild subscriptions are {'enabled' if self.bot._connection.guild_subscriptions else 'disabled'}"

          message.append(f"{message_cache} and {guild_subscriptions}.")
      
      message.append(f'Average websocket latency: {round(self.bot.latency*1000,1)}ms')

      await ctx.send('\n'.join(message))

    
def setup(bot):
  bot.add_cog(Diagnostics(bot))