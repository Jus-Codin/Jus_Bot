from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Iterable, List, Optional, Union

if TYPE_CHECKING:
  from .models import DictT


def optional_factory(func: Callable[[DictT], Any], match: Optional[Any]=None):
  def wrap(val: Optional[DictT]):
    if val == match:
      return val
    else:
      return func(val)
  return wrap

def list_map_factory(func: Callable[[DictT], Any]):
  def wrap(seq: Iterable[DictT]):
    return [func(d) for d in seq]
  return wrap

def always_list(maybe_list: Union[List[DictT], DictT]):
  if isinstance(maybe_list, list):
    val = maybe_list
  else:
    val = [maybe_list]
  return val

def always_list_factory(func: Optional[Callable[[DictT], Any]]=None):
  def wrap(maybe_list: Union[List[DictT], DictT]):
    seq = always_list(maybe_list)
    if func is not None:
      return [func(d) for d in seq]
    else:
      return seq
  return wrap