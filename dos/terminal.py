import sys
import os
import subprocess
import io
from time import sleep

def spawn_terminal_from_shell(shell: str):
    process = subprocess.Popen(shell, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def main():
    sub_process = spawn_terminal_from_shell('pwsh')
    # read_buffer: list[bytes] = []
    # while True:
    #     read_bytes = read_from_fp(stdout_fp)
    #     if read_bytes is None:
    #         print("\n".join(str(byte) for byte in read_buffer))
    #         break
    #     read_buffer.append(read_bytes)
    # return

if __name__ == '__main__':
    main()