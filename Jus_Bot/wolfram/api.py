from __future__ import annotations

from .exceptions import InterpretationError, MissingParameters, InvalidAppID, WolframException
from .models import ConversationalResults, FullResults, Model, SimpleImage

from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
  from requests import Response
  from aiohttp import ClientResponse

class API:
  VERSION: int
  ENDPOINT: str
  PARAMS: Dict[str, str] = {}

  def format_results(resp: Response):
    raise NotImplementedError

  async def async_format_results(resp: ClientResponse):
    raise NotImplementedError



class FullResultsAPI(API):
  VERSION = 2
  ENDPOINT = "query"
  PARAMS = {
    "output": "json"
  }

  def format_results(resp: Response) -> FullResults:
    raw = resp.json()
    return FullResults.from_dict(raw["queryresult"])

  async def async_format_results(resp: ClientResponse) -> FullResults:
    raw = await resp.json()
    return FullResults.from_dict(raw["queryresult"])



class SimpleAPI(API):
  VERSION = 1
  ENDPOINT = "simple"

  def format_results(resp: Response) -> SimpleImage:
    if resp.status_code == 501:
      raise InterpretationError("input was unable to be interpreted by the API")
    elif resp.status_code == 400:
      raise MissingParameters("input parameter was not found")
    elif resp.status_code == 403:
      # In this case it is likely an invalid app id
      if resp.text == "Error 1: Invalid appid":
        raise InvalidAppID("App ID was invalid")
      else:
        raise WolframException(resp.text) # This should not happen

    return SimpleImage(resp.content)

  async def async_format_results(resp: ClientResponse) -> SimpleImage:
    if resp.status == 501:
      raise InterpretationError("input was unable to be interpreted by the API")
    elif resp.status == 400:
      raise MissingParameters("input parameter was not found")
    elif resp.status == 403:
      # In this case it is likely an invalid app id
      if await resp.text() == "Error 1: Invalid appid":
        raise InvalidAppID("App ID was invalid")
      else:
        raise WolframException(await resp.text()) # This should not happen

    return SimpleImage(await resp.read())



class ShortAPI(API):
  VERSION = 1
  ENDPOINT = "result"

  def format_results(resp: Response) -> str:
    if resp.status_code == 501:
      raise InterpretationError("input was unable to be interpreted by the API")
    elif resp.status_code == 400:
      raise MissingParameters("input parameter was not found")
    elif resp.status_code == 403:
      # In this case it is likely an invalid app id
      if resp.text == "Error 1: Invalid appid":
        raise InvalidAppID("App ID was invalid")
      else:
        raise WolframException(resp.text) # This should not happen

    return resp.text

  async def async_format_results(resp: ClientResponse) -> str:
    if resp.status == 501:
      raise InterpretationError("input was unable to be interpreted by the API")
    elif resp.status == 400:
      raise MissingParameters("input parameter was not found")
    elif resp.status == 403:
      # In this case it is likely an invalid app id
      if await resp.text() == "Error 1: Invalid appid":
        raise InvalidAppID("App ID was invalid")
      else:
        raise WolframException(await resp.text()) # This should not happen

    return await resp.text()



class SpokenAPI(API):
  VERSION = 1
  ENDPOINT = "spoken"

  def format_results(resp: Response) -> str:
    if resp.status_code == 501:
      raise InterpretationError("input was unable to be interpreted by the API")
    elif resp.status_code == 400:
      raise MissingParameters("input parameter was not found")
    elif resp.status_code == 403:
      # In this case it is likely an invalid app id
      if resp.text == "Error 1: Invalid appid":
        raise InvalidAppID("App ID was invalid")
      else:
        raise WolframException(resp.text) # This should not happen

    return resp.text

  async def async_format_results(resp: ClientResponse) -> str:
    if resp.status == 501:
      raise InterpretationError("input was unable to be interpreted by the API")
    elif resp.status == 400:
      raise MissingParameters("input parameter was not found")
    elif resp.status == 403:
      # In this case it is likely an invalid app id
      if await resp.text == "Error 1: Invalid appid":
        raise InvalidAppID("App ID was invalid")
      else:
        raise WolframException(await resp.text) # This should not happen

    return await resp.text()



class ConversationalAPI(API):
  VERSION = 1
  ENDPOINT = "conversation.jsp"

  def format_results(resp: Response) -> ConversationalResults:
    if resp.status_code == 403:
      # In this case it is likely an invalid app id
      if resp.text == "Error 1: Invalid appid":
        raise InvalidAppID("App ID was invalid")
      else:
        raise WolframException(resp.text) # This should not happen

    raw = resp.json()

    if raw.get("conversationID") is None: # This is a little bit of hard coding, might be reworked
      error = raw.get("error")
      if error == "No result is available":
        raise InterpretationError("input was unable to be interpreted by the API")
      elif error == "No input.":
        raise MissingParameters("input parameter was not found")
      else:
        raise WolframException(error) # Worse case scenario
    else:
      return ConversationalResults.from_dict(raw)

  async def async_format_results(resp: ClientResponse) -> ConversationalResults:
    if resp.status == 403:
      # In this case it is likely an invalid app id
      if await resp.text == "Error 1: Invalid appid":
        raise InvalidAppID("App ID was invalid")
      else:
        raise WolframException(await resp.text) # This should not happen

    raw = await resp.json()
    return ConversationalResults.from_dict(raw)