__title__ = "JusBot"
__author__ = "JusCodin"
__version__ = "5.0.0a1"

from .bot import JusBot
from .config import get_setup_from_env, get_setup_from_json

from typing import NamedTuple, Literal

class VersionInfo(NamedTuple):
  major: int
  minor: int
  micro: int
  releaselevel: Literal["alpha", "beta", "candidate", "final"]
  serial: int

version_info: VersionInfo = VersionInfo(major=5, minor=0, micro=0, releaselevel="alpha", serial=1)