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
  def inputBypass(text):
    return input({input_token} + str(text))

  globals()['input'] = inputBypass
  '''

  def __init__(self, bot: commands.Bot, ctx: commands.Context, channel: discord.TextChannel=None, delete_channel=False):
    self.repl: asyncio.subprocess.Process = None
    self.bot = bot
    self.ctx = ctx
    self.channel = channel if channel else ctx.channel
    self.delete_channel = delete_channel
    self.waiting_for_input = False
    self.output = None
    self.output_size = 0

    if delete_channel and not channel:
      raise ValueError('Cannot delete channel repl will be created from')

  async def read_output(self, process: asyncio.subprocess.Process):
    chars = await process.stdout.readline()
    if self.input_token in chars:
      self.waiting_for_input = True
      chars = chars.replace(self.input_token, '')
    self.output_size += sys.getsizeof(chars)
    self.output = chars.decode()

  async def await_input(self, process: asyncio.subprocess.Process):

    def check(message: discord.Message):
      tests = (
        message.channel == self.channel,
        message.author.id == self.ctx.author.id
      )

      return all(tests)
      
    if self.waiting_for_input:
      message = await self.bot.wait_for('on_message', check=check, timeout=30)
      text = message.content

      process.stdin.write(text)
      await process.stdin.drain()

  async def start_repl(self):

    await self.channel.send(f'Python {sys.version} on {sys.platform}')

    args = (
      sys.executable,
      '-E',
      '-I',
      '-i',
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
          await self.await_input(self.repl)
        except asyncio.TimeoutError:
          self.repl.terminate()
          break
      else:
        try:
          await asyncio.wait_for(self.read_output(self.repl), TIMEOUT)
        except asyncio.TimeoutError:
          await self.term_repl()
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