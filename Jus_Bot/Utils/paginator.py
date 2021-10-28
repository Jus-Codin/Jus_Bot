import collections
import asyncio
import discord

from discord.ext import commands

EmojiSettings = collections.namedtuple('EmojiSettings', 'start back forward end close')

EMOJI_DEFAULT = EmojiSettings(
    start="\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}",
    back="\N{BLACK LEFT-POINTING TRIANGLE}",
    forward="\N{BLACK RIGHT-POINTING TRIANGLE}",
    end="\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}",
    close="\N{BLACK SQUARE FOR STOP}"
)

class Paginator:
  """
  Class to make pages for discord messages
  """
  max_size = 2000

  def __init__(self, pages: list=[], **kwargs):
    if not isinstance(pages, list):
      raise TypeError('pages has to be a list')
    self._check(*pages)
    self._pages = pages

  def _check(self, *pages):
    for i in range(len(pages)):
      if isinstance(pages[i], str):
        if len(pages[i]) > self.max_size:
          raise ValueError(f'Page {i+1} has more than 2000 characters')
      if not isinstance(pages[i], dict):
        raise TypeError('Page must be an Embed, File, or String')

  def add_page(self, page: str, index=-1):
    """Add a page"""
    self._check(*page)
    if index == -1:
      self._pages.append(page)
    else:
      self._pages.insert(index)
  
  def delete_page(self, index: int):
    """Delete a page"""
    self._pages.pop(index)

  def clear(self):
    """Clears all pages in paginator"""
    self._pages = []

  @property
  def pages(self):
    """Returns rendered list of pages"""
    return self._pages