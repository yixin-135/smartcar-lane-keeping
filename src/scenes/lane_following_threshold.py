import time
import numpy as np
import cv2
from src.actions import SetServo, Stop, Start, TurnLeft, TurnRight, Advance
from src.scenes.base_scene import BaseScene
from src.utils import log

def extract_yellow_region(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_yellow = np.array([15, 40, 120])
    upper_yellow = np.array([45, 180, 255])

    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    yellow_region = cv2.bitwise_and(image, image, mask=mask)

    gray = cv2.cvtColor(yellow_region, cv2.COLOR_BGR2GRAY)

    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)

    return binary

def getEdgeImg(binary_img):
    canny_lth = 50
    canny_hth = 100
    edgeImg = cv2.Canny(binary_img, canny_lth, canny_hth)

    return edgeImg


def roi_mask(img, corner_points):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, corner_points, 255)
    masked_img = cv2.bitwise_and(img, mask)
    return masked_img

def process_image(image):
    rows, cols = image.shape

    for i in range(rows):
        for j in range(cols - 1, -1, -1):

            if image[i][j] != 0:

                for k in range(j, max(-1, j - 3), -1):
                    if k >= 0:
                        image[i][k] = 0
                break

    return image

def getRLaneLine(roi_edges):
    rho = 1
    theta = np.pi / 180
    threshold = 10
    min_line_len = 20
    max_line_gap = 5

    lines = cv2.HoughLinesP(roi_edges, rho, theta, threshold, minLineLength=min_line_len, maxLineGap=max_line_gap)

    if lines is not None:
        cols = roi_edges.shape[1]

        # 第一轮：斜率 > 0 且位置在右侧
        right_lines = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if x2 - x1 == 0:
                continue
            slope = (y2 - y1) / (x2 - x1)
            avg_x = (x1 + x2) / 2
            if slope > 0 and avg_x > cols / 3 and abs(slope) >= 0.1:
                right_lines.append(line)

        # 第二轮：如果没找到，放宽条件，只要在右侧就行
        if not right_lines:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if x2 - x1 == 0:
                    continue
                slope = (y2 - y1) / (x2 - x1)
                avg_x = (x1 + x2) / 2
                if avg_x > cols / 3 and abs(slope) >= 0.1:
                    right_lines.append(line)

        if right_lines:
            longest_line = max(right_lines, key=lambda x: np.linalg.norm(x[0][0:2] - x[0][2:4]))
            x1, y1, x2, y2 = longest_line[0]

            slope = (y2 - y1) / (x2 - x1)
            b = y2 - slope * x2
            return b, slope
        else:
            return 0, 0
    else:
        return 0, 0

def get_cur_offset_x(imgOri):
        small_img = cv2.resize(imgOri, (int(imgOri.shape[1] / 4), int(imgOri.shape[0] / 4)))
        roi_binary = extract_yellow_region(small_img)
        edges = getEdgeImg(roi_binary)

        rows, cols = edges.shape
        points = np.array([[(0, rows), (0, 45), (319, 45), (cols, rows)]])

        roi_edges = roi_mask(edges, points)

        roi_edges = process_image(roi_edges)

        b, slope = getRLaneLine(roi_edges)

        if slope == 0:
            return None

        cur_pos = (int)((45 - b) / slope)
        delta_X = cur_pos - 220

        return delta_X * 4

class LF_threshold(BaseScene):
        def __init__(self, memory_name, camera_info, msg_queue):
            super().__init__(memory_name, camera_info, msg_queue)
            # self.net = None
            self.forward_spd = 35

        def init_state(self):
            log.info(f'start init {self.__class__.__name__}')

            self.ctrl.execute(SetServo(servo=[90, 65]))
            return False

        def loop(self):
            ret = self.init_state()
            if ret:
                log.error(f'{self.__class__.__name__} init failed.')
                return
            frame = np.ndarray((self.height, self.width, 3), dtype=np.uint8, buffer=self.broadcaster.buf)
            log.info(f'{self.__class__.__name__} loop start')
            self.ctrl.execute(Start())
            last_x_offset = 0
            fail_count = 0
            try:
                while True:
                    if self.stop_sign.value:
                        break
                    if self.pause_sign.value:
                        continue
                    start = time.time()
                    img_bgr = frame.copy()
                    x_offset = get_cur_offset_x(img_bgr)
                    if x_offset is None:
                        fail_count += 1
                        if fail_count > 30:
                            self.ctrl.execute(Stop())
                            log.info('失去车道线，停车')
                            break
                        elif fail_count <= 5:
                            x_offset = last_x_offset
                        else:
                            x_offset = last_x_offset * 1.5 if abs(last_x_offset) > 0 else 200
                    else:
                        fail_count = 0
                        last_x_offset = x_offset

                    log.info(f'x_offset: {x_offset}')

                    # 根据偏移量调整方向（死区 ±50）
                    spd = self.forward_spd
                    if -50 < x_offset <= 50:
                        self.ctrl.execute(Advance(speed=spd))
                    elif 50 < x_offset <= 80:
                        self.ctrl.execute(TurnRight(speed=spd, degree=0.35))
                    elif 80 < x_offset <= 120:
                        self.ctrl.execute(TurnRight(speed=spd, degree=0.42))
                    elif 120 < x_offset <= 160:
                        self.ctrl.execute(TurnRight(speed=spd, degree=0.48))
                    elif 160 < x_offset <= 200:
                        self.ctrl.execute(TurnRight(speed=spd, degree=0.53))
                    elif 200 < x_offset <= 250:
                        self.ctrl.execute(TurnRight(speed=spd, degree=0.57))
                    elif x_offset > 250:
                        self.ctrl.execute(TurnRight(speed=spd, degree=0.60))
                    elif -80 < x_offset <= -50:
                        self.ctrl.execute(TurnLeft(speed=spd, degree=0.35))
                    elif -120 < x_offset <= -80:
                        self.ctrl.execute(TurnLeft(speed=spd, degree=0.42))
                    elif -160 < x_offset <= -120:
                        self.ctrl.execute(TurnLeft(speed=spd, degree=0.48))
                    elif -200 < x_offset <= -160:
                        self.ctrl.execute(TurnLeft(speed=spd, degree=0.53))
                    elif -250 < x_offset <= -200:
                        self.ctrl.execute(TurnLeft(speed=spd, degree=0.57))
                    elif x_offset <= -250:
                        self.ctrl.execute(TurnLeft(speed=spd, degree=0.60))

                    log.info(f'LF cost {time.time() - start}')
            except KeyboardInterrupt:
                self.ctrl.execute(Stop())