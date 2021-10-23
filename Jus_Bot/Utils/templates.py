import discord
from discord.ext import commands
from datetime import datetime
from random import choice
import json

with open('./Jus_Bot/Data/error_msg.json') as file:
  file = json.loads(file.read())
  error_msg = file['Default']

def embed_template(ctx: commands.Context, **kwargs) -> discord.Embed:
  bot = ctx.bot
  user = ctx.author
  colour = kwargs.pop('colour', None) or discord.Colour.from_rgb(178, 255, 255)
  timestamp = kwargs.pop('timestamp', None) or datetime.now()
  embed = discord.Embed(colour=colour, timestamp=timestamp, **kwargs)
  embed.set_footer(text=f'Requested by {user!s}', icon_url=user.display_avatar.url)
  embed.set_author(name=bot.user.name, icon_url=bot.user.display_avatar.url)
  return embed

def error_template(ctx: commands.Context, type=None, **kwargs) -> discord.Embed:
  bot = ctx.bot
  user = ctx.author
  title = kwargs.pop('title', None)
  colour = kwargs.pop('colour', None) or discord.Colour.brand_red()
  timestamp = kwargs.pop('timestamp', None) or datetime.now()
  if not title:
    if type:
      title = choice(file[type]+error_msg)
    else:
      title = choice(error_msg)
  embed = discord.Embed(title=title, colour=colour, timestamp=timestamp, **kwargs)
  embed.set_footer(text=f'Requested by {user!s}', icon_url=user.display_avatar.url)
  embed.set_author(name=bot.user.name, icon_url=bot.user.display_avatar.url)
  return embed