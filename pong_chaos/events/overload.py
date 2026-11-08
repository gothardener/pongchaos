from __future__ import annotations
import math
import random
import pygame
from ..core import *
from .base import *


@reg
class ChaosOverload(Event):
    name = 'CHAOS OVERLOAD'
    sub = 'EVERYTHING AT ONCE!!!'
    dur = 0
    weight = 2.5

    def start(self):
        g = self.g
        for _ in range(4):
            c = None
            for _try in range(10):
                c = g.pick_event()
                if c is not None and (not c.is_mode) and (c is not ChaosOverload):
                    break
                c = None
            if c is not None:
                g.start_event(c)
        g.flash(WHITE, 140)
