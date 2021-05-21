from discord.ext.commands import errors, MissingPermissions, MissingRequiredArgument
from discord.ext.commands.bot import BotBase, _default
from discord.errors import Forbidden
from .PythonShell.pythonshell import python3
from signal import Signals
import discord
import traceback

def _pythonPrefix(s: str):
  return all((
    s.startswith('```python\n') or s.startswith('```py\n'),
    s.endswith('```')
  ))

class JusBotBase(BotBase):
  '''Base bot to combine python shell and main features'''

  async def on_command_error(self, ctx, error):
    try:
      if isinstance(error, errors.CommandNotFound):
        await ctx.send("Error, cOmMaNd DoEsN't ExIsT")
      elif isinstance(error, MissingPermissions):
        await ctx.send('Error, your permissions are far inferior for this command')
      elif isinstance(error, errors.NotOwner):
        await ctx.send('Error, only the owner of the bot can run this command')
      elif isinstance(error, MissingRequiredArgument):
        await ctx.send('Error, missing smthing')
      else:
        trace_string = '\n'.join(traceback.format_exception(type(error), error, error.__traceback__))
        await ctx.send(f'```\n{trace_string}```')
    except Forbidden:
      pass

  async def on_message(self, message: discord.Message):
    channel = message.channel
    if message.author.bot:
      return
    elif _pythonPrefix(message.content) or channel.name == 'python-shell':
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
          print(output)
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