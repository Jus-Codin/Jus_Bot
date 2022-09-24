from __future__ import annotations

from .pages import Page
from ..utils import embed_template
from .interface import Interface, InterfaceView

from typing import List, Union

import discord

# You can change these emojis and rows to use your own
EMOJIS = {
  "start" : "\N{BLACK LEFT-POINTING DOUBLE TRIANGLE}",
  "back" : "\N{BLACK LEFT-POINTING TRIANGLE}",
  "page" : None,
  "forward" : "\N{BLACK RIGHT-POINTING TRIANGLE}",
  "end" : "\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE}",
  "stop" : "\N{BLACK SQUARE FOR STOP}"
}

ROW = {
  "start" : 2,
  "back" : 2,
  "page" : 2,
  "forward" : 2,
  "end" : 2,
  "stop" : 3,
  "return" : 3,
  "select" : 2
}

class _PageSelect(InterfaceView):
  """
  Interface to select a page to go to
  """
  parent: Paginator # I sincerely hope that this is fine...

  EMBED = discord.Embed(title="Page Browser", description="Please choose a page")

  @discord.ui.button(label="Back", style=discord.ButtonStyle.primary, emoji=EMOJIS["back"], row=ROW["return"])
  async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.parent.set_view(self.parent.default_view)
    await self.parent.update(interaction)

  @discord.ui.select(placeholder="Select a page...", row=ROW["select"])
  async def page_select(self, interaction: discord.Interaction, select: discord.ui.Select):
    page = int(select.values[0])
    self.parent._current_page = page
    self.parent.set_view(self.parent.default_view)
    await self.parent.update(interaction)

  @discord.ui.button(label="Close", style=discord.ButtonStyle.danger, emoji=EMOJIS["stop"], row=ROW["stop"])
  async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    await self.message.delete()
    self.stop()




class PaginatorView(InterfaceView):
  """
  Default view for the Paginator
  """
  parent: Paginator # I sincerely hope that this is fine...

  @discord.ui.button(style=discord.ButtonStyle.primary, emoji=EMOJIS["start"], row=ROW["start"])
  async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.parent._current_page = 0
    await self.parent.update(interaction)

  @discord.ui.button(style=discord.ButtonStyle.primary, emoji=EMOJIS["back"], row=ROW["back"])
  async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.parent._current_page -= 1
    await self.parent.update(interaction)

  @discord.ui.button(style=discord.ButtonStyle.secondary, emoji=EMOJIS["page"], row=ROW["page"])
  async def page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    view = _PageSelect(self.parent)

    # We need to get all the pages in the paginator
    for i, page in enumerate(self.parent.pages):
      title = page.title if page.title is not None else f"Page {i+1}"
      if len(title) > 100:
        title = title[:97] + "..."
      preview = page.preview
      if len(preview) > 100:
        preview = preview[:97] + "..."
      view.page_select.add_option(label=f"{i+1}. {title}", value=str(i), description=preview)
    
    self.parent.set_view(view)
    await self.parent.update(
      interaction,
      embed=embed_template(
        bot=self.parent.bot,
        author=self.parent.user,
        embed=_PageSelect.EMBED
      )
    )

  @discord.ui.button(style=discord.ButtonStyle.primary, emoji=EMOJIS["forward"], row=ROW["forward"])
  async def forward_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.parent._current_page += 1
    await self.parent.update(interaction)

  @discord.ui.button(style=discord.ButtonStyle.primary, emoji=EMOJIS["end"], row=ROW["end"])
  async def end_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.parent._current_page = self.parent.page_count - 1
    await self.parent.update(interaction)

  @discord.ui.button(label="Close", style=discord.ButtonStyle.danger, emoji=EMOJIS["stop"], row=ROW["stop"])
  async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    await self.message.delete()
    self.stop()



class Paginator(Interface):
  """
  Class to make pages for discord messages
  """
  view: Union[_PageSelect, PaginatorView]
  max_size = 2000

  def __init__(self, pages: List[Page], **options):
    # NOTE: This is to fix a potential issue for the page browser
    # as a Select can only hold 25 values. This could be fixed by
    # only showing the 24 pages around the current page, but that
    # will be just added to the TODO list
    if len(pages) > 25:
      raise ValueError("Number of pages exceeds 25")
      
    for i, page in enumerate(pages):
      self._check(page, i)
    self._pages: List[Page] = list(pages)

    self._current_page = 0

    custom_view = PaginatorView(self)

    super().__init__(custom_view=custom_view, **options)

  def _check(self, page: Page, page_index: int):
    if not isinstance(page, Page):
      raise TypeError(f"Page {page_index+1} is not a 'Page' type")
    elif len(page) > self.max_size:
      raise ValueError(f"Page {page_index+1} exceeds the size limit of 2000 characters")

  @property
  def pages(self):
    """Returns a list of pages"""
    return self._pages

  @property
  def page_count(self):
    """Returns the number of pages"""
    return len(self._pages)

  @property
  def page(self) -> Page:
    """Returns the current `Page`"""
    return self.pages[self.current_page]

  @property
  def current_page(self):
    """Returns the current page the paginator is on"""
    self._current_page = max(0, min(self.page_count-1, self._current_page))
    return self._current_page

  @property
  def kwargs(self):
    if self.view == self.default_view:
      self.view.page_button.label = f"{self.current_page+1}/{self.page_count}"

      self.view.enable_all()

      if self.current_page == 0:
        self.view.start_button.disabled = True
        self.view.back_button.disabled = True
      if self.current_page == self.page_count - 1:
        self.view.forward_button.disabled = True
        self.view.end_button.disabled = True
      if self.page_count == 1:
        self.view.page_button.disabled = True
        
    return {
      **self.page.kwargs,
      "view": self.view
    }
