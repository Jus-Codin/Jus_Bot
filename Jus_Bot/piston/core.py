from __future__ import annotations

import re
import typing

from pyston import File, PystonClient

if typing.TYPE_CHECKING:
  from pyston.models import Output


MAX_LEN = 2000
MAX_LINE = 10




def get_codeblocks(code: str) -> typing.List[typing.Tuple[str, str]]:
  codeblocks = re.findall(r"```([a-zA-Z0-9]*)\s([\s\S(^\\`{3})]*?)\s*```", code)
  return codeblocks

async def run_code(lang: str, code: str, filename: str = None) -> Output:
  client = PystonClient()
  code = [File(code, filename=filename)]
  output = await client.execute(
    lang.lower(),
    code
  )
  return output

async def process_output(output: Output):
  stage = output.run_stage or output.compile_stage
  returncode = stage.signal or stage.code
  lang = output.langauge
  msg = f"Your {lang} code has finished running with return code {returncode}"
  res = stage.output
  if res:
    res = [f'{i:03d} | {line}' for i, line in enumerate(res.split('\n'), 1)][:-1]
    if len(res) > MAX_LINE:
      result = '\n'.join(res[:9]) + '\n      ... truncated, too many lines'
    else:
      result = '\n'.join(res)
  else:
    lang = ''
    result = 'No output detected'
  if len(result + msg + lang) + 45 > MAX_LEN:
    lang = ''
    result = 'Output too large to send'
  
  return f'{msg}.\n\n```{lang}\n{result}\n```'