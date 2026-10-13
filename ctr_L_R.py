from src.actions.base_action import Advance,TurnLeft,TurnRight,Sleep,Stop
from src.utils import Controller


class Left_Right():
    def __init__(self):
        self.force = True
        self.update_controller_speed = False
        self.action_seq = [
            Advance(speed=50),  # ① 设置前进
            Sleep(duration=2),  # ② 前进 2 秒
            TurnLeft(speed=50, degree=0.9),  # ③ 设置左转
            Sleep(duration=0.8),  # ④ 左转 0.8 秒
            Advance(speed=50),  # ⑤ 设置前进
            Sleep(duration=1),  # ⑥ 前进 1 秒
            TurnRight(speed=50, degree=1.0),  # ⑦ 设置右转
            Sleep(duration=0.8),  # ⑧ 右转 0.8 秒
            Stop(speed=0),  # ⑨ 停止
        ]

ctrl = Controller()
ctrl.execute(Left_Right())