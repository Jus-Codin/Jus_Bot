from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext.commands import Cog, command, Context

from ..utils import embed_template

if TYPE_CHECKING:
  from ..bot import JusBot

class Diagnostics(Cog):

  def __init__(self, bot: JusBot, hidden: bool, suppress: bool):
    self.bot = bot
    self.hidden = hidden
    self.suppress = suppress

  @command(help='Get websocket latency')
  async def ping(self, ctx: Context):
    embed = embed_template(self.bot, ctx.author, title='Pong! \U0001F3D3', description=f'{round(self.bot.latency*1000,1)}ms')
    await ctx.reply(embed=embed)