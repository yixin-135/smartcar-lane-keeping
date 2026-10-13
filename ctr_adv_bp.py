# -*- coding: UTF-8 -*-
from src.actions.base_action import Advance, Stop, BackUp, Sleep
from src.utils import Controller


class Advance_Backup():
    def __init__(self, speed=50):
        self.force = True
        self.update_controller_speed = False
        self.action_seq = [
            Advance(speed=speed),
            Sleep(duration=8),
            Stop(speed=0),
            Sleep(duration=1),
            BackUp(speed=speed),
            Sleep(duration=6),
            Stop(speed=0),
        ]


ctrl = Controller()
ctrl.execute(Advance_Backup())