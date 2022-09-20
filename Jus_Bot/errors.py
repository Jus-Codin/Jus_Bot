from __future__ import annotations

import sys

from asyncio import iscoroutinefunction
from traceback import print_exception, format_exception

from typing import TYPE_CHECKING, Optional

from .utils import functionise, error_template, ErrorType

if TYPE_CHECKING:
  from .bot import JusBot
  from discord.ext.commands import Context, errors

class ErrorHandler:
  """The error handler implementation for the bot
  This can be subclasses to customise the behavior of the bot's error handling
  """

  def __init__(self, bot: JusBot):
    self.bot = bot

  async def on_error_unhandled(self, ctx: Context, error: errors.CommandError):
    """|coro|
    The handles all errors that do not have a listener

    By default this method will just send a traceback
    """
    if self.bot.suppress:
      print(f"Ignoring exception in command {ctx.command}:", file=sys.stderr)
      print_exception(type(error), error, error.__traceback__, file=sys.stdout)
    else:
      trace_string = '\n'.join(format_exception(type(error), error, error.__traceback__))
      embed = error_template(self.bot, ctx.author, description=f"```\n{trace_string}```")
      await ctx.reply(embed=embed)

  async def handle_error(self, ctx: Context, error: errors.CommandError):
    command = ctx.command
    if command and command.has_error_handler():
      return

    cog = ctx.cog
    if cog and (cog.has_error_handler() or cog.suppress):
      return

    try:
      coro = getattr(self, "on_error_" + functionise(error.__class__.__name__))
    except AttributeError:
      coro = self.on_error_unhandled

    if not iscoroutinefunction(coro):
      raise TypeError(f"Error listener needs to be awaitable, not {coro.__class__}")

    await coro(ctx, error)



class DefaultErrorHandler(ErrorHandler):
  """The default error handler implementation for the bot
  
  # TODO: Rework configuration to allow for more customised messages
  """

  async def send_error_embed(self, msg: str, ctx: Context, err_type: Optional[ErrorType]=None):
    """Responds to a command that raises an error with an embed"""
    embed = error_template(self.bot, ctx, description=msg, err_type=err_type)
    await ctx.reply(embed=embed)

  async def on_error_command_not_found(self, context: Context, error: errors.CommandNotFound):
    await self.send_error_embed("**cOmMaNd DoEsN\'t ExIsT**", context.author, ErrorType.NOT_FOUND)

  async def on_error_missing_permissions(self, context: Context, error: errors.MissingPermissions):
    await self.send_error_embed("Your permissions are far inferior for this command", context.author, ErrorType.BAD_PERMS)

  async def on_error_not_owner(self, context: Context, error: errors.NotOwner):
    await self.send_error_embed("Only the owner of the bot can run this command", context.author, ErrorType.BAD_PERMS)

  async def on_error_no_private_message(self, context: Context, error: errors.NoPrivateMessage):
    await self.send_error_embed("This command can only be run in servers!", context.author)