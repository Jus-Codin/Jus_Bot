from discord.ext import commands
from ..PythonShell import replChannel
import discord
import random
import signal
class FunStuff(commands.Cog):
  """> Place with fun, wacky stuff"""

  def __init__(self, bot):
    self.bot = bot
    self.hidden = False

  @commands.command(help='> Don\'t even try')
  async def repl(self, ctx):
    handler = replChannel(self.bot, ctx)
    returncode = await handler.start_repl()
    if returncode == signal.SIGTERM:
      await ctx.send('The repl timed out or was terminated')

  #rng stuff
  @commands.command(help='> Gives you a random number or something idk')
  async def rng(self, ctx, start: int, end: int):
      if start < end:
        await ctx.send(str(random.randrange(start,end)))
      else:
        await ctx.send('Start range cannot be more than the end of it')
  
  @commands.command(help='> Imagine rng, but only from 1 to 6')
  async def dice(self, ctx):
    await ctx.send(random.randint(1,6))
  
  #other stuff
  @commands.command(help='> I have no idea what this does so have fun')
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
  
  @commands.command(help='> Allows anyone to execute code on the bot, this is perfectly safe')
  async def pyeval(self, ctx):
    class View(discord.ui.View):
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        button = discord.ui.Button(style=discord.ButtonStyle.secondary, label='Go here I guess',url='https://Puzzles.juscodin.repl.co/puzzle-1')
        self.add_item(button)
    await ctx.send('Hah nice try', view=View())


def setup(bot):
  bot.add_cog(FunStuff(bot))