import datetime
import os
import cv2
import numpy as np
from src.actions import Advance, Stop, SetServo, TurnLeft, TurnRight, SpinClockwise, SpinAntiClockwise, BackUp, ShiftLeft, ShiftRight, LeftOblique, RightOblique, CustomAction

from src.scenes.base_scene import BaseScene
from src.utils import log


class Manual(BaseScene):
    def __init__(self, memory_name, camera_info, msg_queue):
        super().__init__(memory_name, camera_info, msg_queue)
        self.speed = 45
        self.save_dir = os.path.join(os.getcwd(), 'capture')
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir, exist_ok=True)

    def init_state(self):
        self.ctrl.execute(SetServo(servo=[90, 65]))

    def loop(self):
        ret = self.init_state()
        if ret:
            log.error(f'{self.__class__.__name__} init failed.')
            return
        frame = np.ndarray((self.height, self.width, 3), dtype=np.uint8, buffer=self.broadcaster.buf)
        log.info(f'{self.__class__.__name__} loop start')
        last_action = SetServo(servo=[90, 65])

        while True:
            try:
                if not self.msg_queue.empty():
                    key = self.msg_queue.get()
                else:
                    continue
            except KeyboardInterrupt:
                self.ctrl.execute(Stop())
                break

            degree = 0

            # ========== 按键控制 ==========
            if key == 'w':
                last_action = Advance(speed=self.speed)
            elif key == 'a':
                last_action = TurnLeft(speed=self.speed, degree=0.6)
            elif key == 's':
                last_action = BackUp(speed=self.speed)
            elif key == 'd':
                last_action = TurnRight(speed=self.speed, degree=0.6)
            elif key == 'q':
                last_action = SpinAntiClockwise(speed=self.speed)
            elif key == 'e':
                last_action = SpinClockwise(speed=self.speed)
            elif key == 'r':
                last_action = ShiftLeft(speed=self.speed)
            elif key == 't':
                last_action = ShiftRight(speed=self.speed)
            elif key == 'z':
                last_action = RightOblique(speed=self.speed)
            elif key == 'x':
                last_action = LeftOblique(speed=self.speed)
            # 加速
            elif key == 'up':
                self.speed = min(100, self.speed + 10)
                log.info(f'Speed up: {self.speed}')
                continue
            # 减速
            elif key == 'down':
                self.speed = max(10, self.speed - 10)
                log.info(f'Speed down: {self.speed}')
                continue
            # 拍照
            elif key == 'c':
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                filepath = os.path.join(self.save_dir, f'capture_{timestamp}.jpg')
                cv2.imwrite(filepath, frame)
                log.info(f'Image saved: {filepath}')
                continue
            # 暂时停车
            elif key == 'space':
                self.ctrl.execute(Stop())
                log.info('Pause (space)')
                continue
            # 退出
            elif key == 'esc':
                self.ctrl.execute(Stop())
                log.info('Exit by ESC')
                break
            else:
                log.info(f'Unknown key: {key}')
                continue

            # 下发动作
            if not isinstance(last_action, CustomAction):
                last_action.update_speed = False
                last_action.speed_setting = last_action.generate_speed_setting(speed=self.speed, degree=getattr(last_action, 'degree', 0))
                last_action.fix_speed()
            self.ctrl.execute(last_action)