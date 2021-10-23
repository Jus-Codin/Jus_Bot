from discord import Bot
from .base import JusBotBase
from .Web import open_web

__version__ = '4.0.0a'
__all__ = (
  'Jus_Bot',
  'open_web'
)

class Jus_Bot(JusBotBase, Bot):
  '''Main bot with modified BotBase'''

  pass
