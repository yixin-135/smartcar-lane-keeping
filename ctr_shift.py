from src.actions.base_action import Advance, Sleep, ShiftLeft, ShiftRight, LeftOblique, RightOblique, BackUp, Stop
from src.utils import Controller


class Shift():
      def __init__(self):
          self.force = True
          self.update_controller_speed = False
          self.action_seq = [
              Advance(speed=50),        # ① 设置前进
              Sleep(duration=1),        # ② 前进 1 秒
              ShiftLeft(speed=50),      # ③ 设置向左平移
              Sleep(duration=1),        # ④ 向左平移 1 秒
              BackUp(speed=50),         # ⑤ 设置后退
              Sleep(duration=1),        # ⑥ 后退 1 秒
              ShiftRight(speed=50),     # ⑦ 设置向右平移
              Sleep(duration=1),        # ⑧ 向右平移 1 秒
              LeftOblique(speed=50),    # ⑨ 设置斜向左前方
              Sleep(duration=1),        # ⑩ 斜向左前方 1 秒
              RightOblique(speed=50),   # ⑪ 设置斜向右前方
              Sleep(duration=0.8),      # ⑫ 斜向右前方 0.8 秒
              Stop(speed=0),            # ⑬ 停止
          ]


ctrl = Controller()
ctrl.execute(Shift())