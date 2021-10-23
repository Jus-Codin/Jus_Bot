from discord.ext.commands.bot import BotBase
from .PythonShell.pythonshell import python3
from .Utils import error_handler
import discord
import re

def _pythonPrefix(s: str, channel: discord.Message.channel=None):
  if hasattr(channel, 'name'):
    if channel.name == 'python-shell':
      return True
  return all((
      s.startswith('```python\n') or s.startswith('```py\n'),
      s.endswith('```')
  ))

class JusBotBase(BotBase):
  '''Base bot to combine python shell and main features'''
  suppress = False

  async def on_command_error(self, ctx, error):

    if self.suppress:
      suppress = True
    elif ctx.cog:
      if ctx.cog.suppress:
        suppress = True
      elif ctx.cog.has_error_handler():
        return
      else:
        suppress = False
    else:
      suppress = False

    if ctx.command:
      if ctx.command.has_error_handler():
        return

    await error_handler(ctx, error, suppress=suppress)

  async def on_message(self, message: discord.Message):
    channel = message.channel
    if message.author.bot:
      return
    elif _pythonPrefix(message.content, channel):
      code = re.sub("```python|```py|```", "", message.content).strip()
      if code.startswith('i#'):
        return
      
      async with channel.typing():
        s = await python3(code, message.author.mention)

      await channel.send(s)
    else:
      await self.process_commands(message)