import collections
import asyncio
import discord
import typing

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
  max_size = 1990#Less than actual limit because page numbers are inserted on a new line

  def __init__(self, pages: typing.List[dict]=[], **kwargs):
    if not isinstance(pages, list):
      raise TypeError('pages has to be a list')
    self._check(*pages)
    self._pages = pages

  def _check(self, *pages: typing.Union[typing.List[dict], dict]):
    for i in range(len(pages)):
      if content := pages[i].get('content', None):
        if len(content) > self.max_size:
          raise TypeError(f'Page {i+1} has too many characters')

  def add_page(self, index=-1, **page):
    """Add a page"""
    self._check(page)
    if index == -1:
      self._pages.append(page)
    else:
      self._pages.insert(index, page)
  
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

class PaginatorInterface:
  """
  Message and reaction based interface for paginators.
  """
  template = {
    'content' : None,
    'embeds'  : [],
    'view'    : None
  }

  def __init__(self, bot: commands.Bot, paginator: Paginator, **kwargs):
    if not isinstance(paginator, Paginator):
      raise TypeError('paginatior must be an instance of Utils.Paginator')

    self._current_page = 0

    self.bot = bot

    self.message = None
    self.paginator = paginator

    self.emojis = kwargs.pop('emoji', EMOJI_DEFAULT)
    self.timeout = kwargs.pop('timeout', 7200)
    self.delete_message = kwargs.pop('delete_message', False)

    self.page_reactions_sent = False

    self.task: asyncio.Task = None

  @property
  def pages(self):
    paginator_pages = self.paginator._pages
    return paginator_pages

  @property
  def page_count(self):
    return len(self.pages)

  @property
  def current_page(self):
    self._current_page = max(0, min(self.page_count -1, self._current_page))
    return self._current_page

  @property
  def send_kwargs(self) -> dict:
    current_page = dict(self.pages[self.current_page])
    page_num = f'\nPage {self.current_page + 1}/{self.page_count}'
    if embeds := current_page.get('embeds', None):
      embeds[-1] = embeds[-1].set_footer(text=page_num[1:])
      current_page['embeds'] = embeds
    elif content := current_page.get('content', None) or current_page.get('view', None):
      content += page_num
      current_page['content'] = content
    return {**self.template, **current_page}

  async def send_to(self, ctx: commands.Context):
    self.ctx = ctx
    self.message = await ctx.send(**self.send_kwargs)
    await self.message.add_reaction(self.emojis.close)

    if self.task:
      self.task.cancel()

    self.task = self.bot.loop.create_task(self.wait_loop())

    if not self.page_reactions_sent and self.page_count > 1:
      await self.send_all_reactions()
    elif self.page_count == 1:
      self.page_reactions_sent = True
    
    return self

  async def send_all_reactions(self):
    for emoji in filter(None, self.emojis):
      try:
        await self.message.add_reaction(emoji)
      except discord.NotFound:
        break
    self.page_reactions_sent = True

  @property
  def closed(self):
    if not self.task:
      return False
    return self.task.done()

  async def wait_loop(self):
    start, back, forward, end, close = self.emojis

    def check(payload: discord.RawReactionActionEvent):
      emoji = payload.emoji
      if isinstance(emoji, discord.PartialEmoji) and emoji.is_unicode_emoji():
        emoji = emoji.name
      
      tests = (
        payload.user_id == self.ctx.author.id,
        payload.message_id == self.message.id,
        emoji,
        emoji in self.emojis,
        payload.user_id != self.bot.user.id
      )

      return all(tests)

    try:
      while not self.bot.is_closed():
        while not self.page_reactions_sent:
          await asyncio.sleep(0.1)
        payload = await self.bot.wait_for('raw_reaction_add', check=check, timeout=self.timeout)

        emoji = payload.emoji
        if isinstance(emoji, discord.PartialEmoji) and emoji.is_unicode_emoji():
          emoji = emoji.name

        if emoji == close:
          await self.message.delete()
          return

        if emoji == start:
          self._current_page = 0
        elif emoji == end:
          self._current_page = self.page_count - 1
        elif emoji == back:
          self._current_page -= 1
        elif emoji == forward:
          self._current_page += 1

        self.bot.loop.create_task(self.update())
      
        try:
          await self.message.remove_reaction(payload.emoji, discord.Object(id=payload.user_id))
        except discord.Forbidden:
          pass

    except (asyncio.CancelledError, asyncio.TimeoutError):
      if self.delete_message:
        return await self.message.delete()

      for emoji in filter(None, self.emojis):
        try:
          await self.message.remove_reaction(emoji, self.bot.user)
        except (discord.Forbidden, discord.NotFound):
          pass

  async def update(self):
    if not self.message:
      await asyncio.sleep(0.5)

    if not self.page_reactions_sent and self.page_count > 1:
      self.bot.loop.create_task(self.send_all_reactions())
      self.page_reactions_sent = True

    try:
      await self.message.edit(**self.send_kwargs)
    except discord.NotFound:
      if self.task:
        self.task.cancel()
