from __future__ import annotations

import os
import typing
from json import loads

from .utils import ErrorType
from .errors import ErrorHandler, DefaultErrorHandler
from .help import HelpCog, DefaultHelpCog

from discord import Colour, Intents, Game, Status, BaseActivity

def get_setup_from_env() -> SetupConfigDict:
  """
  Gets all the setup parameters for the bot from env,
  all variables must be uppercase and prefixed with `JUS_`

  Booleans can be specified with a number, `0` being `False` and `1` being `True`
  """
  setup_config: SetupConfigDict = {}
  for key in os.environ.keys():
    if key.startswith('JUS_'):
      item = os.environ.get(key)
      if item.isdigit() and len(item) == 1:
        item = not not int(item) # faster I think?
      setup_config[key.removeprefix('JUS_').lower()] = item
  return setup_config

def get_setup_from_json(filename: str) -> SetupConfigDict:
  """
  Gets all setup parameters for the bot from a json file.
  """
  path = os.path.join(
    os.getcwd(), filename
  )
  with open(path, 'r') as f:
    setup_config: SetupConfigDict = loads(f.read())
  return setup_config

# TODO: Full rework of config system

class ConfigDict(typing.TypedDict):
  intents: Intents
  activity_message: str
  activity_type: typing.Union[BaseActivity, None]
  status: Status
  help_cog: HelpCog
  default_colour: typing.Callable[[], Colour]
  error_colour: typing.Callable[[], Colour]
  error_handler: ErrorHandler
  error_msg: typing.Dict[ErrorType, typing.List[str]]

class SetupConfigDict(typing.TypedDict):
  """Configurations needed to specified to run the bot"""
  prefix: str
  token: str
  suppress: bool
  case_insensitive: bool
  enable_eval: bool
  wolfram_appid: str

# TODO: Implement cog configuration settings

DEFAULT_CONFIG_DICT: ConfigDict = {
  "intents": Intents.all(),
  "activity_message": "jusdev help",
  "activity_type": Game,
  "status": Status.online,
  "help_cog": DefaultHelpCog,
  "default_colour": Colour.random,
  "error_colour": Colour.brand_red,
  "error_handler": DefaultErrorHandler,
  "error_msg": {
    "default": [
      "Error!",
      "D'Oh",
      "Oops?",
      "Uh oh...",
      "What did you do...",
      "Reebe!",
      "01000101 01110010 01110010 01101111 01110010 00100001",
      "RXJyb3Ih",
      "VWggb2guLi4=",
      "Better luck next time",
      "why",
      "Noooooooo",
      "Have you tried turning it off and on again?",
      "Pls no"
    ],
    "not_found": [
      "What even is that?!",
      "UNKNOWN COMMAND",
      "Maybe it works on Alexa...",
      "Maybe try suggesting it?",
      "Nice typing",
      "Idk tho",
      "This ain't Google btw"
    ],
    "bad_perms": [
      "Nice try",
      "Haha NOO!",
      "Sike you thought",
      "Worth a try I guess",
      "E for Effort",
      "Cry about it",
      "NO U"
    ]
  }
}

class ConfigManager:

  def __init__(self, setup_config: SetupConfigDict, config_dict: ConfigDict):
    self.setup_config = setup_config
    self.config_dict = config_dict
    self._configs: typing.Union[SetupConfigDict, ConfigDict] = {**setup_config, **config_dict}

  @property
  def values(self) -> typing.Union[SetupConfigDict, ConfigDict]:
    return self._configs

  @property
  def items(self):
    return self._configs.items()

  @property
  def keys(self):
    return self._configs.keys()

  def get(self, item, default=None):
    try:
      return self._configs[item]
    except KeyError:
      return default

  def __getitem__(self, item: str):
    return self.get(item)

  def __setitem__(self, item: str, value: typing.Any):
    self._configs[item] = value

  def __str__(self):
    return str(self._configs)