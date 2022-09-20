from __future__ import annotations

import discord
from discord.ui import View

from typing import Union, Optional, TYPE_CHECKING

from discord.ext.commands import Context

if TYPE_CHECKING:
  from ..bot import JusBot

class InterfaceView(View):
  """The view used by `Interface`, not meant to be sent directly"""

  def __init__(
    self,
    parent: Interface,
    timeout: Optional[float] = 60.0,
    delete_on_timeout: bool = False
  ):
    super().__init__(timeout=timeout)

    self.parent = parent

    self.delete_on_timeout: bool = delete_on_timeout

  @property
  def message(self):
    return self.parent.message

  def disable_all(self):
    for child in self.children:
      child.disabled = True

  def enable_all(self):
    for child in self.children:
      child.disabled = False
  
  def add_view(self, custom_view: View):
    """Add items from a custom view"""
    if isinstance(custom_view, View):
      for child in custom_view.children:
        self.add_item(child) # They should handle rows themselves
    else:
      raise TypeError(f'expected View not {custom_view.__class__!r}')

  async def interaction_check(self, interaction: discord.Interaction):
    if self.parent.user == interaction.user:
      return True
    else:
      await interaction.response.send_message('This is not for you!', ephemeral=True)
      return False

  async def on_timeout(self): # TODO: Fix error where message cannot be found on timeout
    if self.delete_on_timeout:
      await self.parent.message.delete()
    else:
      self.disable_all()
      await self.parent.update()
    self.stop()



class Interface:
  """The base class for all UI Interfaces
  This is a model that can be used to respond to a command

  Parameters
  ----------
  timeout: Optional[:class:`float`]
    Timeout in seconds before no longer accepting any input, defaults to 60 seconds
  delete_on_timeout: :class:`bool`
    Whether to delete the message on timeout
  custom_view: Optional[:class:`InterfaceView`]
    A custom view to use instead of the default `InterfaceView` which is empty
  """

  def __init__(
    self,
    timeout: Optional[float] = 60.0,
    delete_on_timeout: bool = False,
    custom_view: InterfaceView = None
  ):

    self.delete_on_timeout: bool = delete_on_timeout

    self._view = custom_view or InterfaceView(self, timeout, delete_on_timeout)
    self._current_view = self._view

    self.bot: JusBot = None

    self.interface_sent: bool = False

  def set_view(self, view):
    """Change the view of the interface"""
    self._current_view = view

  @property
  def view(self) -> View:
    """The view that is currently being displayed by the interface"""
    return self._current_view

  @property
  def default_view(self) -> View:
    """The default view that will be displayed by default by the interface"""
    return self._view

  async def send_to(self, ctx: Union[Context, discord.Interaction], **kwargs) -> Union[discord.Message, discord.InteractionMessage]:
    # Regarding this, I feel that it is better to update self.kwargs with kwargs than the other
    # way around. I might change this in the future
    kwargs = {**self.kwargs, **kwargs}
    if isinstance(ctx, Context):
      self.user = ctx.author
      self.message = await ctx.reply(**kwargs)
    elif isinstance(ctx, discord.Interaction):
      self.user = ctx.user
      if ctx.response.is_done():
        self.message = await ctx.followup.send(wait=True, **kwargs)
      else:
        await ctx.response.send_message(**kwargs)
        self.message = await ctx.original_response()
    else:
      raise TypeError(f'expected Context or ApplicationContext not {ctx.__class__!r}')
    self.bot = ctx.bot
    self.interface_sent = True
    return self.message

  @property
  def kwargs(self) -> dict:
    """Returns the arguments that will be sent.
    This can be changed in subclasses to customise the content sent
    """
    return {
      "view": self.view
    }

  async def update(self, interaction: discord.Interaction=None, **kwargs):
    """Updates the Interface with the message parameters provided
    Interaction parameter can be optionally provided to respond to it
    """
    kwargs = {**self.kwargs, **kwargs}
    if self.interface_sent:
      if interaction is not None:
        if interaction.response.is_done():
          self.message = await interaction.original_response()
          self.message = await self.message.edit(**kwargs)
        else:
          await interaction.response.edit_message(**kwargs)
          self.message = await interaction.original_response()
      else:
        self.message = await self.message.edit(**kwargs)
    else:
      raise RuntimeError('message has not been sent')