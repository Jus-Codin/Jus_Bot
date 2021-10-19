from discord.ext.commands.bot import BotBase
from .PythonShell.pythonshell import python3
from .Utils import error_handler
from signal import Signals
import discord

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

    if suppress:
      s = 'globally' if self.suppress else 'for this command\'s cog'
      await ctx.send('Command raised an exception, but error suppression is enabled '+s)
      return

    if ctx.command:
      if ctx.command.has_error_handler():
        return

    await error_handler(ctx, error)

  async def on_message(self, message: discord.Message):
    channel = message.channel
    if message.author.bot:
      return
    elif _pythonPrefix(message.content, channel):
      code = message.content.replace('```python', '```py', 1)[6:-3] if _pythonPrefix(message.content) else message.content
      if code.startswith('i#'):
        return
      
      async with channel.typing():
        result = await python3(code)

        returncode = result.returncode

        msg = f'Your code has finished running with return code {returncode}'
        err = ''

        if returncode is None:
          msg = 'Your code has failed'
          err = result.stdout.strip()
        elif returncode == 15:
          msg = 'Your code timed out or ran out of memory'
        elif returncode == 255:
          msg = 'Your code has failed'
          err = 'A fatal error has occurred'
        else:
          try:
            name = Signals(returncode).name
            msg = f'{msg} ({name})'
          except ValueError:
            pass

        if err:
          output = err
        else:
          output = result.stdout.strip()
          if output == '':
            output = 'No output detected'
          else:
            output = [f'{i:03d} | {line}' for i, line in enumerate(output.split('\n'), 1)]
            output = '\n'.join(output)

        s = f'{message.author.mention}, {msg}.\n\n```\n{output}\n```'

      if len(s) < 2001:
        await channel.send(s)
      else:
        output = 'Output too large to send'
        await channel.send(f'{message.author.mention}, {msg}.\n\n```\n{output}\n```')
    else:
      await self.process_commands(message)