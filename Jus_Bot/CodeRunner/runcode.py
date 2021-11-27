from pyston import PystonClient, File
from pyston.exceptions import TooManyRequests
from asyncio import sleep
import signal

TIMEOUT = 1000
MAX_LEN = 2000
MAX_LINE = 10

_client = PystonClient()

def is_codeblock(s: str):
  return s.startswith('```') and s.endswith('```') and len(s) > 6

def format_code(s: str):
  s = s[3:-3].split('\n', 1)
  if len(s) == 1:
    return None, s[0]
  else:
    return s

async def get_langs():
  runtimes = _client._runtimes or await _client.runtimes()
  langs = []
  for runtime in runtimes:
    langs.append(runtime.language)
    if runtime.aliases:
      langs.extend(runtime.aliases)
  return langs

async def run_code(code: str, mention: str, lang: str,  filename=None, _recursion=0):
  if lang.lower() not in await get_langs():
    return f'Unknown language, {mention}'
  if isinstance(code, str):
    code = [File(code, filename=filename or 'code')]
  try:
    output = await _client.execute(
      lang.lower(),
      code,
      run_timeout = TIMEOUT
    )
  except TooManyRequests:
    if _recursion > 5:
      return f"Bot has been rate limited, try again later, {mention}"
    await sleep(10)
    return await run_code(code, mention, lang, _recursion+1)
  
  stage = output.run_stage or output.compile_stage

  returncode = stage.signal or stage.code

  msg = f'Your {output.langauge} code has finished running with return code {returncode}'

  try:
    name = signal.strsignal(returncode)
    msg += f' ({name})'
  except Exception:
    pass

  result = stage.output

  if result:
    result = [f'{i:03d} | {line}' for i, line in enumerate(result.split('\n'), 1)][:-1]
    if len(result) > MAX_LINE:
      result = '\n'.join(result[:9])
      result += '\n      ... truncated, too many lines'
    else:
      result = '\n'.join(result)
  else:
    lang = ''
    result = 'No output detected'

  if len(result + msg + mention + lang) + 13 > MAX_LEN:
    lang = ''
    result = 'Output too large to send'

  return f'{mention}, {msg}.\n\n```{lang}\n{result}\n```'

async def run_file(mention, *files):
  results = []
  for file in files:
    filename_split = file.filename.split('.')
    if len(filename_split) < 2:
      results.append(f'Files must have a file extensions, {mention}')
      break
    # Have to do this in case some genius decides to give multiple file extensions
    filename = filename_split[0]
    lang = filename_split[-1]

    source = await file.read()
    try:
      source.decode('utf-8')
    except UnicodeDecodeError:
      results.append(f"Cannot decode {file.filename}, {mention}")
      break

    results.append(await run_code(source, mention, lang, filename))
  return results