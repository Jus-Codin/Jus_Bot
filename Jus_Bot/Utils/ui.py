from .paginator import Paginator
from typing import List

import discord

EMOJI_DEFAULT = {
  'close' : '\N{BLACK SQUARE FOR STOP}',
  'start' : '\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}',
  'back' : '\N{BLACK LEFT-POINTING TRIANGLE}',
  'forward' : '\N{BLACK RIGHT-POINTING TRIANGLE}',
  'end' : '\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}',
}

class PaginatorButton(discord.ui.Button['Paginator']):
  def __init__(self, label: str, **kwargs):
    super().__init__(style=discord.ButtonStyle.primary, label=label, row=4)

  async def callback(self, interaction: discord.Interaction):
    if interaction.user == self.view.user:
      close, start, back, forward, end = self.view.emojis.values()
      if self.label == close:
        await interaction.delete_original_message()
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

    for emoji in self.emojis.values():
      self.add_item(PaginatorButton(emoji))

    self.template = {
      'content' : None,
      'embeds'  : [],
      'view'    : self
    }

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
      embeds[-1] = embeds[-1].set_footer(text=footer)
      current_page['embeds'] = embeds
      if not current_page.get('content', None):
        current_page['content'] = 'Paginator'
    elif content := current_page.get('content', None) or current_page.get('view', None):
      content += page_num
      current_page['content'] = content
    if view := current_page.pop('view', None):
      for item in view.children:
        self.add_item(item)
    return {**self.template, **current_page}

  async def send_to(self, ctx):
    self.user = ctx.author
    await ctx.send(**self.send_kwargs)