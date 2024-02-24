import os
import sys
import subprocess
import time
import atexit

target_pid = sys.argv[1]
## Inject
# 给*目标进程*准备的输入输出管道
input_pipe = "/tmp/awrapperi"
output_pipe = "/tmp/awrappero"
# 保存目标进程当前的输入输出
prev_stdin = os.readlink(f"/proc/{target_pid}/fd/0")
prev_stdout = os.readlink(f"/proc/{target_pid}/fd/1")
# remove existing pipe
if os.path.exists(input_pipe):
    os.remove(input_pipe)
if os.path.exists(output_pipe):
    os.remove(output_pipe)

# create pipe
os.mkfifo(input_pipe)
os.mkfifo(output_pipe)

# use gdb to redirect target process's IO to pipe
command = ['gdb', '-n', '-q', '-batch', '--pid', target_pid, '-ex', 'set scheduler-locking on', '-ex', f'call $pipei = open("{input_pipe}", 2)', '-ex', 'call close(0)', '-ex', 'call (int)dup2($pipei, 0)', '-ex', 'call close($pipei)', '-ex', f'call $pipeo = open("{output_pipe}", 2)', '-ex', 'call close(1)', '-ex', 'call (int)dup2($pipeo, 1)', '-ex', 'call close($pipeo)', '-ex', 'detach', '-ex', 'quit']
# Only input redirect
#command = ['gdb', '-n', '-q', '-batch', '--pid', target_pid, '-ex', 'set scheduler-locking on', '-ex', f'call $pipei = open("{input_pipe}", 2)', '-ex', 'call close(0)', '-ex', 'call (int)dup2($pipei, 0)', '-ex', 'call close($pipei)', '-ex', 'detach', '-ex', 'quit']
result = subprocess.run(command, capture_output=True, text=True)

# error handle
if 'No such process.' in result.stderr:
    print(f"未找到 pid={target_pid} 的进程")
    exit(1)

## Exit handler

def exit_handler():
    command = ['gdb', '-n', '-q', '-batch', '--pid', target_pid, '-ex', 'set scheduler-locking on', '-ex', f'call $pipei = open("{prev_stdin}", 2)', '-ex', 'call close(0)', '-ex', 'call (int)dup2($pipei, 0)', '-ex', 'call close($pipei)', '-ex', f'call $pipeo = open("{prev_stdout}", 2)', '-ex', 'call close(1)', '-ex', 'call (int)dup2($pipeo, 1)', '-ex', 'call close($pipeo)', '-ex', 'detach', '-ex', 'quit']
    subprocess.run(command, capture_output=True, text=True)
    # remove pipe
    if os.path.exists(input_pipe):
        os.remove(input_pipe)
    if os.path.exists(output_pipe):
        os.remove(output_pipe)

atexit.register(exit_handler)

## Main Logic for bomb game
pipei = open(output_pipe, "r")
pipeo = open(input_pipe, "w")

def pwrite(pipe, data, end='\n'):
    pipe.write(data + end)
    # print(f"debug: send: {repr(data + end)}")
    try:
        pipe.flush()
        return 0
    except BrokenPipeError:
        print("管道已关闭")
        return 1

end_at = 1000  # 限制运行次数
x = input("输入第一个密码：")
pwrite(pipeo, x)
while True:
    i = pipei.readline()
    print(i, end='')
    if "*BOOM!*" in i:
        continue
    if "Your score:" in i:
        break
    if end_at == 0:
        pwrite(pipeo, "42")  # 引爆炸弹
    else:
        pwrite(pipeo, i.split()[-1])
    end_at -= 1
