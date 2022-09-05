from __future__ import annotations

from typing import TYPE_CHECKING, List, Mapping, Optional

from dataclasses import dataclass

from .utils import embed_template, error_template
from .ui.paginator import Paginator, Page
from .cog import JusCog

from discord.ext.commands import command, Context

if TYPE_CHECKING:
  from discord.ext.commands import Command
  from discord import Message

  from .bot import JusBot

@dataclass
class CommandHelp:
  """A minimal command class that holds all info needed for the help command"""
  name: str
  help: str
  hidden: bool
  aliases: Optional[List[str]]
  signature: str

@dataclass
class CategoryHelp:
  """A minimal cog class that holds all the info needed for the help command"""
  name: str
  description: str
  hidden: bool
  commands: List[CommandHelp]



class HelpManager:
  """The manager that stores all the info needed to build the help responses"""

  def __init__(self, bot: JusBot):
    self.bot = bot
    self._categories = {}
    for name, category in self.bot.cogs.items():
      if not isinstance(category, HelpCog):
        self._categories[name] = self._get_category_help(category)
    commands = self._get_uncategorised_commands()
    if commands is not None:
      self._categories[None] = self._get_uncategorised_commands()

  def _get_command_help(self, command: Command) -> CommandHelp:
    """Constructs a `CommandHelp` instance from a `Command`"""
    return CommandHelp(command.name, command.help, command.hidden, command.aliases, command.signature)

  def _get_category_help(self, category: JusCog) -> CategoryHelp:
    """Constructs a `CategoryHelp` instance from a `Cog`"""
    commands = []
    for command in category.walk_commands():
      commands.append(self._get_command_help(command))
    return CategoryHelp(category.qualified_name, category.description, category.hidden, commands)

  def _get_uncategorised_commands(self) -> CategoryHelp:
    """Constructs a special hidden `CategoryHelp` instance which stores all commands
    that are not in a cog
    """
    commands = [self._get_command_help(cmd) for cmd in self.bot.commands if cmd.cog is None]
    if commands:
      return CategoryHelp("Uncategorised", "Commands that are not in a category", True, commands)
    else:
      return None

  @property
  def categories(self) -> Mapping[str, CategoryHelp]:
    """A mapping of category names to category
    The uncategorised commands are stored with the key `NoneType`"""
    return self._categories

  @property
  def commands(self) -> List[CommandHelp]:
    """A list of all commands"""
    commands = []
    for category in self.categories.values():
      for command in category.commands:
        commands.append(command)
    return commands



class HelpCog(JusCog):
  """The base help cog"""

  def __init__(self, bot: JusBot, suppress: bool, show_hidden: bool):
    super().__init__(bot, hidden=True, suppress=suppress)
    self._show_hidden = show_hidden

  async def send_bot_help(self):
    """|coro|

    Handles the bot help page in the help command
    This function is called when the help command is called with no arguments

    You can override this method to customise the behaviour

    Note: You can access the invocation context with :attr:`HelpCommand.context`
    """

  async def send_category_help(self, category: CategoryHelp):
    """|coro|

    Handles the category help page in the help command
    This function is called when the help command is called with a cog as the argument

    You can override this method to customise the behaviour

    Note: You can access the invocation context with :attr:`HelpCommand.context`
    """

  async def send_command_help(self, command: CommandHelp):
    """|coro|

    Handles the command help page in the help command
    This function is called when the help command is called with a command as the argument

    You can override this method to customise the behaviour

    Note: You can access the invocation context with :attr:`HelpCommand.context`
    """

  async def show_hidden(self) -> bool:
    """|coro|

    To decide if hidden commands should be shown or not
    By default it simply returns `self._show_hidden`

    You can override this method to customise the behaviour

    Note: You can access the invocation context with :attr:`HelpCommand.context`
    """
    return self._show_hidden

  async def category_hidden(self, name: str, category: CategoryHelp):
    """|coro|

    This function is called when the category found from the help command is hidden
    and `self.show_hidden` returns False

    You can override this method to customise the behaviour

    Note: You can access the invocation context with :attr:`HelpCommand.context`
    """
    return await self.not_found()

  async def command_hidden(self, name: str, command: CommandHelp):
    """|coro|

    This function is called when the command found from the help command is hidden
    and `self.show_hidden` returns False

    You can override this method to customise the behaviour

    Note: You can access the invocation context with :attr:`HelpCommand.context`
    """
    return await self.not_found(name)

  async def not_found(self, command):
    """|coro|

    Handles the command/category not found error page in the help command
    This function is called when the argument specified in the help command is not found in `HelpManager`

    You can override this method to customise the behaviour

    Note: You can access the invocation context with :attr:`HelpCommand.context`
    """

  @command(help="Shows this message")
  async def help(self, ctx: Context, *, command: Optional[str]):
    """Actual implementation of the help command"""

    self.manager = HelpManager(self.bot)
    self.context = ctx

    if command is None:
      return await self.send_bot_help()

    for name in self.manager.categories.keys():
      if name is not None and command.lower() == name.lower():
        category = self.manager.categories[name]
        if category.hidden and not self.show_hidden:
          return await self.category_hidden(command, category)
        return await self.send_category_help(category)

    for cmd in self.manager.commands:
      if command.lower() == cmd.name.lower() or command.lower() in cmd.aliases:
        if cmd.hidden and not self.show_hidden:
          return await self.command_hidden(command, cmd)
        return await self.send_command_help(cmd)

    return await self.not_found(command)

EMPTY = "\u200B"

class DefaultHelpCog(HelpCog):
  """The default help cog"""

  async def get_category_help(self, category: CategoryHelp) -> Page:
    """Creates the help page for a category"""
    embed = embed_template(
      self.bot, self.context.author,
      title=f"{category.name} Command Listing",
      description=category.description
    )
    for command in category.commands:
      if command.hidden and not self.show_hidden:
        continue
      embed.add_field(name=command.name, value=f"> {command.help if command.help else EMPTY}", inline=True)

    return Page(embed=embed)

  async def get_command_help(self, command: CommandHelp) -> Page:
    """Creates the help page for a command"""
    embed = embed_template(
      self.bot, self.context.author,
      title=command.name,
      description=command.help
    )
    aliases = "\n".join(command.aliases) if command.aliases else "None"
    embed.add_field(name="Aliases", value=f"```\n{aliases}```", inline=False)

    usage = f"```\n{self.bot.prefix}{command.name} {command.signature}```"
    embed.add_field(name="Usage", value=usage)

    return Page(embed=embed)

  async def send_pages(self, pages: List[Page]) -> Message:
    """Sends a group of pages using a `Paginator`"""
    paginator = Paginator(pages=pages)
    return await paginator.send_to(self.context)

  async def send_bot_help(self) -> Message:
    embed = embed_template(
      self.bot, self.context.author,
      title="List of Command Categories",
      description="\u200b"
    )
    pages = []
    for category in self.manager.categories.values():
      if category.hidden and not self.show_hidden:
        continue
      embed.add_field(name=category.name, value=f"> {category.description if category.description else EMPTY}", inline=True)
      pages.append(await self.get_category_help(category))
    pages.insert(0, Page(embed=embed))
    return await self.send_pages(pages)

  async def send_category_help(self, category: CategoryHelp) -> Message:
    pages = [await self.get_category_help(category)]
    for command in category.commands:
      pages.append(await self.get_command_help(command))
    return await self.send_pages(pages)

  async def send_command_help(self, command: CommandHelp) -> Message:
    pages = [await self.get_command_help(command)]
    return await self.send_pages(pages)

  async def show_hidden(self) -> bool:
    return self.show_hidden or await self.bot.is_owner(self.context.author)

  async def not_found(self, command) -> Message:
    embed = error_template(
      self.bot, self.context.author,
      err_type = "NotFound",
      description = f"Command \"{command}\" does not exist!"
    )
    return await self.context.reply(embed=embed)