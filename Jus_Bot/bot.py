from __future__ import annotations

from datetime import datetime

from discord.ext.commands import Bot

from pyston.exceptions import InvalidLanguage, TooManyRequests

from .config import DEFAULT_CONFIG_DICT, ConfigManager
from .cogs import cogs
from .piston import get_codeblocks, run_code, process_output
from .utils import handle_error

import typing

if typing.TYPE_CHECKING:
  from discord import Colour, Message
  from discord.ext.commands import Context, errors
  from .config import SetupConfigDict

class JusBot(Bot):
  """
  Represents a bot connecting to the Discord API

  Parameters
  ----------
  setup_config: :class:`SetupConfigDict`
  """

  # TODO: Implement error handling

  def __init__(self, setup_config: SetupConfigDict, *args, **kwargs):
    config_dict = kwargs.pop('config', DEFAULT_CONFIG_DICT)
    self.config = ConfigManager(setup_config=setup_config, config_dict=config_dict)
    self.token = self.config['token']

    self.prefix = self.config['prefix']
    if self.prefix[-1].isalpha():
      self.prefix += " "

    self.suppress = self.config['suppress']

    super().__init__(
      help_command=None, # Using custom help command
      status=self.config['status'],
      activity=self.config['activity_type'](self.config['activity_message']),
      intents=self.config["intents"],
      case_insensitive=self.config['case_insensitive']
      *args, 
      **kwargs
    )

    for cog in cogs:
      # TODO: Implement cog configurations
      print(f"Loaded cog {cog}")
      self.add_cog(cog(self, False, False))

  def run(self, *args, **kwargs):
    self.start_time = datetime.now()
    super().run(self.token, *args, **kwargs)

  async def on_message(self, message: Message):
    if message.author.bot:
      return

    codes = get_codeblocks(message.content)

    if codes and self.enable_eval:
      async with message.channel.typing():
        for lang, code in codes:
          if not code.startswith("i#"):
            mention = message.author.mention
            try:
              output = await run_code(lang, code)
              s = await process_output(output, mention)
              await message.reply(s)
            except InvalidLanguage:
              await message.reply(f"Unknown language, {mention}")
            except TooManyRequests:
              await message.reply(f"Bot is currently handling too many requests, try again later, {mention}")
    else:
      await self.process_commands(message)


  async def on_command_error(self, ctx: Context, error: errors.CommandError):
    """|coro|

    The default command error handler provided by the bot
    """
    if self.extra_events.get('on_command_error', None):
      return

    command = ctx.command
    if command and command.has_error_handler():
      return

    cog = ctx.cog
    if cog and (cog.has_error_handler() or cog.suppress):
      return

    await handle_error(self, ctx, error)

  @property
  def uptime(self) -> str:
    """Get the uptime of the bot"""
    timediff = datetime.now() - self.start_time
    hours, remainder = divmod(timediff, 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    fmt = f'{hours}h, {minutes}m and {seconds}s'
    return (f'{days}d, ' + fmt) if days else fmt

  async def get_prefix(self, message: Message):
    if message.content.lower().startswith(self.prefix):
      return message.content[:len(self.prefix)]
    else:
      return [self.prefix, f"<@{self.user.id}> ", f"<@!{self.user.id}> "]

  @property
  def enable_eval(self) -> bool:
    """Whether the bot will run code"""
    return self.config['enable_eval']

  @property
  def default_embed_colour(self) -> typing.Callable[[], Colour]:
    """The default colour for the bot's embeds"""
    return self.config['default_colour']

  @property
  def error_embed_colour(self) -> typing.Callable[[], Colour]:
    """The default colour for the bot's error embeds"""
    return self.config['error_colour']

  @property
  def error_msg(self) -> typing.Dict[str, list]:
    """The random error messages for the bot"""
    return self.config['error_msg']

  