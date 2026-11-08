from __future__ import annotations
import math
import random
from collections import deque
import pygame
from .core import *

class Particles:

    def __init__(self):
        self.p = []

    def burst(self, x, y, color, n=14, speed=220, life=0.6, size=5, grav=0.0, angle=None, spread=math.tau):
        for _ in range(max(1, n // 2)):
            a = random.uniform(0, math.tau) if angle is None else angle + random.uniform(-spread / 2, spread / 2)
            sp = random.uniform(0.2, 1.0) * speed
            lf = life * random.uniform(0.6, 1.0)
            self.p.append([x, y, math.cos(a) * sp, math.sin(a) * sp, lf, lf, color, size, grav])
        if len(self.p) > 500:
            del self.p[:150]

    def update(self, dt):
        for q in self.p:
            q[0] += q[2] * dt
            q[1] += q[3] * dt
            q[3] += q[8] * dt
            q[4] -= dt
        self.p = [q for q in self.p if q[4] > 0]

    def draw(self, surf):
        for q in self.p:
            pygame.draw.rect(surf, q[6], (int(q[0]), int(q[1]), 4, 4))

def draw_digits(surf, txt, cx, y, px, color):
    adv = 6 * px
    total_w = len(txt) * adv - px
    x = cx - total_w // 2
    for ch in txt:
        pat = _F['O' if ch == '0' else ch]
        for i, c in enumerate(pat):
            if c == '1':
                pygame.draw.rect(surf, color, (x + i % 5 * px, y + i // 5 * px, px, px))
        x += adv
INV1 = ['00100000100', '00010001000', '00111111100', '01101110110', '11111111111', '10111111101', '10100000101', '00011011000']
INV2 = ['00100000100', '10010001001', '10111111101', '11101110111', '11111111111', '01111111110', '00100000100', '01000000010']

class Ball:

    def __init__(self, g, x, y, vx, vy, fake=False):
        self.g = g
        self.x, self.y, self.vx, self.vy = (x, y, vx, vy)
        self.fake = fake
        self.alive = True
        self.trail = deque(maxlen=14)
        self.stuck = None
        self.stick_t = 0.0
        self.stick_off = 0.0
        self.stick_sp = BASE_SPEED
        self.captured = False
        self.cool = 0.0
        self.last_hit = 0

    @property
    def size(self):
        return BALL_BASE * self.g.bsize_cur

    def speed(self):
        return math.hypot(self.vx, self.vy)

    def set_speed(self, sp):
        cur = self.speed()
        if cur < 1e-06:
            self.vx, self.vy = (sp, 0)
        else:
            self.vx *= sp / cur
            self.vy *= sp / cur

class Paddle:

    def __init__(self, side, controller):
        self.side = side
        self.controller = controller
        self.w = 14
        self.x = 28 if side < 0 else W - 28 - 14
        self.base_h = 92
        self.y = H / 2 - 46
        self.vy = 0.0
        self.speed = 470.0
        self.xoff = 0.0
        self.mods = []
        self.ai_err = 0.0
        self.ai_t = 0.0

    def mod(self, owner, key, val=1, t=None):
        if owner is None and t is not None:
            for m in self.mods:
                if m[0] is None and m[1] == key and (m[2] == val):
                    m[3] = max(m[3] or 0, t)
                    return
        self.mods.append([owner, key, val, t])

    def unmod(self, owner):
        self.mods = [m for m in self.mods if m[0] is not owner]

    def prod(self, key):
        r = 1.0
        for m in self.mods:
            if m[1] == key:
                r *= m[2]
        return r

    def has(self, key):
        for m in self.mods:
            if m[1] == key:
                return True
        return False

    def food(self):
        for m in self.mods:
            if m[1] == 'food':
                return m[2]
        return None

    @property
    def h(self):
        return clamp(self.base_h * self.prod('h'), 26, 380)

    def cy(self):
        return self.y + self.h / 2

    def segs(self):
        if self.food() == 'donut':
            return [(0, 0.36), (0.64, 1)]
        if self.has('split'):
            return [(0, 0.38), (0.62, 1)]
        return [(0, 1)]

    def rects(self):
        h = self.h
        x = self.x + self.xoff
        ys = [self.y]
        if self.has('clone'):
            ys.append(H - self.y - h)
        out = []
        for y0 in ys:
            for a, b in self.segs():
                out.append((x, y0 + a * h, self.w, (b - a) * h))
        return out

    def update(self, dt, dirn):
        for m in self.mods:
            if m[3] is not None:
                m[3] -= dt
        self.mods = [m for m in self.mods if m[3] is None or m[3] > 0]
        sp = self.speed * self.prod('speed')
        if self.has('frozen'):
            dirn = 0
        target = dirn * sp
        if self.has('slip'):
            self.vy += (target - self.vy) * min(1.0, dt * 3.0)
        else:
            self.vy = target
        self.y += self.vy * dt
        h = self.h
        if self.y < 0:
            self.y = 0
            self.vy = 0
        if self.y > H - h:
            self.y = H - h
            self.vy = 0
