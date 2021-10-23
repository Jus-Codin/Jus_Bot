from discord.ext import commands
from discord.commands import slash_command, message_command
from ..Utils import embed_template
from ..PythonShell import python3
import discord
import re

class AppCommands(commands.Cog):
  
  def __init__(self, bot):
    self.bot: commands.Bot = bot
    self.hidden = True
    self.suppress = False

  @slash_command(name='ping', description='Get the websocket latency', guild_ids=[837579283991887892])
  async def ping(self, ctx):
    embed = embed_template(ctx, title='Pong! \U0001F3D3', description=f'{round(self.bot.latency*1000,1)}ms')
    await ctx.respond(embed=embed)

  @message_command(name='Run Python', guild_ids=[837579283991887892])
  async def python(self, ctx, message: discord.Message):
    code = re.sub("```python|```py|```", "", message.content).strip()
    s = await python3(code, ctx.user.mention)
    await ctx.respond(s)

def setup(bot):
  bot.add_cog(AppCommands(bot))