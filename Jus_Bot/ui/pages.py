from __future__ import annotations

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
  from typing import Optional, List
  from discord import Embed
  from discord.ui import View

class MISSING:
  ...

class Page:
  """Represents a page, not meant to be used directly.

  Parameters
  ----------
  content: Optional[:class:`str`]
    The content of the message to send
  embed: :class:`~discord.Embed`
    The rich embed for the message
  embeds: List[:class:`~discord.Embed`]
    A list of embeds to send. Must be a maximum of 10
  file: :class:`~discord.File`
    The file to upload
  files: List[:class:`~discord.File`]
    A list of files to upload. Must be a maximum of 10
  """

  def __init__(
    self,
    content: Optional[str]=None,
    *,
    embed: Embed=None,
    embeds: List[Embed]=None,
    title: Optional[str]=MISSING,
    preview: Optional[str]=MISSING,
    **options
  ):
    self.content = content
  
    if embed and embeds:
      raise ValueError("'embed' and 'embeds' arguments cannot both be specified")
    self.embed = embed
    self.embeds = embeds

    self._title = title
    self._preview = preview

    self.options = options

  @property
  def title(self):
    if self._title is not MISSING:
      return self._title
    elif self.embed is not None:
      return self.embed.title
    else:
      return None

  @property
  def preview(self):
    if self._preview is not MISSING:
      return self._preview
    elif self.content is not None:
      return self.content
    elif self.embed is not None:
      return self.embed.description
    else:
      return None

  @property
  def kwargs(self):
    kwargs = {
      "content": self.content,
      **self.options
    }
    if self.embed is not None:
      kwargs["embed"] = self.embed
    elif self.embed is not None:
      kwargs["embeds"] = self.embeds
    return kwargs

  def __len__(self):
    return len(self.content) if self.content else 0