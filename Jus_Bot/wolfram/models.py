"""
Practically all WolframAlpha API models as well as internally used
data classes are here
"""
from __future__ import annotations

from dataclasses import dataclass, field, InitVar
from typing import (
  Callable,
  Generic,
  Mapping,
  Optional,
  List,
  TYPE_CHECKING,
  TypeVar,
  Union
)

from .types import (
  WolframDict,
  FullResultsDict,
  ConversationalResultsDict,
  PodDict,
  SubPodDict,
  ImageDict,
  AudioDict,
  AssumptionsDict,
  AssumptionDict,
  WarningDict,
  SpellCheckWarningDict,
  DelimiterWarningDict,
  TranslationWarningDict,
  AlternativeDict,
  ReinterpretWarningDict,
  DidYouMeanDict,
  LanguageMsgDict,
  FutureTopicDict,
  ExamplePageDict,
  TipsDict,
  GeneralizationDict,
  ErrorDict,
  SourceDict
)
from .factory import optional_factory, list_map_factory, always_list_factory

if TYPE_CHECKING:
  from dataclasses import Field

DictT = TypeVar("DictT", bound=WolframDict)



class WolframURL:
  def __init__(self, url: str):
    url = url.split("?")
    if len(url) > 1:
      url, self._query = url
    else:
      url, self._query = url[0], None
    self._path = url.replace("\/", "/")

  def __str__(self):
    return self.url

  def __repr__(self):
    return f"WolframURL(url={self.url})"

  @property
  def path(self) -> str:
    return self._path

  @property
  def query(self) -> Optional[str]:
    return self._query

  @property
  def params(self) -> Optional[Mapping[str, str]]:
    if self.query is None:
      return None
    d = {}
    for param in self.query.split("&"):
      k, v = param.split("=")
      d[k] = v
    return d

  @property
  def url(self) -> str:
    if self.query is None:
      return self.path
    else:
      return self.path + "?" + self.query



def model_field(factory: Optional[Callable] = None, **kwargs) -> Field:
  return field(
    metadata={"factory": factory},
    **kwargs
  )

def optional_field(factory: Callable, match=None, **kwargs) -> Field:
  return field(
    default=None,
    metadata={"factory": optional_factory(factory, match=match)},
    **kwargs
  )

@dataclass
class Model(Generic[DictT]):
  """The base class of all Wolfram|Alpha models"""
  _raw: InitVar[DictT]

  def __post_init__(self, _raw: DictT=None):
    self._raw = _raw
    for attr, field in self.__dataclass_fields__.items():
      # This is a little hacky, but no better way to do this with dataclasses
      factory = field.metadata.get("factory")
      if factory is not None:
        val = getattr(self, attr)
        setattr(self, attr, factory(val))

  def __getattr__(self, attr):
    return self.raw[attr]

  def __getitem__(self, item):
    return self.raw[item]

  @classmethod
  def from_dict(cls, raw: DictT):
    """Constructs the model from a mapping"""
    try:
      return cls(
        _raw = raw,
        **{
          k: v
          for k, v in raw.items()
          if k in cls.__dataclass_fields__.keys()
        }
      )
    except AttributeError as e:
      print(raw)
      raise e

  @property
  def _to_dict(self) -> DictT:
    """Returns the model with it's values in a dictionary excluding private variables,
    not to be called directly"""
    d = {}
    for k in self.__dataclass_fields__.keys():
      if not k.startswith("_"):
        if isinstance(k, Model):
          d[k] = getattr(self, k).raw
        else:
          d[k] = getattr(self, k)
    return d

  @property
  def raw(self) -> DictT:
    """Returns the raw dictionary of the model"""
    return self._raw if self._raw is not None else self._to_dict



# Subpod models

@dataclass
class Image(Model[ImageDict]):
  width: int
  height: int
  contenttype: str
  src: WolframURL = model_field(
    factory=WolframURL
  )
  themes: List[int] = model_field(
    factory=lambda seq: [
      int(ele) for ele in seq.split(",")
    ]
  )
  title: Optional[str] = optional_field(
    factory=str,
    match="?"
  )
  alt: Optional[str] = optional_field(
    factory=str,
    match="?"
  )

  def __repr__(self):
    return f"Image(title={self.title}, alt={self.alt}, src={self.src})"


@dataclass
class Audio(Model[AudioDict]):
  type: str
  url: WolframURL = model_field(factory=WolframURL)



# Assumptions

@dataclass
class Assumption(Model[AssumptionDict]):
  name: str
  desc: str
  input: str

  def __repr__(self):
    return f"Assumption(name={self.name})"
  
@dataclass
class AssumptionsCollection(Model[AssumptionsDict]):
  type: str
  template: str
  count: int
  values: List[Assumption] = model_field(
    factory=list_map_factory(
      Assumption.from_dict
    )
  )
  word: Optional[str] = None

  def __repr__(self):
    return f"AssumptionsCollection(type={self.type}, word={self.word}, values={self.values})"

  def __iter__(self):
    return iter(self.values)

  def __getitem__(self, index: Union[int, slice]) -> Assumption:
    return self.values[index]

  @property
  def description(self):
    """The default description of the assumption"""
    return self.values[0].desc

  @property
  def text(self):
    """The assumption message provided by the API"""
    text = self.template.replace("${desc1}", self.description)
    try:
      text = text.replace("${word}", self.word)
    except TypeError:
      pass
    return text.split(". ", 1)[0]



# Warnings

@dataclass
class Warning(Model[WarningDict], Generic[DictT]):
  text: str

  @classmethod
  def _find_cls(cls, warning: DictT):
    for sub in cls.__subclasses__():
      if all(
        k in warning.keys() or k == "text"
        for k in sub.__dataclass_fields__.keys()
      ):
        return sub
    return cls

  @classmethod
  def to_subclass(cls, warning: DictT):
    cls = cls._find_cls(warning)
    return cls.from_dict(warning)

  @property
  def msg(self):
    """The warning message provided by Wolfram|Alpha"""
    return self.text

@dataclass
class SpellCheckWarning(Warning[SpellCheckWarningDict]):
  word: str
  suggestion: str

@dataclass
class DelimiterWarning(Warning[DelimiterWarningDict]):
  pass

@dataclass
class TranslationWarning(Warning[TranslationWarningDict]):
  phrase: str
  trans: str
  lang: str

@dataclass
class Alternative(Model[AlternativeDict]):
  level: str
  val: str
  score: float = model_field(factory=float)

@dataclass
class ReinterpretWarning(Warning[ReinterpretWarningDict]):
  new: str
  level: str
  score: float = model_field(factory=float)
  alternative: List[Alternative] = model_field(
    factory=always_list_factory(
      Alternative.from_dict
    )
  )

  @property
  def msg(self):
    return f"{self.text} {self.new}"



# Queries that are not understood

@dataclass
class DidYouMean(Model[DidYouMeanDict]):
  level: str
  val: str
  score: float = model_field(factory=float)

@dataclass
class LanguageMsg(Model[LanguageMsgDict]):
  english: str
  other: str

  @property
  def msg(self):
    return f"{self.english}\n{self.other}"

@dataclass
class FutureTopic(Model[FutureTopicDict]):
  topic: str
  msg: str

@dataclass
class ExamplePage(Model[ExamplePageDict]):
  category: str
  url: WolframURL = model_field(factory=WolframURL)

@dataclass
class Tip(Model[TipsDict]):
  text: str

@dataclass
class Generalization(Model[GeneralizationDict]):
  topic: str
  desc: str
  url: WolframURL = model_field(factory=WolframURL)



# Errors usually caused by bad app ids

@dataclass
class Error(Model[ErrorDict]):
  msg: str
  code: int = model_field(factory=int)



# Sources

@dataclass
class Source(Model[SourceDict]):
  text: str
  url: WolframURL = model_field(factory=WolframURL)



@dataclass
class SubPod(Model[SubPodDict]):
  title: str
  plaintext: Optional[str] = optional_field(
    factory=str,
    match="?"
  )
  img: Optional[Image] = optional_field(
    factory=Image.from_dict
  )
  sound: Optional[Image] = optional_field(
    factory=Audio.from_dict
  )



@dataclass
class Pod(Model[PodDict]):
  title: str
  position: int
  id: str
  numsubpods: int
  subpods: List[SubPod] = model_field(
    factory=list_map_factory(
      SubPod.from_dict
    )
  )
  error: Optional[Error] = optional_field(
    factory=Error.from_dict,
    match=False
  )
  primary: bool = False

  def __repr__(self):
    return f"Pod(title={self.title}, numsubpods={self.numsubpods}, primary={self.primary})"

  @property
  def text(self) -> Optional[str]:
    for subpod in self.subpods:
      if subpod.plaintext is not None:
        return subpod.plaintext


@dataclass
class FullResults(Model[FullResultsDict]):
  success: bool
  numpods: int
  timing: float

  id: str
  host: str

  tips: Optional[List[Tip]] = optional_field(
    factory=always_list_factory(
      Tip.from_dict
    )
  )

  recalculate: Optional[WolframURL] = optional_field(
    factory=optional_factory(
      WolframURL,
      match=""
    )
  )
  pods: Optional[List[Pod]] = optional_field(
    factory=list_map_factory(
      Pod.from_dict
    )
  )  
  
  warnings: Optional[List[Warning]] = optional_field(
    factory=always_list_factory(
      Warning.to_subclass
    )
  )
  sources: Optional[List[Source]] = optional_field(
    factory=always_list_factory(
      Source.from_dict
    )
  )

  languagemsg: Optional[LanguageMsg] = optional_field(
    factory=LanguageMsg.from_dict
  )
  futuretopic: Optional[FutureTopic] = optional_field(
    factory=FutureTopic.from_dict
  )
  examplepage: Optional[ExamplePage] = optional_field(
    factory=ExamplePage.from_dict
  )
  generalization: Optional[Generalization] = optional_field(
    factory=Generalization.from_dict
  )
  didyoumeans: Optional[List[DidYouMean]] = optional_field(
    factory=always_list_factory(
      DidYouMean.from_dict
    )
  )
  
  assumptions: Optional[AssumptionsCollection] = optional_field(
    factory=AssumptionsCollection.from_dict
  )

  error: Optional[Error] = optional_field(
    factory=Error.from_dict,
    match=False
  )

  def __repr__(self):
    return f"FullResults(success={self.success}, numpods={self.numpods})"

  @property
  def is_error(self) -> bool:
    return self.error is not None

  @property
  def primary(self) -> Optional[Pod]:
    """Returns the primary pod, if any"""
    if self.pods is not None:
      for pod in self.pods:
        if pod.primary:
          return pod
    else: # TODO: make custom exception for this
      raise Exception("There are no pods")

  @property
  def details(self) -> Mapping[str, str]:
    """A simplified set of answers by pod title"""
    return {
      pod.title: pod.text
      for pod in self.pods
      if pod.text is not None
    }

  @property
  def is_fallthrough(self) -> bool:
    """If the result is a fallthrough result.
    A fallthrough result occurs when the API does not understand your query.
    For more information, read https://products.wolframalpha.com/api/documentation/#queries-that-are-not-understood
    """
    return not self.success and self.error is None

  @property
  def fallthrough(self):
    """Returns a fallthrough result, if any"""
    return (
      self.languagemsg or self.futuretopic or self.examplepage  or self.didyoumeans
    )



@dataclass
class ConversationalResults(Model[ConversationalResultsDict]):
  conversationID: str
  host: str
  s: Optional[int] = optional_field(factory=int)
  result: Optional[str] = optional_field(factory=str)
  error: Optional[str] = optional_field(factory=str)

  @property
  def is_error(self):
    """If the result is an error"""
    return self.error is not None

  @property
  def followup_url(self) -> str:
    """The url to send a follow up request to.
    Note that this is meant to be passed to `Client.query_conversational`"""
    return f"https://{self.host}/api/"

  @property
  def followup_params(self) -> dict:
    """A dictionary of parameters that should be sent with the follow up request"""
    d = dict(conversationID=self.conversationID)
    if self.s is not None:
      d["s"] = self.s
    return d



try:
  from PIL import Image as _Image
  from io import StringIO
except ImportError:
  _Image = None

class SimpleImage:
  """Represents an image given via the Simple API"""
  def __init__(self, data: bytes):
    self._data = data

  @property
  def data(self) -> bytes:
    """Returns the raw image data"""
    return self._data

  def get_image(self) -> _Image.Image:
    if _Image is None:
      raise Exception("pillow must be installed to convert to image")
    return _Image.open(StringIO(self.data))

  def save_to(self, fp: str):
    """Saves the image to a specified file path"""
    img = self.get_image()
    img.save(fp)