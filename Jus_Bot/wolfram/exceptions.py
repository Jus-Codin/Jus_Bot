class WolframException(Exception):
  """The base execution class"""

class ParameterConflict(WolframException):
  """Exception that is raised when a parameter that has been specified by the API was passed in"""

class InterpretationError(WolframException):
  """Exception that is raised when the API is unable to interpret the input value"""

class MissingParameters(WolframException):
  """Exception that is raised when a required parameter is missing. This should rarely be raised"""

class InvalidAppID(WolframException):
  """Exception that is raised when an App ID is invalid"""