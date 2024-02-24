import os
import random
import string
from threading import Thread
import time

pid = os.getpid()
print(f"My pid is {pid}")

introduce = """
====================
>     拆弹专家     <
====================
拆弹密码会显示在屏幕
上，需要在十秒之内输
入正确的密码，否则炸
弹就会爆炸。
"""

print(introduce)

pw_len = 4  # 密码初始长度
pw = ""  # 炸弹密码
score = 0  # 得分
tickrate = 20  # tick频率
countdown = 0 # 炸弹倒计时

# 炸弹的三种状态
ACTIVE = 0
INACTIVE = 1
BOOM = 2
bomb_state = INACTIVE

def bomb_t():
    global bomb_state
    global score
    x = input()
    if x != pw:
        bomb_state = BOOM
    if x == pw:
        score = score + 1 + pw_len * 0.5
        bomb_state = INACTIVE

while True:
    if bomb_state == INACTIVE:
        # generate password
        pw = ''.join([random.choice(string.ascii_lowercase) for _ in range(pw_len)])
        pw_len += random.randint(0, 1)
        print(f"PASSWORD: {pw}")
        countdown = 10 * tickrate
        bomb = Thread(target=bomb_t)
        bomb.daemon = True
        bomb_state = ACTIVE  # 必须先修改状态在start，警惕并发bug
        bomb.start()
    if bomb_state == ACTIVE:
        if countdown == 0:
            bomb_state = BOOM
        countdown -= 1
    if bomb_state == BOOM:
        print("*BOOM!*")
        print(f"Your score: {score}")
        exit(0)
    time.sleep(1 / tickrate)
