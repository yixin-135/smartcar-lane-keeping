from src.actions.base_action import Advance, SpinAntiClockwise, Sleep, SpinClockwise, Stop
from src.utils import Controller


class Rotate():
      def __init__(self):
          self.force = True
          self.update_controller_speed = False
          self.action_seq = [
              Advance(speed=50),                   # ① 设置前进
              Sleep(duration=1),                   # ② 前进 1 秒
              SpinAntiClockwise(speed=50),          # ③ 设置逆时针旋转
              Sleep(duration=0.8),                 # ④ 逆时针旋转 0.8 秒
              Advance(speed=50),                   # ⑤ 设置前进
              Sleep(duration=0.5),                 # ⑥ 前进 0.5 秒
              SpinClockwise(speed=50),              # ⑦ 设置顺时针旋转
              Sleep(duration=0.8),                 # ⑧ 顺时针旋转 0.8 秒
              Stop(speed=0),                       # ⑨ 停止
          ]

ctrl = Controller()
ctrl.execute(Rotate())