from __future__ import annotations

import re

from typing import TYPE_CHECKING, Optional

from datetime import datetime
from random import choice

import discord

if TYPE_CHECKING:
  from .bot import JusBot

def embed_template(bot: JusBot, author: discord.User=None, embed: discord.Embed=None, **options) -> discord.Embed:
  colour = options.pop('colour', None) or options.pop('color', None) or bot.default_embed_colour()
  timestamp = options.pop('timestamp', None) or datetime.now()

  if embed is None:
    embed = discord.Embed(colour=colour, timestamp=timestamp, **options)
  else:
    if embed.timestamp is None:
      embed.timestamp = timestamp
    if embed.colour is None:
      embed.colour = colour

  if author is not None:
    embed.set_footer(text=f'Requested by {author!s}', icon_url=author.display_avatar.url)
  embed.set_author(name=bot.user.name, icon_url=bot.user.display_avatar.url)
  return embed



class ErrorType:
  DEFAULT = "default"
  NOT_FOUND = "not_found"
  BAD_PERMS = "bad_perms"



error_msg = None

def error_template(bot: JusBot, author: discord.User=None, err_type: Optional[ErrorType]=None, **options) -> discord.Embed:
  global error_msg
  colour = options.pop('colour', None) or options.pop('color', None) or bot.error_embed_colour()
  title = options.pop('title', None)
  timestamp = options.pop('timestamp', None) or datetime.now()
  if not title:
    error_msg = bot.error_msg
    if err_type is not None:
      title = choice(error_msg[err_type]+error_msg[ErrorType.DEFAULT])
    else:
      title = choice(error_msg[ErrorType.DEFAULT])
  embed = discord.Embed(title=title, colour=colour, timestamp=timestamp, **options)
  if author is not None:
    embed.set_footer(text=f'Requested by {author!s}', icon_url=author.display_avatar.url)
  embed.set_author(name=bot.user.name, icon_url=bot.user.display_avatar.url)
  return embed



def functionise(string: str) -> str:
  """Converts pascalcase strings to PEP 8 standard function names
  Note that this most likely does not cover all possible cases
  """
  string = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
  return re.sub('([a-z0-9])([A-Z])', r'\1_\2', string).lower()