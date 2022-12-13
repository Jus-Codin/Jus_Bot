from enum import Enum
from typing import Union

class WolframEnum(Enum):
  """Base enum implementation, not to be used directly"""

  def __str__(self):
    return str(self.value)

class Bool(WolframEnum):
  TRUE = "true"
  FALSE = "false"

class Units(WolframEnum):
  METRIC = "metric"
  IMPERIAL = "imperial"



class LatLong:
  def __init__(self, lat: Union[int, float], long: Union[int, float]):
    self.lat = lat
    self.long = long

  def __str__(self):
    return f"{self.lat},{self.long}"