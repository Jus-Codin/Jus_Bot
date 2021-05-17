import discord
from signal import Signals
from .pythonshell import python3

def pythonPrefix(s: str):
  return all((
    s.startswith('```python\n') or s.startswith('```py\n'),
    s.endswith('```')
  ))

class PythonShellBot(discord.Client):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.event(self.on_message)

  async def on_message(self, message: discord.Message):
    channel = message.channel
    if message.author == self.user or message.author.bot:
      return
    elif pythonPrefix(message.content) or channel.name == 'python-shell':
      code = message.content.replace('```python', '```py', 1)[6:-3] if pythonPrefix(message.content) else message.content
      if code.startswith('i#'):
        return

      async with channel.typing():
        result = python3(code)

        returncode = result.returncode

        msg = f'Your code has finished running with return code {returncode}'
        err = ''

        if returncode is None:
          msg = 'Your code has failed'
          err = result.stdout.strip()
        elif returncode == 9:
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
          output = [f'{i:03d} | {line}' for i, line in enumerate(output.split('\n'), 1)]
          output = '\n'.join(output)

        s = f'{message.author.mention}, {msg}.\n\n```\n{output}\n```'

      try:
        await channel.send(s)
      except discord.HTTPException:
        output = 'Output too large to send'
        await channel.send(f'{message.author.mention}, {msg}.\n\n```\n{output}\n```')
        