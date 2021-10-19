from .paginator import Paginator
from typing import List, Coroutine

import discord

EMOJI_DEFAULT = {
  'close' : '\N{BLACK SQUARE FOR STOP}',
  'start' : '\N{BLACK LEFT-POINTING DOUBLE TRIANGLE}',
  'back' : '\N{BLACK LEFT-POINTING TRIANGLE}',
  'forward' : '\N{BLACK RIGHT-POINTING TRIANGLE}',
  'end' : '\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE}',
}

class _PaginatorButton(discord.ui.Button['Paginator']):
  def __init__(self, emoji: str, **kwargs):
    super().__init__(style=discord.ButtonStyle.primary, label=emoji, row=4)

  async def callback(self, interaction: discord.Interaction):
    close, start, back, forward, end = self.view.emojis.values()
    if self.label == close:
      await interaction.message.delete()
      self.view.stop()
      return
    elif self.label == start:
      self.view._current_page = 0
    elif self.label == back:
      self.view._current_page -= 1
    elif self.label == forward:
      self.view._current_page += 1
    elif self.label == end:
      self.view._current_page = self.view.page_count - 1

    await interaction.response.edit_message(**self.view.send_kwargs)


class PaginatorView(discord.ui.View):

  def __init__(self, paginator: Paginator, **kwargs):
    super().__init__()
    if not isinstance(paginator, Paginator):
      raise TypeError('paginatior must be an instance of Utils.Paginator')

    self._current_page = 0
    self.paginator = paginator
    
    self.emojis = kwargs.pop('emojis', EMOJI_DEFAULT)
    self.delete_message = kwargs.pop('delete_message', False)
    self.timeout = kwargs.pop('timeout', 60.0)

    if len(self.paginator._pages) > 1:
      for emoji in self.emojis.values():
        self.add_item(_PaginatorButton(emoji))
    else:
      self.add_item(_PaginatorButton(self.emojis['close']))

    self.template = {
      'content' : None,
      'embeds'  : [],
      'view'    : self
    }

  async def interaction_check(self, interaction: discord.Interaction):
    if self.user == interaction.user:
      return True
    else:
      await interaction.response.send_message('This is not for you!', ephemeral=True)
      return False

  async def on_timeout(self):
    if self.delete_message:
      await self.message.delete()
    else:
      for child in self.children:
        child.disabled = True
      await self.message.edit(view=self)
    self.stop()

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
      if embeds[-1].footer.text == discord.Embed.Empty:
        footer = page_num[1:]
      elif embeds[-1].footer.text.startswith(page_num[1:]):
        footer = embeds[-1].footer.text
      else:
        footer = page_num[1:] + '\n' + embeds[-1].footer.text
      embeds[-1] = embeds[-1].set_footer(text=footer, icon_url=embeds[-1].footer.icon_url)
      current_page['embeds'] = embeds
      if not current_page.get('content', None):
        current_page['content'] = self.user.mention
    elif content := current_page.get('content', None) or current_page.get('view', None):
      content += page_num
      current_page['content'] = content
    if view := current_page.pop('view', None):
      for item in view.children:
        self.add_item(item)
    return {**self.template, **current_page}

  async def send_to(self, ctx):
    self.user = ctx.author
    self.message = await ctx.send(**self.send_kwargs)





class _Choice(discord.ui.Select):
  
  def __init__(self, choices: List[discord.SelectOption], handler: Coroutine, **kwargs):
    super().__init__(
      options=choices,
      **kwargs
    )
    self.choices = choices
    self.handler = handler

  async def callback(self, interaction):
    await self.handler(self, interaction)

class ChoiceView(discord.ui.View):
  
  def __init__(self, choices: List[discord.SelectOption], handler: Coroutine, **kwargs):
    super().__init__()
    self.delete_message = kwargs.pop('delete_message', False)
    self.timeout = kwargs.pop('timeout', 60.0)
    self.timeout_func = kwargs.pop('timeout_func', None)
    self.add_item(
      _Choice(choices, handler, **kwargs)
    )

  async def interaction_check(self, interaction: discord.Interaction):
    if self.user == interaction.user:
      return True
    else:
      await interaction.response.send_message('This is not for you!', ephemeral=True)
      return False

  async def on_timeout(self):
    if self.delete_message:
      await self.message.delete()
    elif self.timeout_func is not None:
      await self.timeout_func(self)
    else:
      for child in self.children:
        child.disabled = True
      await self.message.edit(view=self)
    self.stop()

  async def send_to(self, ctx, **kwargs):
    if isinstance(ctx, discord.Interaction):
      self.user = ctx.user
      self.message = await ctx.response.send_message(view=self, **kwargs)
    else:
      self.user = ctx.author
      self.message = await ctx.send(view=self, **kwargs)