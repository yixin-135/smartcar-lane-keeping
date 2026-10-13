import time
from abc import ABC, abstractmethod


class BaseAction(ABC):

    def __init__(self, *args, **kwds) -> None:
        # 抽象的速度信息
        self.speed = kwds.get('speed', -1)
        # 电机角度
        self.servo_angle = kwds.get('servo', [-1, -1])

        self.motor_rating = [1, 1, 1, 1]

        # 确定是否需要在运行时根据前动作更新电机角度及电机速度
        self.update_speed = False
        self.update_servo = False

        if self.speed == -1:
            self.update_speed = True

        if self.servo_angle[0] == -1 or self.servo_angle[1] == -1:
            self.update_servo = True

        # 由速度生成方法将抽象的总体速度计算为4个电机的速度并输出为list
        if self.speed == -1:
            self.speed_setting = [0, 0, 0, 0]
        else:
            self.speed_setting = self.generate_speed_setting(self.speed)
            self.fix_speed()

    def fix_speed(self):
        self.speed_setting = [int(speed * ratio) for speed, ratio in zip(self.speed_setting, self.motor_rating)]

    @abstractmethod
    def generate_speed_setting(self, speed, degree=0):
        pass

    def __call__(self, speed, servo_angle):
        if self.update_servo:
            self.servo_angle = servo_angle
        if self.update_speed:
            degree = 0
            if hasattr(self, 'degree'):
                degree = self.degree
            self.speed_setting = self.generate_speed_setting(speed, degree)
            self.fix_speed()

        return self.speed_setting + self.servo_angle


class Advance(BaseAction):
    def generate_speed_setting(self, speed, degree=0):
        return [speed, speed, speed, speed]


class BackUp(BaseAction):
    def generate_speed_setting(self, speed, degree=0):
        return [-speed, -speed, -speed, -speed]


class Stop(BaseAction):
    def generate_speed_setting(self, speed, degree=0):
        return [0, 0, 0, 0]


class Sleep(BaseAction):
    def __init__(self, *args, **kwds):
        self.duration = kwds.get('duration', 0)
        super().__init__(*args, **kwds)

    def generate_speed_setting(self, speed, degree=0):
        return [speed, speed, speed, speed]

    def __call__(self, speed, servo_angle):
        time.sleep(self.duration)
        return None


class TurnLeft(BaseAction):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.degree = kwds.get('degree', 0)
        self.speed_setting = self.generate_speed_setting(speed=self.speed, degree=self.degree)
        self.fix_speed()

    def generate_speed_setting(self, speed, degree=0):
        # 右侧(3,4)快，左侧(1,2)慢 → 车向左转
        left_speed = int(speed * (1 - degree))
        right_speed = int(speed * (1 + degree))
        return [left_speed, left_speed, right_speed, right_speed]


class TurnRight(BaseAction):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.degree = kwds.get('degree', 0)
        self.speed_setting = self.generate_speed_setting(speed=self.speed, degree=self.degree)
        self.fix_speed()

    def generate_speed_setting(self, speed, degree=0):
        # 左侧(1,2)快，右侧(3,4)慢 → 车向右转
        left_speed = int(speed * (1 + degree))
        right_speed = int(speed * (1 - degree))
        return [left_speed, left_speed, right_speed, right_speed]


class SpinClockwise(BaseAction):
    def generate_speed_setting(self, speed, degree=0):
        # 左侧(1,2)正转 + 右侧(3,4)反转 → 顺时针旋转
        return [speed, speed, -speed, -speed]


class SpinAntiClockwise(BaseAction):
    def generate_speed_setting(self, speed, degree=0):
        # 左侧(1,2)反转 + 右侧(3,4)正转 → 逆时针旋转
        return [-speed, -speed, speed, speed]


class ShiftLeft(BaseAction):
    def generate_speed_setting(self, speed, degree=0):
        # 1(-), 2(+), 3(-), 4(+) → 小车向左平移
        return [-speed, speed, -speed, speed]


class ShiftRight(BaseAction):
    def generate_speed_setting(self, speed, degree=0):
        # 1(+), 2(-), 3(+), 4(-) → 小车向右平移
        return [speed, -speed, speed, -speed]


class LeftOblique(BaseAction):
    def generate_speed_setting(self, speed, degree=0):
        # 只有2号和4号正转 → 斜向左前方
        return [0, speed, 0, speed]


class RightOblique(BaseAction):
    def generate_speed_setting(self, speed, degree=0):
        # 只有1号和3号正转 → 斜向右前方
        return [speed, 0, speed, 0]


class SetServo(BaseAction):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.speed = 0

    def generate_speed_setting(self, speed, degree=0):
        return [0, 0, 0, 0]


class CustomAction(BaseAction):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.speed_setting = kwds.get('motor_setting', [0, 0, 0, 0])
        self.update_controller_speed = False
        self.update_speed = False

    def generate_speed_setting(self, speed, degree=0):
        return [0, 0, 0, 0]
