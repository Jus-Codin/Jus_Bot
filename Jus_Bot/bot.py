from __future__ import annotations

from datetime import datetime

from discord.ext.commands import Bot

from pyston.exceptions import InvalidLanguage, TooManyRequests

from .config import DEFAULT_CONFIG_DICT, ConfigManager
from .cogs import cogs
from .piston import get_codeblocks, run_code, process_output
from .errors import ErrorHandler
from .help import HelpCog

from typing import TYPE_CHECKING, Callable, Dict, Optional

import discord

if TYPE_CHECKING:
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
    config_dict = kwargs.pop("config", DEFAULT_CONFIG_DICT)
    self.config = ConfigManager(setup_config=setup_config, config_dict=config_dict)
    self.token = self.config["token"]

    self.prefix = self.config["prefix"]
    if self.prefix[-1].isalpha():
      self.prefix += " "

    self.suppress = self.config["suppress"]

    error_handler = self.config["error_handler"]

    if not issubclass(error_handler, ErrorHandler):
      raise TypeError(
        f"Error handler must be a `ErrorHandler` type, not {error_handler.__class__}"
      )
    
    self.error_handler = error_handler(self)

    super().__init__(
      command_prefix=self.prefix,
      help_command=None, # Using custom help command
      status=self.config["status"],
      activity=self.config["activity_type"](self.config["activity_message"]),
      intents=self.config["intents"],
      case_insensitive=self.config["case_insensitive"]
      *args, 
      **kwargs
    )

  async def setup_hook(self):
    for cog in cogs:
      # TODO: Implement cog configurations
      await self.add_cog(cog(self, False, False))
      print(f"Loaded cog {cog}")

    print("Setting up help command...")

    help_cog = self.config["help_cog"]

    if not issubclass(help_cog, HelpCog):
      raise TypeError(f"help_cog must be a `HelpCog` type, not {help_cog.__class__}")

    self._help_cog = None

    # TODO: Implement cog configurations, currently this will just use bot.suppress
    await self.set_help_cog(help_cog(self, self.suppress, False))

    self.start_time = datetime.now()

  def run(self, *args, **kwargs):
    super().run(self.token, *args, **kwargs)

  async def on_message(self, message: Message):
    if message.author.bot:
      return

    codes = get_codeblocks(message.content)

    if codes and self.enable_eval and not code.startswith("i#"):
      async with message.channel.typing():
        for lang, code in codes:
          mention = message.author.mention
          try:
            output = await run_code(lang, code)
            s = await process_output(output, mention)
            await message.reply(discord.utils.escape_mentions(s))
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
    if self.extra_events.get("on_command_error", None):
      return

    await self.error_handler.handle_error(ctx, error)

  @property
  def uptime(self) -> str:
    """Get the uptime of the bot"""
    timediff = datetime.now() - self.start_time
    hours, remainder = divmod(int(timediff.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    fmt = f"{hours}h, {minutes}m and {seconds}s"
    return (f"{days}d, " + fmt) if days else fmt

  async def get_prefix(self, message: Message):
    if message.content.lower().startswith(self.prefix):
      return message.content[:len(self.prefix)]
    else:
      return [self.prefix, f"<@{self.user.id}> ", f"<@!{self.user.id}> "]

  @property
  def wolfram_appid(self) -> str:
    return self.config["wolfram_appid"]

  @property
  def enable_eval(self) -> bool:
    """Whether the bot will run code"""
    return self.config['enable_eval']

  @property
  def default_embed_colour(self) -> Callable[[], Colour]:
    """The default colour for the bot"s embeds"""
    return self.config["default_colour"]

  @property
  def error_embed_colour(self) -> Callable[[], Colour]:
    """The default colour for the bot"s error embeds"""
    return self.config["error_colour"]

  @property
  def error_msg(self) -> Dict[str, list]:
    """The random error messages for the bot"""
    return self.config["error_msg"]

  async def set_help_cog(self, cog: Optional[HelpCog]):
    if cog is not None:
      if not isinstance(cog, HelpCog):
        raise TypeError(f"help_cog must be an instance of `HelpCog`, not {cog.__class__}")
      if self._help_cog is not None:
        await self.remove_cog(self._help_cog.qualified_name)
      self._help_cog = cog
      await self.add_cog(cog)
    elif self._help_cog is not None:
      await self.remove_cog(self._help_cog.qualified_name)
      self._help_cog = None
    else:
      self._help_cog = None

  @property
  def error_handler(self) -> ErrorHandler:
    return self._error_handler

  @error_handler.setter
  def error_handler(self, value: ErrorHandler) -> None:
    if not isinstance(value, ErrorHandler):
      raise TypeError(
        f"Error handler must be a `ErrorHandler` type, not {value.__class__}"
      )
    self._error_handler = value