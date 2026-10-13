import os
import time
import numpy as np
from src.actions import SetServo, Stop, TurnLeftInPlace, TurnRightInPlace, TurnAround, Start
from src.scenes.base_scene import BaseScene
from src.scenes.logo_match import TemplateMatcher
from src.utils import log
import cv2


class Helper_template_match(BaseScene):
    def __init__(self, memory_name, camera_info, msg_queue):
        super().__init__(memory_name, camera_info, msg_queue)
        self.det = None

    def init_state(self):
        log.info(f'start init {self.__class__.__name__}')
        self.det = TemplateMatcher('/root/syl/car/src/scenes/templates', match_threshold=0.5)
        log.info(f'{self.__class__.__name__} model init succ.')
        self.ctrl.execute(SetServo(servo=[90, 65]))
        return False

    def loop(self):
        ret = self.init_state()
        if ret:
            log.error(f'{self.__class__.__name__} init failed.')
            return
        frame = np.ndarray((self.height, self.width, 3), dtype=np.uint8, buffer=self.broadcaster.buf)
        log.info(f'{self.__class__.__name__} loop start')
        self.ctrl.execute(Start())    # 启动后慢速前进，寻找路标
        last_cate = None
        try:
            while True:
                if self.stop_sign.value:
                    break
                if self.pause_sign.value:
                    continue
                start = time.time()
                img_bgr = frame.copy()
                img_bgr = cv2.resize(img_bgr, (int(img_bgr.shape[1] / 4), int(img_bgr.shape[0] / 4)))
                bboxes = self.det.infer(img_bgr)
                bboxes = sorted(bboxes, key=lambda x: x[5], reverse=True)
                for x1, y1, x2, y2, cate, score in bboxes:
                    x, y = (x1 + x2) // 2, (y1 + y2) // 2
                    h, w = y2 - y1, x2 - x1
                    log.info(f'det: {x} {y} {h} {w} cate:{cate} score:{score}')

                    if score < 0.65:    # 分数太低，跳过
                        continue

                    if cate == 'left':
                        if 120 < x < 500 and y >= 50 and h >= 30:
                            self.ctrl.execute(TurnLeftInPlace())
                            time.sleep(1)
                            self.ctrl.execute(Start())
                            break

                    if cate == 'right':
                        if 120 < x < 500 and y >= 50 and h >= 30:
                            self.ctrl.execute(TurnRightInPlace())
                            time.sleep(1)
                            self.ctrl.execute(Start())
                            break

                    if cate == 'turnaround':
                        if 120 < x < 500 and y > 50 and h >= 30:
                            self.ctrl.execute(TurnAround())
                            time.sleep(2)
                            self.ctrl.execute(Start())
                            break
                log.info(f'infer cost {time.time() - start}')
        except KeyboardInterrupt:
            self.ctrl.execute(Stop())
