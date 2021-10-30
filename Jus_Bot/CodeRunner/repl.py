import signal
import sys
import asyncio
import discord
from discord.ext import commands
from secrets import token_hex

OUTPUT_MAX = 1000000
TIMEOUT = 10

class replChannel:

  input_token = token_hex(4)

  init_code = f'''
_input = input
def inputBypass(text=''):
  print('{input_token}', end='')
  return _input(text).rstrip('\\n')

globals()['input'] = inputBypass
while True:
  code = inputBypass()
  print(code)
  eval(code)
'''

  def __init__(self, bot: commands.Bot, ctx: commands.Context, channel: discord.TextChannel=None, delete_channel=False):
    self.repl: asyncio.subprocess.Process = None
    self.bot = bot
    self.ctx = ctx
    self.channel = channel if channel else ctx.channel
    self.delete_channel = delete_channel
    self.waiting_for_input = True
    self.output = None
    self.output_size = 0

    if delete_channel and not channel:
      raise ValueError('Cannot delete channel repl will be created from')

  async def read_output(self, process: asyncio.subprocess.Process):
    print('Reading line')
    chars = await process.stdout.read(10000)
    print('Finished reading')
    chars = chars.decode()
    print(chars)
    print('Token:', self.input_token)
    if self.input_token in chars:
      self.waiting_for_input = True
      chars = chars.replace(self.input_token, '')
    self.output_size += sys.getsizeof(chars)
    print(chars)
    self.output = chars

  async def await_input(self, process: asyncio.subprocess.Process):

    def check(message: discord.Message):
      print(message.channel)
      print(message.author.id)
      print(self.channel)
      print('self.ctx.author.id')
      tests = (
        message.channel == self.channel,
        message.author.id == self.ctx.author.id
      )

      return all(tests)
      
    if self.waiting_for_input:
      message = await self.bot.wait_for('message', check=check, timeout=30)
      print('Message found')
      text = message.content.encode('utf-8')

      print(text)
      process.stdin.write(text)
      await process.stdin.drain()

      self.waiting_for_input = False

  async def start_repl(self):

    await self.channel.send(f'Python {sys.version} on {sys.platform}')

    args = (
      sys.executable,
      '-E',
      '-c',
      self.init_code
    )

    self.repl = await asyncio.create_subprocess_exec(
      *args,
      stdout = asyncio.subprocess.PIPE,
      stderr = asyncio.subprocess.STDOUT,
      stdin = asyncio.subprocess.PIPE
    )

    return await self.main_loop()

  async def main_loop(self):
    while self.repl.returncode is None:
      if self.waiting_for_input:
        try:
          print('waiting for input')
          await self.await_input(self.repl)
          print('input sent')
        except asyncio.TimeoutError:
          self.repl.terminate()
          break
      else:
        try:
          print('reading')
          await asyncio.wait_for(self.read_output(self.repl), TIMEOUT)
          if self.output:
            await self.channel.send(self.output)
          print('reading done')
        except asyncio.TimeoutError:
          self.repl.terminate()
          break

        if self.output_size > OUTPUT_MAX:
          await self.term_repl()
          break

    return self.repl.returncode if self.repl.returncode is not None else signal.SIGTERM

  async def term_repl(self):
    if self.delete_channel:
      try:
        await self.channel.delete()
      except discord.Forbidden:
        pass
      except discord.NotFound:
        pass
    self.repl.terminate()