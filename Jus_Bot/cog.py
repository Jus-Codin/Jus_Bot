from __future__ import annotations

from discord.ext.commands import Cog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from .bot import JusBot

class JusCog(Cog):
  """
  The custom cog used for the `JusBot`

  Parameters
  ----------
  bot: :class:`JusBot`
    The bot that loaded this cog
  hidden: :class:`bool`
    Whether the cog should be hidden.
    Defaults to `False`
  suppress: :class:`bool`
    Whether the cog should suppress errors.
    Defaults to `False`
  """

  def __init__(self, bot: JusBot, hidden=False, suppress=False):
    self.bot = bot
    self.hidden = hidden
    self.suppress = suppress