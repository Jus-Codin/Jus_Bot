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

class PaginatorInterface:
  """
  Message and reaction based interface for paginators.
  """
  max_page_size = 2000

  def __init__(self, bot: commands.Bot, paginator: commands.Paginator, **kwargs):
    if not isinstance(paginator, commands.Paginator):
      raise TypeError('paginatior must be an instance on commands.Paginator')

    self._current_page = 0

    self.bot = bot

    self.message = None
    self.paginator = paginator

    self.emojis = kwargs.pop('emoji', EMOJI_DEFAULT)
    self.timeout = kwargs.pop('timeout', 7200)
    self.delete_message = kwargs.pop('delete_message', False)

    self.page_reactions_sent = False

    self.task: asyncio.Task = None
    self.send_lock: asyncio.Event = asyncio.Event()
    self.update_lock: asyncio.Lock = asyncio.Semaphore(value=kwargs.pop('update_max', 2))

    if self.page_size > self.max_page_size:
      raise ValueError(
        f'Paginator passed has too large of a page size for this interface. '
        f'({self.page_size} > {self.max_page_size})'
      )

  @property
  def pages(self):
    paginator_pages = list(self.paginator._pages)
    if len(self.paginator._current_page) > 1:
      paginator_pages.append('\n'.join(self.paginator._current_page) + '\n' + (self.paginator.suffix or ''))
    
    return paginator_pages

  @property
  def page_count(self):
    return len(self.pages)

  @property
  def page_size(self) -> int:
    page_count = self.page_count
    return self.paginator.max_size + len(f'\nPage {page_count}/{page_count}')

  @property
  def current_page(self):
    self._current_page = max(0, min(self.page_count -1, self._current_page))
    return self._current_page

  @property
  def send_kwargs(self) -> dict:
    current_page = self.current_page
    page_num = f'\nPage {current_page + 1}/{self.page_count}'
    content = self.pages[current_page] + page_num
    return {'content': content}

  async def send_to(self, destination: discord.abc.Messageable):
    self.message = await destination.send(**self.send_kwargs)
    await self.message.add_reaction(self.emojis.close)

    self.send_lock.set()

    if self.task:
      self.task.cancel()

    self.task = self.bot.loop.create_task(self.wait_loop())

    if not self.page_reactions_sent and self.page_count > 1:
      await self.send_all_reactions()
    
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
        payload.message.id == self.message.id,
        emoji,
        emoji in self.emojis,
        payload.user_id != self.bot.user.id
      )

      return all(tests)

    try:
      while not self.bot.is_closed():
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
          await self.message.remove.reaction(emoji, self.bot.user)
        except (discord.Forbidden, discord.NotFound):
          pass

  async def update(self):
    if self.update_lock.locked():
      return
    
    await self.send_lock.wait()

    async with self.update_lock:
      if self.update_lock.locked():
        await asyncio.sleep(1)

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

# Work in progress
"""
class PaginatorEmbedInterface(PaginatorInterface):
  def __init__(self, *args, **kwargs):
    self._embed = kwargs.pop('embed', None) or discord.Embed()
    super().__init__(*args, **kwargs)

  @property
  def send_kwargs(self) -> dict:
    current_page = self.current_page
    self._embed.set_author(name='Jus_Bot', icon_url=self.bot.user.avatar_url)
    self._embed.description = self.pages[current_page]
    self._embed.set_footer(text=f'Page {current_page + 1}/{self.page_count}')
    return {'embed': self._embed}

  max_page_size =2048

  @property
  def page_size(self) -> int:
    return self.paginator.max_size
    """