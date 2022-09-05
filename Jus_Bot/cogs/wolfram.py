from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext.commands import Cog, Context, command

from ..utils import embed_template
from ..wolframalpha import Client

if TYPE_CHECKING:
  from ..bot import JusBot

class WolframAlpha(Cog):
  """Get useful information from the Wolfram|Alpha v2.0 API"""

  def __init__(self, bot: JusBot, hidden: bool, suppress: bool):
    self.bot = bot
    self.hidden = hidden
    self.suppress = suppress
    self.appid = bot.wolfram_appid