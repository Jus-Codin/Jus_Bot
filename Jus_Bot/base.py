from discord.ext.commands.bot import BotBase
from .CodeRunner import run_code, is_codeblock, format_code
from .Utils import error_handler
import discord

class JusBotBase(BotBase):
  '''Base bot to combine python shell and main features'''
  suppress = False
  running_code = True

  def run(self, *args, **kwargs):
    self.token = args[0]
    super().run(*args, **kwargs)

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
    elif is_codeblock(message.content) and self.running_code:
      lang, code = format_code(message.content)

      if code.startswith('i#') or not lang:
        return

      async with channel.typing():
        s = await run_code(code, message.author.mention, lang)

      await channel.send(s)
    else:
      await self.process_commands(message)