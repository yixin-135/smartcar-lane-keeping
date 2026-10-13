from abc import ABC
from src.actions.base_action import Advance, Sleep, SpinAntiClockwise, SpinClockwise, Stop


class ComplexAction(ABC):
    def __init__(self):
        self.force = True
        self.update_controller_speed = False


class Start(ComplexAction):
    def __init__(self):
        super().__init__()
        self.update_controller_speed = True
        self.action_seq = [
            Advance(speed=35),
            Sleep(duration=0.2),
            Advance(speed=25),
        ]


class TurnLeftInPlace(ComplexAction):
    def __init__(self):
        super().__init__()
        self.action_seq = [
            Advance(speed=35),            # 直行到转弯位置
            Sleep(duration=3.4),          # 直行到转弯点
            SpinAntiClockwise(speed=40),  # 原地左转
            Sleep(duration=2.0),          # 转 90 度
            Stop(speed=0),                # 停止
        ]


class TurnRightInPlace(ComplexAction):
    def __init__(self):
        super().__init__()
        self.action_seq = [
            Advance(speed=35),            # 直行到转弯位置
            Sleep(duration=3.4),          # 直行到转弯点
            SpinClockwise(speed=40),      # 原地右转
            Sleep(duration=2.0),          # 转 90 度
            Stop(speed=0),                # 停止
        ]


class TurnAround(ComplexAction):
    def __init__(self):
        super().__init__()
        self.action_seq = [
            Advance(speed=35),            # 直行到合适位置
            Sleep(duration=4.4),          # 比转弯长一秒
            SpinAntiClockwise(speed=40),  # 第一次逆时针转
            Sleep(duration=2.0),
            Advance(speed=30),            # 直行一小段进入内道
            Sleep(duration=3.1),
            SpinAntiClockwise(speed=40),  # 第二次逆时针转
            Sleep(duration=2.0),
            Stop(speed=0),                # 停止
        ]
