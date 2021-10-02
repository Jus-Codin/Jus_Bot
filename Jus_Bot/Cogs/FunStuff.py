from discord.ext import commands
from ..PythonShell import replChannel
import random
import signal
class FunStuff(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.hidden = False

  @commands.command()
  async def repl(self, ctx):
    handler = replChannel(self.bot, ctx)
    returncode = await handler.start_repl()
    if returncode == signal.SIGTERM:
      await ctx.send('The repl timed out or was terminated')

  #rng stuff
  @commands.command()
  async def rng(self, ctx, start: int, end: int):
      if start < end:
        await ctx.send(str(random.randrange(start,end)))
      else:
        await ctx.send('Start range cannot be more than the end of it')
  
  @commands.command()
  async def dice(self, ctx):
    await ctx.send(random.randint(1,6))
  
  #other stuff
  @commands.command()
  async def decode(self, ctx, *args):
    if len(args)>1:
      text=' '.join(args[:-1])
      decoder=args[-1]
      try:
        await ctx.send(text.decode(decoder))
        return
      except:
        pass
    await ctx.send('Did you input in the form (string) (decoder)?')


def setup(bot):
  bot.add_cog(FunStuff(bot))