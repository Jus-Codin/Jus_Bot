import sys
import subprocess

OUTPUT_MAX = 1000000
READ_CHUNK_SIZE = 10000

def python3(code: str):

  args = (
    sys.executable,
    '-c',
    code
  )

  python = subprocess.Popen(
    args,
    stdout = subprocess.PIPE,
    stderr = subprocess.STDOUT,
    text = True
  )

  output_size = 0
  output = []

  with python:
    while python.poll() is None:
      chars = python.stdout.read(READ_CHUNK_SIZE)
      output_size += sys.getsizeof(chars)
      output.append(chars)

      if output_size > OUTPUT_MAX:
        python.terminate()
        break
    
  output = ''.join(output)

  returncode = -python.returncode if python.returncode < 0 else python.returncode

  return subprocess.CompletedProcess(args, returncode, output, None)

