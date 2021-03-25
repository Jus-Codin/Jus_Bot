import discord
import io
import traceback
import sys

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
      codeOut = io.StringIO()
      code = message.content.replace('```python', '```py', 1)[6:-3] if pythonPrefix(message.content) else message.content
      if code.startswith('i#'):
        return
      sys.stdout = codeOut

      try:
        code = compile(code, filename='<InlineCode>', mode='exec')

        if message.author.id == 694139031298113556:
          exec(code, {'message':message, 'channel':channel, 'bot':self, 'p':print, 'runCoro':self.loop.create_task})
        else:
          exec(code, {'p':print, 'input':None})
      
      except discord.HTTPException:
        await channel.send('`A HTTP exception has occurred`')
        return
      except KeyboardInterrupt as e:
        # Prevent people from accidentally shutting the bot down
        tb = traceback.format_exc()
        await channel.send('```' + f'{e}\n{tb}' + '```')
        return
      except Exception as e:
        tb = traceback.format_exc()
        await channel.send('```' + f'{e}\n{tb}' + '```')
        return

      sys.stdout = sys.__stdout__
      s = codeOut.getvalue()
      if s:
        await channel.send(f'```{s}```')
      else:
        await channel.send(f'```No output detected```')  