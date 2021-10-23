import sys
import subprocess
import asyncio
import signal

OUTPUT_MAX = 1000000
READ_CHUNK_SIZE = 10000
TIMEOUT = 10

async def python3(code: str, mention: str):
  
  backend = '''
import sys
sys.modules['sys'] = None
sys.modules['os'] = None
sys.modules['_io'] = None
sys.modules['io'] = None
sys.modules['subprocess'] = None
del sys
del __builtins__.open
del __loader__
'''

  code = backend + code

  args = (
    sys.executable,
    '-E',
    '-I',
    '-c',
    code
  )

  python = await asyncio.create_subprocess_exec(
    *args,
    stdout = subprocess.PIPE,
    stderr = subprocess.STDOUT
  )

  output_size = 0
  output = []

  while python.returncode is None:
    try:
      chars = await asyncio.wait_for(python.stdout.read(READ_CHUNK_SIZE), TIMEOUT)
    except asyncio.TimeoutError:
      python.terminate()
      break

    output_size += sys.getsizeof(chars)
    output.append(chars)

    if output_size > OUTPUT_MAX:
      python.terminate()
      break
    
  output = ''.join([chunk.decode() for chunk in output])

  returncode = python.returncode if python.returncode is not None else signal.SIGTERM

  result = subprocess.CompletedProcess(args, returncode, output, None)

  returncode = result.returncode

  msg = f'Your code has finished running with return code {returncode}'
  err = ''

  if returncode is None:
    msg = 'Your code has failed'
    err = result.stdout.strip()
  elif returncode == 15:
    msg = 'Your code timed out or ran out of memory'
  elif returncode == 255:
    msg = 'Your code has failed'
    err = 'A fatal error has occurred'
  else:
    try:
      name = signal.Signals(returncode).name
      msg = f'{msg} ({name})'
    except ValueError:
      pass

  if err:
    output = err
  else:
    output = result.stdout.strip()
    if output == '':
      output = 'No output detected'
    else:
      output = [f'{i:03d} | {line}' for i, line in enumerate(output.split('\n'), 1)]
      output = '\n'.join(output)

  s = f'{mention}, {msg}.\n\n```\n{output}\n```'
  if len(s) > 2000:
    output = 'Output too large to send'
    s = f'{mention}, {msg}.\n\n```\n{output}\n```'

  return s