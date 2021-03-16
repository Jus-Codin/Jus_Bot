from discord.ext.commands import Bot, errors, MissingPermissions, MissingRequiredArgument
from discord.errors import Forbidden
from discord.client import _cleanup_loop
from .pythonshell import PythonShellBot
import asyncio

class Jus_Bot(Bot):
  '''Main class to bind pythonshell to the same bot'''

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.event(self.on_command_error)

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
        await ctx.send(f'{error}')
    except Forbidden:
      pass

  def run(self, token):
    loop = self.loop
    client = PythonShellBot()

    def stop_loop_on_completion(f):
      loop.stop()

    self_start = loop.create_task(self.start(token))
    client_start = loop.create_task(client.start(token))

    future = asyncio.gather(self_start, client_start, loop=loop)
    future.add_done_callback(stop_loop_on_completion)

    try:
      loop.run_forever()
    except KeyboardInterrupt:
      pass
    finally:
      future.remove_done_callback(stop_loop_on_completion)
      _cleanup_loop(loop)
    
    if not future.cancelled():
      try:
        return future.result()
      except KeyboardInterrupt:
        return None