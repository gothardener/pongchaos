from __future__ import annotations
import math
import random
import pygame
from ..core import *

EVENTS = []

def reg(cls):
    EVENTS.append(cls)
    return cls

class Event:
    name = 'EVENT'
    sub = ''
    dur = 8.0
    group = None
    weight = 1.0
    is_mode = False
    cap = 15.0
    grabs_keys = False

    def __init__(self, g):
        self.g = g
        self.t = 0.0
        self.done = False

    @classmethod
    def ok(cls, g):
        return True

    def start(self):
        pass

    def update(self, dt):
        pass

    def end(self):
        pass

    def on_hit(self, ball, paddle):
        pass

    def on_wall(self, ball):
        pass

    def goal_mult(self, ball):
        return 1

    def draw_back(self, s):
        pass

    def draw_front(self, s):
        pass

    def post(self, s):
        return s

    def on_key(self, key):
        pass

    def draw_top(self, s):
        pass

def fevent(name, key, val, dur=8, sub='', group=None):

    class E(Event):
        pass
    E.name, E.dur, E.sub, E.group = (name, dur, sub, group)

    def start(self):
        self.g.fset(key, self, val)
        self.g.flash((255, 255, 255), 40)
    E.start = start
    EVENTS.append(E)
    return E

def pevent(name, key, val=1, dur=8, who='one', sub='', group=None, extra=None):

    class E(Event):
        pass
    E.name, E.dur, E.group = (name, dur, group)

    def start(self):
        g = self.g
        sides = [-1, 1] if who == 'both' else [random.choice((-1, 1))]
        for sd in sides:
            p = g.paddle(sd)
            p.mod(self, key, val)
            if extra:
                for k2, v2 in extra:
                    p.mod(self, k2, v2)
            g.parts.burst(p.x + 7, p.cy(), (255, 255, 0), 18, 220, 0.6)
        self.sub = ('BOTH PADDLES' if who == 'both' else g.who(sides[0])) + (' - ' + sub if sub else '')
    E.start = start
    EVENTS.append(E)
    return E
MAN = ['01110', '01110', '11111', '00100', '00100', '01010', '01010']

def human_keys(g, side):
    k = pygame.key.get_pressed()
    if side < 0:
        L, R, U, D = (k[pygame.K_a], k[pygame.K_d], k[pygame.K_w], k[pygame.K_s])
        F = k[pygame.K_SPACE] or k[pygame.K_f]
        if g.mode == 1:
            L = L or k[pygame.K_LEFT]
            R = R or k[pygame.K_RIGHT]
            U = U or k[pygame.K_UP]
            D = D or k[pygame.K_DOWN]
    else:
        L, R, U, D = (k[pygame.K_LEFT], k[pygame.K_RIGHT], k[pygame.K_UP], k[pygame.K_DOWN])
        F = k[pygame.K_RETURN] or k[pygame.K_RSHIFT] or k[pygame.K_KP0] or k[pygame.K_SLASH]
    return (bool(L), bool(R), bool(U), bool(D), bool(F))

def is_cpu(g, side):
    return side > 0 and g.mode == 1

class Mode(Event):
    is_mode = True
    weight = 3.0
    group = 'mode'
    dur = 40
    limit = 34
    hint1 = ''
    hint2 = ''

    @classmethod
    def ok(cls, g):
        return g.state == 'play' and bool(g.real_balls()) and (not g.fhas('takeover'))

    def start(self):
        g = self.g
        g.fset('takeover', self)
        g.hist.clear()
        for b in g.balls:
            b.captured = True
        self.over_t = None
        self.begin()

    def begin(self):
        pass

    def finish(self):
        pass

    def on_timeout(self):
        pass

    def tick(self, dt):
        pass

    def award(self, side, pts=1, msg=None):
        g = self.g
        g.scores[0 if side < 0 else 1] += pts
        g.play('powerup')
        g.popup(W / 2, H / 2, msg or '%s +%d' % (g.who(side), pts), GOLD, 30)
        g.flash(GOLD, 60)

    def end_soon(self, delay=1.6):
        if self.over_t is None:
            self.over_t = self.t + delay

    def update(self, dt):
        if self.over_t is not None:
            if self.t >= self.over_t:
                self.done = True
            return
        if self.t >= self.limit:
            self.on_timeout()
            self.end_soon(1.2)
            return
        self.tick(dt)

    def end(self):
        self.finish()
        self.g.restore_ball()

    def hint(self, s, y=H - 64):
        if self.t < 6.0:
            self.g.text_at(s, self.hint1 if self.g.mode == 1 else self.hint2, W // 2, y, 15, WHITE)
