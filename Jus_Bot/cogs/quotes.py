from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext.commands import Cog, command, Context
from discord.ext.tasks import loop

from ..utils import embed_template, error_template
from ..quotes import QODClient, RateLimitExceeded

if TYPE_CHECKING:
  from ..bot import JusBot
  from ..quotes.models import Quote
  from typing import Dict

class Quotes(Cog):
  """Get some fancy quotes"""

  def __init__(self, bot: JusBot, hidden: bool, suppress: bool):
    self.bot = bot
    self.hidden = hidden
    self.suppress = suppress

    self.client = QODClient()

    self.qods: Dict[str, Quote] = {}
    self.categories = ()

    self.update_qod.start()

  @loop(hours=24)
  async def update_qod(self):
    try:
      self.categories = self.categories or await self.client.categories()
      for category in self.categories:
        self.qods[category] = await self.client.qod(category=category)
    except RateLimitExceeded:
      pass

  @command(help="Gives a Quote of the Day")
  async def qod(self, ctx: Context, category="inspire"):
    quote = self.qods.get(category)
    if quote is None:
      embed = error_template(self.bot, ctx.author, description="Unknown category")
    else:
      embed = embed_template(self.bot, ctx.author, title="Quote of the Day", description=f"\"{quote.quote}\"\n~{quote.author}")
    await ctx.reply(embed=embed)

  @command(help="Get all available Quote of the Day categories")
  async def categories(self, ctx: Context):
    categories = self.categories
    if categories:
      embed = embed_template(self.bot, ctx.author, title="Available categories", description="\n".join(categories))
    else:
      embed = embed_template(self.bot, ctx.author, title="Rate Limited", description="Bot is currently rate limited, please try again later")
    await ctx.reply(embed=embed)