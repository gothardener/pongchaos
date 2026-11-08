from __future__ import annotations
import math
import random
import pygame
from ..core import *
from .base import *


@reg
class SpinBar(Event):
    name = 'HELICOPTER'
    sub = 'A SPINNING BAR OF DOOM'
    dur = 11
    group = 'world'
    L = 125

    def start(self):
        self.ang = random.uniform(0, math.tau)
        self.w = random.choice((-1, 1)) * 2.4

    def ends(self):
        ex, ey = (math.cos(self.ang) * self.L, math.sin(self.ang) * self.L)
        return (W / 2 - ex, H / 2 - ey, W / 2 + ex, H / 2 + ey)

    def update(self, dt):
        g = self.g
        self.ang += self.w * g.sdt
        ax, ay, bx, by = self.ends()
        vx, vy = (bx - ax, by - ay)
        for b in g.real_balls():
            t_ = clamp(((b.x - ax) * vx + (b.y - ay) * vy) / (vx * vx + vy * vy), 0, 1)
            px, py = (ax + vx * t_, ay + vy * t_)
            dx, dy = (b.x - px, b.y - py)
            d = math.hypot(dx, dy)
            r = b.size / 2 + 8
            if d < r:
                if d < 1e-06:
                    dx, dy, d = (0.0, -1.0, 1.0)
                nx, ny = (dx / d, dy / d)
                b.x, b.y = (px + nx * r, py + ny * r)
                tvx, tvy = (-self.w * (py - H / 2), self.w * (px - W / 2))
                rvx, rvy = (b.vx - tvx, b.vy - tvy)
                dot = rvx * nx + rvy * ny
                if dot < 0:
                    rvx -= 2 * dot * nx
                    rvy -= 2 * dot * ny
                b.vx, b.vy = (rvx + tvx, rvy + tvy)
                b.set_speed(clamp(b.speed(), 260, MAX_SPEED * 0.9))
                g.play('bump', 0.5)

    def draw_front(self, s):
        ax, ay, bx, by = self.ends()
        for k in range(6):
            x0, y0 = (ax + (bx - ax) * k / 6.0, ay + (by - ay) * k / 6.0)
            x1, y1 = (ax + (bx - ax) * (k + 1) / 6.0, ay + (by - ay) * (k + 1) / 6.0)
            pygame.draw.line(s, (230, 60, 60) if k % 2 else WHITE, (x0, y0), (x1, y1), 14)
        pygame.draw.circle(s, (255, 230, 0), (W // 2, H // 2), 12)

@reg
class Snowball(Event):
    name = 'SNOWBALL'
    sub = 'THE BALL GROWS EVERY TIME YOU HIT IT'
    dur = 12
    group = 'size'

    def start(self):
        self.hits = 0

    def on_hit(self, ball, paddle):
        self.hits += 1
        self.g.fset('bsize', self, min(3.2, 1.0 + 0.35 * self.hits))
        self.g.play('bump', 0.6)

@reg
class SpeedDemon(Event):
    name = 'SPEED DEMON'
    sub = 'IT KEEPS ACCELERATING'
    dur = 11
    group = 'speed'

    def update(self, dt):
        for b in self.g.real_balls():
            if not b.stuck:
                b.set_speed(min(MAX_SPEED * 0.85, b.speed() * (1 + 0.1 * self.g.bdt * 6)))

@reg
class FogBank(Event):
    name = 'FOG BANK'
    sub = "CAN'T SEE A THING"
    dur = 11

    def start(self):
        self.clouds = [[random.uniform(0, W), random.uniform(60, H - 160), random.uniform(25, 55) * random.choice((-1, 1))] for _ in range(4)]

    def update(self, dt):
        for c in self.clouds:
            c[0] += c[2] * dt
            if c[0] > W + 120:
                c[0] = -260
            elif c[0] < -260:
                c[0] = W + 120

    def draw_top(self, s):
        g = self.g
        for x, y, _ in self.clouds:
            g.alpha_rect(s, (x, y, 240, 130), (225, 225, 230), 100)
            g.alpha_rect(s, (x + 30, y - 24, 140, 30), (225, 225, 230), 100)

def draw_cat(s, x, y, u, face, col=(150, 150, 160), t=0.0):

    def R(dx, dy, w, h, c):
        px = x + (dx if face > 0 else -dx - w) * u
        pygame.draw.rect(s, c, (px, y + dy * u, w * u, h * u))
    R(-5, -2, 8, 4, col)
    R(2, -4, 5, 5, col)
    R(2, -6, 1, 2, col)
    R(6, -6, 1, 2, col)
    R(4, -3, 1, 1, BLACK)
    R(6, -3, 1, 1, BLACK)
    R(5, -1, 1, 1, (255, 150, 170))
    sw = int(math.sin(t * 9) * 2)
    R(-7, -3 + sw, 2, 1, col)
    R(-8, -4 + sw, 1, 2, col)
    leg = int(t * 8) % 2
    R(-4, 2, 1, 2 + leg, col)
    R(-1, 2, 1, 3 - leg, col)
    R(0, 2, 1, 2 + leg, col)
    R(2, 2, 1, 3 - leg, col)

@reg
class NyanCat(Event):
    name = 'NYAN CAT'
    sub = 'NYA NYA NYA NYA NYA'
    dur = 8
    group = 'critter'

    def start(self):
        self.dir = random.choice((-1, 1))
        self.y0 = random.uniform(110, H - 110)
        self.speed = (W + 300) / 6.4
        self.g.play('nyan')

    def pos(self):
        x = -150 + self.speed * self.t if self.dir > 0 else W + 150 - self.speed * self.t
        return (x, self.y0 + 38 * math.sin(self.t * 2.6))

    def update(self, dt):
        g = self.g
        x, y = self.pos()
        for b in g.real_balls():
            if g.bounce_rect(b, (x - 40, y - 26, 80, 52), 1.06):
                g.play('hit', 0.6)
                g.parts.burst(b.x, b.y, hsv(self.t), 10, 260, 0.5)
        if self.t > 6.7:
            self.done = True

    def draw_front(self, s):
        x, y = self.pos()
        d = self.dir
        cols = [(255, 0, 0), (255, 150, 0), (255, 255, 0), (0, 255, 0), (0, 150, 255), (150, 80, 255)]
        for xx in range(0, 420, 8):
            tx = x - d * (36 + xx)
            if tx < -8 or tx > W:
                continue
            wob = int(math.sin(xx * 0.08 + self.t * 12) * 5)
            for i, c in enumerate(cols):
                pygame.draw.rect(s, c, (tx, y - 24 + i * 8 + wob, 8, 8))
        pygame.draw.rect(s, (255, 205, 150), (x - 34, y - 26, 68, 52))
        pygame.draw.rect(s, (255, 130, 190), (x - 28, y - 20, 56, 40))
        for sx, sy in ((-18, -12), (6, -4), (-8, 8), (18, 10), (14, -14)):
            pygame.draw.rect(s, (220, 40, 100), (x + sx, y + sy, 4, 4))
        hx = x + d * 38
        pygame.draw.rect(s, (130, 130, 140), (hx - 18, y - 16, 36, 30))
        pygame.draw.rect(s, (130, 130, 140), (hx - 18, y - 24, 8, 8))
        pygame.draw.rect(s, (130, 130, 140), (hx + 10, y - 24, 8, 8))
        pygame.draw.rect(s, BLACK, (hx - 10, y - 8, 4, 6))
        pygame.draw.rect(s, BLACK, (hx + 6, y - 8, 4, 6))
        pygame.draw.rect(s, (255, 150, 170), (hx - 14, y + 2, 6, 6))
        pygame.draw.rect(s, (255, 150, 170), (hx + 8, y + 2, 6, 6))
        for k in range(4):
            lx = x - 24 + k * 16 + (4 if int(self.t * 10) % 2 else 0)
            pygame.draw.rect(s, (130, 130, 140), (lx, y + 24, 8, 8))

@reg
class CatAttack(Event):
    name = 'CAT ATTACK'
    sub = 'IT WANTS THE BALL. THE BALL IS A TOY.'
    dur = 12
    group = 'critter'

    def start(self):
        self.x, self.y = (random.choice((60, W - 60)), random.uniform(100, H - 100))
        self.face = 1
        self.rest = 0.0
        self.t_ = 0.0

    def update(self, dt):
        g = self.g
        self.t_ += dt
        if self.rest > 0:
            self.rest -= dt
            return
        rb = g.real_balls()
        if not rb:
            return
        b = min(rb, key=lambda q: math.hypot(q.x - self.x, q.y - self.y))
        dx, dy = (b.x - self.x, b.y - self.y)
        d = math.hypot(dx, dy) or 1.0
        sp = 190.0
        self.x += dx / d * sp * dt
        self.y += dy / d * sp * dt
        self.face = 1 if dx >= 0 else -1
        if d < 46:
            a = random.uniform(-1.1, 1.1) + (0 if random.random() < 0.5 else math.pi)
            spd = max(b.speed(), BASE_SPEED) * 1.05
            b.vx, b.vy = (math.cos(a) * spd, math.sin(a) * spd)
            g.play('meow')
            g.popup(self.x, self.y - 40, 'MEOW!', (255, 200, 120), 24)
            g.parts.burst(b.x, b.y, (255, 220, 160), 10, 220, 0.4)
            self.rest = 1.1

    def draw_front(self, s):
        draw_cat(s, self.x, self.y, 5, self.face, (200, 140, 70) if self.rest <= 0 else (150, 150, 160), self.t_)
        if self.rest > 0 and int(self.t_ * 4) % 2:
            self.g.text_at(s, 'ZZZ' if self.rest > 0.6 else '!', self.x, self.y - 50, 22, WHITE)

@reg
class Roomba(Event):
    name = 'ROOMBA'
    sub = 'IT CLEANS. IT BOUNCES. IT JUDGES.'
    dur = 13
    group = 'critter'

    def start(self):
        self.x, self.y = (random.uniform(300, 500), random.uniform(120, H - 120))
        a = random.uniform(0, math.tau)
        self.vx, self.vy = (math.cos(a) * 150, math.sin(a) * 150)
        self.r = 30
        self.cd = 0.0

    def update(self, dt):
        g = self.g
        s = g.sdt
        self.x += self.vx * s
        self.y += self.vy * s
        if self.x < 120 or self.x > W - 120:
            self.vx = -self.vx
            self.x = clamp(self.x, 120, W - 120)
            self.vy += random.uniform(-60, 60)
        if self.y < self.r or self.y > H - self.r:
            self.vy = -self.vy
            self.y = clamp(self.y, self.r, H - self.r)
            self.vx += random.uniform(-60, 60)
        self.cd -= dt
        if self.cd <= 0:
            self.cd = 0.5
            g.play('vac', 0.25)
        for b in g.real_balls():
            if g.bounce_circle(b, self.x, self.y, self.r, 1.03):
                g.play('beep')
                g.popup(self.x, self.y - 40, 'BEEP BOOP', (120, 255, 160), 16)

    def draw_front(self, s):
        x, y, r = (int(self.x), int(self.y), self.r)
        pygame.draw.circle(s, (70, 70, 80), (x, y), r)
        pygame.draw.circle(s, (170, 170, 180), (x, y), r, 4)
        pygame.draw.circle(s, (40, 40, 50), (x, y), 12)
        pygame.draw.rect(s, (80, 255, 120) if int(self.t * 3) % 2 else (255, 80, 80), (x - 4, y - 4, 8, 8))
        a = self.t * 8
        pygame.draw.line(s, WHITE, (x + math.cos(a) * 16, y + math.sin(a) * 16), (x + math.cos(a) * 36, y + math.sin(a) * 36), 2)

@reg
class FingerOfGod(Event):
    name = 'THE FINGER'
    sub = 'IT POKES THE BALL'
    dur = 11
    group = 'critter'

    def start(self):
        self.cd = 1.0
        self.f = None

    def update(self, dt):
        g = self.g
        if self.f is None:
            self.cd -= dt
            rb = g.real_balls()
            if self.cd <= 0 and rb:
                b = random.choice(rb)
                self.f = [clamp(b.x + b.vx * 0.5, 120, W - 120), 0.0, random.random() < 0.5, False]
                g.play('warn')
        else:
            f = self.f
            f[1] += dt
            if f[1] > 0.7 and (not f[3]):
                f[3] = True
                g.play('whoosh')
            if f[3]:
                tip = self.tip()
                for b in g.real_balls():
                    if abs(b.x - f[0]) < 26 + b.size / 2 and abs(b.y - tip) < 30 + b.size / 2:
                        d = 1 if b.x >= f[0] else -1
                        sp = min(MAX_SPEED * 0.9, max(b.speed(), BASE_SPEED) * 1.2)
                        b.vx, b.vy = (d * sp * 0.8, (1 if f[2] else -1) * sp * 0.5)
                        g.play('boing')
                        g.popup(b.x, b.y - 30, 'BOOP!', (255, 200, 150), 24)
            if f[1] > 1.4:
                self.f = None
                self.cd = random.uniform(1.0, 1.8)

    def tip(self):
        f = self.f
        k = clamp((f[1] - 0.7) / 0.15, 0, 1) if f[1] < 1.0 else clamp(1 - (f[1] - 1.0) / 0.4, 0, 1)
        return k * (H * 0.55) if f[2] else H - k * (H * 0.55)

    def draw_front(self, s):
        if self.f is None:
            return
        x, ph, top, go = self.f
        if not go:
            if int(ph * 12) % 2:
                pygame.draw.ellipse(s, (255, 60, 60), (x - 30, H - 12 if top else 0, 60, 12))
                self.g.text_at(s, '!', x, H - 40 if top else 40, 30, (255, 60, 60))
            return
        tip = self.tip()
        skin = (255, 205, 160)
        if top:
            pygame.draw.rect(s, skin, (x - 24, 0, 48, tip))
            pygame.draw.rect(s, (255, 230, 220), (x - 14, tip - 14, 28, 12))
        else:
            pygame.draw.rect(s, skin, (x - 24, tip, 48, H - tip))
            pygame.draw.rect(s, (255, 230, 220), (x - 14, tip + 4, 28, 12))

@reg
class SeagullBandit(Event):
    name = 'SEAGULL BANDIT'
    sub = 'SQUAWK! IT STEALS THE BALL'
    dur = 12
    group = 'critter'

    @classmethod
    def ok(cls, g):
        return bool(g.real_balls())

    def start(self):
        self.x, self.y = (random.choice((-40, W + 40)), 90.0)
        self.st = 'in'
        self.tm = 0.0
        self.ball = None
        self.tx = W / 2
        self.g.play('squawk')

    def update(self, dt):
        g = self.g
        s = g.sdt
        self.tm += s
        if self.st == 'in':
            rb = [b for b in g.real_balls() if not b.stuck]
            if not rb:
                self.done = True
                return
            tgt = min(rb, key=lambda b: math.hypot(b.x - self.x, b.y - self.y))
            dx, dy = (tgt.x - self.x, tgt.y - self.y)
            d = math.hypot(dx, dy) or 1.0
            self.x += dx / d * 330 * s
            self.y += dy / d * 330 * s
            if d < 24:
                self.ball = tgt
                tgt.captured = True
                self.st = 'carry'
                self.tm = 0.0
                self.tx = random.uniform(220, W - 220)
                g.play('squawk')
        elif self.st == 'carry':
            self.x += clamp(self.tx - self.x, -260 * s, 260 * s)
            self.y += (110 - self.y) * min(1.0, s * 4)
            b = self.ball
            b.x, b.y = (self.x, self.y + 22)
            if abs(self.tx - self.x) < 6 or self.tm > 2.2:
                b.captured = False
                a = random.uniform(0.4, 1.2)
                sp = max(b.speed(), BASE_SPEED)
                b.vx, b.vy = (random.choice((-1, 1)) * math.cos(a) * sp, math.sin(a) * sp)
                g.play('pop')
                g.popup(self.x, self.y, 'DROPPED IT', WHITE, 20)
                self.st = 'out'
        else:
            self.y -= 240 * s
            self.x += 160 * s * sign(self.x - W / 2)
            if self.y < -60:
                self.done = True

    def end(self):
        if self.ball:
            self.ball.captured = False

    def draw_front(self, s):
        x, y = (int(self.x), int(self.y))
        flap = int(self.t * 10) % 2
        wing = -14 if flap else 10
        pygame.draw.rect(s, WHITE, (x - 14, y - 6, 28, 12))
        pygame.draw.rect(s, WHITE, (x + 10, y - 12, 12, 12))
        pygame.draw.rect(s, (255, 170, 0), (x + 22, y - 8, 8, 4))
        pygame.draw.rect(s, BLACK, (x + 16, y - 10, 4, 4))
        pygame.draw.polygon(s, (190, 190, 200), [(x - 10, y - 4), (x + 8, y - 4), (x - 6, y + wing - 6)])
        pygame.draw.polygon(s, (190, 190, 200), [(x - 10, y + 2), (x + 8, y + 2), (x - 6, y - wing + 10)])
        pygame.draw.rect(s, (255, 170, 0), (x - 16, y + 6, 4, 8))

@reg
class ChickenCrossing(Event):
    name = 'CHICKEN CROSSING'
    sub = 'WHY DID THE CHICKEN CROSS THE COURT?'
    dur = 11
    group = 'critter'

    def start(self):
        self.ch = []
        for i in range(3):
            self.ch.append({'x': random.uniform(260, 540), 'y': -30 - i * 150 if i % 2 == 0 else H + 30 + i * 150, 'vy': 110 if i % 2 == 0 else -110, 'cd': 0.0})
        self.g.play('cluck')

    def update(self, dt):
        g = self.g
        for c in self.ch:
            c['y'] += c['vy'] * g.sdt
            c['cd'] -= dt
            for b in g.real_balls():
                if c['cd'] <= 0 and abs(b.x - c['x']) < 24 + b.size / 2 and (abs(b.y - c['y']) < 22 + b.size / 2):
                    c['cd'] = 0.5
                    b.vx = -b.vx
                    b.set_speed(min(MAX_SPEED * 0.9, b.speed() * 1.12))
                    g.play('cluck')
                    g.popup(c['x'], c['y'] - 30, 'BAWK!', (255, 200, 80), 22)
                    g.parts.burst(c['x'], c['y'], WHITE, 12, 220, 0.8, 4, 200)
        if all((c['y'] > H + 60 or c['y'] < -60 for c in self.ch)) and self.t > 3:
            self.done = True

    def draw_front(self, s):
        for c in self.ch:
            x, y = (int(c['x']), int(c['y']))
            fl = int(self.t * 8) % 2
            pygame.draw.rect(s, WHITE, (x - 14, y - 12, 28, 24))
            pygame.draw.rect(s, WHITE, (x - 6, y - 24, 16, 14))
            pygame.draw.rect(s, (230, 40, 40), (x - 2, y - 30, 8, 8))
            pygame.draw.rect(s, (255, 190, 0), (x + 8, y - 18, 8, 4))
            pygame.draw.rect(s, BLACK, (x + 2, y - 20, 4, 4))
            pygame.draw.rect(s, (255, 190, 0), (x - 8, y + 12, 4, 8 + 4 * fl))
            pygame.draw.rect(s, (255, 190, 0), (x + 4, y + 12, 4, 12 - 4 * fl))
            pygame.draw.rect(s, (220, 220, 220), (x - 18, y - 4 - 6 * fl, 8, 12))

@reg
class CatsAndDogs(Event):
    name = 'RAINING CATS AND DOGS'
    sub = 'LITERALLY'
    dur = 11
    group = 'critter'

    def start(self):
        self.drops = []
        self.cd = 0.0

    def update(self, dt):
        g = self.g
        self.cd -= dt
        if self.cd <= 0 and self.t < self.dur - 3:
            self.cd = 0.5
            self.drops.append({'x': random.uniform(130, W - 130), 'y': -24.0, 'cat': random.random() < 0.5, 'vy': random.uniform(140, 230), 'hit': 0.0})
        for d in self.drops:
            d['y'] += d['vy'] * g.sdt
            d['hit'] -= dt
            for b in g.real_balls():
                if g.bounce_circle(b, d['x'], d['y'], 18, 1.02):
                    d['hit'] = 0.3
                    g.play('meow' if d['cat'] else 'quack', 0.5)
        for d in list(self.drops):
            if d['y'] > H + 30:
                self.drops.remove(d)

    def draw_front(self, s):
        for d in self.drops:
            x, y = (int(d['x']), int(d['y']))
            if d['cat']:
                c = (170, 170, 180)
                pygame.draw.circle(s, c, (x, y), 16)
                pygame.draw.polygon(s, c, [(x - 16, y - 6), (x - 14, y - 24), (x - 4, y - 14)])
                pygame.draw.polygon(s, c, [(x + 16, y - 6), (x + 14, y - 24), (x + 4, y - 14)])
                pygame.draw.rect(s, BLACK, (x - 8, y - 4, 4, 6))
                pygame.draw.rect(s, BLACK, (x + 4, y - 4, 4, 6))
                pygame.draw.rect(s, (255, 150, 170), (x - 2, y + 4, 4, 4))
            else:
                c = (170, 110, 60)
                pygame.draw.circle(s, c, (x, y), 16)
                pygame.draw.rect(s, (110, 60, 30), (x - 24, y - 12, 10, 22))
                pygame.draw.rect(s, (110, 60, 30), (x + 14, y - 12, 10, 22))
                pygame.draw.rect(s, BLACK, (x - 8, y - 4, 4, 4))
                pygame.draw.rect(s, BLACK, (x + 4, y - 4, 4, 4))
                pygame.draw.rect(s, BLACK, (x - 3, y + 4, 6, 6))
                if int(self.t * 6) % 2:
                    pygame.draw.rect(s, (255, 100, 120), (x - 2, y + 10, 4, 6))

@reg
class Squirrel(Event):
    name = 'SQUIRREL!'
    dur = 6
    group = 'critter'

    def start(self):
        g = self.g
        self.side = random.choice((-1, 1))
        self.sub = '%s IS DISTRACTED' % g.who(self.side)
        self.dir = random.choice((-1, 1))
        self.x = -30 if self.dir > 0 else W + 30
        self.y0 = random.uniform(130, H - 130)
        self.y = self.y0
        g.paddle(self.side).mod(self, 'frozen', 1)
        g.play('whoosh')

    def update(self, dt):
        g = self.g
        self.x += self.dir * (W + 60) / 5.0 * dt
        self.y = self.y0 + 110 * math.sin(self.t * 3.2)
        p = g.paddle(self.side)
        d = self.y - p.cy()
        p.y = clamp(p.y + clamp(d, -430 * dt, 430 * dt), 0, H - p.h)
        if self.t > 5.2:
            self.done = True

    def draw_front(self, s):
        x, y = (int(self.x), int(self.y))
        f = self.dir
        pygame.draw.rect(s, (160, 90, 40), (x - 10, y - 4, 20, 12))
        pygame.draw.rect(s, (160, 90, 40), (x + (6 if f > 0 else -16), y - 12, 10, 10))
        pygame.draw.rect(s, BLACK, (x + (12 if f > 0 else -12), y - 10, 4, 4))
        for k in range(4):
            pygame.draw.rect(s, (200, 120, 60), (x - f * (14 + k * 4), y - 16 - k * 6 + k % 2 * 4, 10, 10))
        self.g.text_at(s, '!', x, y - 44, 30, (255, 230, 0))

@reg
class RushHour(Event):
    name = 'RUSH HOUR'
    sub = 'BEEP BEEP'
    dur = 11
    group = 'world'

    def start(self):
        self.cars = []
        for i, x in enumerate((300, 400, 500)):
            d = 1 if i % 2 == 0 else -1
            self.cars.append({'x': x, 'y': random.uniform(-100, H + 100), 'v': d * random.uniform(170, 260), 'col': random.choice(((230, 60, 60), (60, 120, 255), (255, 200, 0), (80, 220, 100))), 'cd': 0.0})

    def update(self, dt):
        g = self.g
        for c in self.cars:
            c['y'] += c['v'] * g.sdt
            c['cd'] -= dt
            if c['y'] > H + 70:
                c['y'] = -70
            elif c['y'] < -70:
                c['y'] = H + 70
            for b in g.real_balls():
                if g.bounce_rect(b, (c['x'] - 18, c['y'] - 34, 36, 68), 1.04):
                    g.play('honk', 0.5)
                    c['cd'] = 0.3
                    g.popup(c['x'], c['y'] - 44, 'HONK!', (255, 255, 120), 20)

    def draw_back(self, s):
        for x in (300, 400, 500):
            for y in range(0, H, 40):
                pygame.draw.rect(s, (60, 60, 60), (x + 28, y, 4, 20))

    def draw_front(self, s):
        for c in self.cars:
            x, y = (int(c['x']), int(c['y']))
            pygame.draw.rect(s, c['col'], (x - 18, y - 34, 36, 68))
            pygame.draw.rect(s, (160, 220, 255), (x - 12, y - 18 if c['v'] > 0 else y + 4, 24, 14))
            pygame.draw.rect(s, (255, 255, 160), (x - 16, y + (28 if c['v'] > 0 else -34), 8, 6))
            pygame.draw.rect(s, (255, 255, 160), (x + 8, y + (28 if c['v'] > 0 else -34), 8, 6))
            pygame.draw.rect(s, BLACK, (x - 22, y - 26, 4, 14))
            pygame.draw.rect(s, BLACK, (x + 18, y + 12, 4, 14))

@reg
class BeeSwarm(Event):
    name = 'ANGRY BEES'
    sub = 'THEY CHASE WHOEVER HIT THE BALL LAST'
    dur = 10
    group = 'critter'

    def start(self):
        self.bees = [[random.uniform(300, 500), random.uniform(100, H - 100), 0.0, 0.0] for _ in range(14)]
        self.target = -1
        self.cd = 0.0

    def update(self, dt):
        g = self.g
        rb = g.real_balls()
        if rb and rb[0].last_hit:
            self.target = rb[0].last_hit
        p = g.paddle(self.target)
        tx, ty = (p.x + 7, p.cy())
        self.cd -= dt
        near = 0
        for b in self.bees:
            dx, dy = (tx - b[0], ty - b[1])
            d = math.hypot(dx, dy) or 1.0
            b[2] += (dx / d * 260 + random.uniform(-220, 220) - b[2]) * min(1.0, dt * 4)
            b[3] += (dy / d * 260 + random.uniform(-220, 220) - b[3]) * min(1.0, dt * 4)
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            if d < 40:
                near += 1
        if near >= 3 and self.cd <= 0:
            self.cd = 1.8
            p.mod(None, 'invert', 1, 1.3)
            g.play('buzz')
            g.popup(tx, ty - 50, 'STUNG!', (255, 220, 0), 22)

    def draw_front(self, s):
        for b in self.bees:
            x, y = (int(b[0]), int(b[1]))
            pygame.draw.rect(s, (255, 220, 0), (x - 4, y - 2, 8, 6))
            pygame.draw.rect(s, BLACK, (x - 1, y - 2, 2, 6))
            pygame.draw.rect(s, (200, 230, 255), (x - 2, y - 6 - int(self.t * 40) % 2 * 2, 4, 4))

@reg
class RubberDucks(Event):
    name = 'RUBBER DUCKS'
    sub = 'BATH TIME'
    dur = 12
    group = 'critter'

    def start(self):
        self.d = [[random.uniform(230, 570), random.uniform(60, H - 60), random.uniform(-70, 70), random.uniform(-70, 70)] for _ in range(5)]

    def update(self, dt):
        g = self.g
        for k in self.d:
            k[0] += k[2] * g.sdt
            k[1] += k[3] * g.sdt
            if not 200 < k[0] < W - 200:
                k[2] = -k[2]
            if not 30 < k[1] < H - 30:
                k[3] = -k[3]
            for b in g.real_balls():
                if g.bounce_circle(b, k[0], k[1], 20, 1.03):
                    g.play('quack', 0.6)
                    g.parts.burst(k[0], k[1], (255, 230, 0), 6, 140, 0.4)

    def draw_front(self, s):
        for x, y, _, _ in self.d:
            x, y = (int(x), int(y))
            pygame.draw.circle(s, (255, 220, 0), (x, y + 4), 16)
            pygame.draw.circle(s, (255, 220, 0), (x + 8, y - 12), 10)
            pygame.draw.rect(s, (255, 130, 0), (x + 16, y - 12, 10, 6))
            pygame.draw.rect(s, BLACK, (x + 8, y - 16, 4, 4))
            pygame.draw.rect(s, (255, 250, 150), (x - 14, y + 2, 12, 8))

@reg
class Pinata(Event):
    name = 'PINATA'
    sub = 'HIT IT 3 TIMES - CANDY = A POINT FOR WHOEVER HIT LAST'
    dur = 13
    group = 'world'

    def start(self):
        self.hits = 0
        self.cd = 0.0
        self.burst = 0.0
        self.x = W / 2

    def update(self, dt):
        g = self.g
        self.x = W / 2 + 150 * math.sin(self.t * 1.3)
        self.cd -= dt
        if self.burst > 0:
            self.burst -= dt
            if self.burst <= 0:
                self.done = True
            return
        for b in g.real_balls():
            if self.cd <= 0 and g.bounce_circle(b, self.x, 120, 36, 1.02):
                self.hits += 1
                self.cd = 0.4
                g.play('hit')
                g.parts.burst(self.x, 120, hsv(random.random()), 14, 260, 0.6, 5)
                if self.hits >= 3:
                    self.burst = 1.2
                    side = b.last_hit
                    g.play('powerup')
                    for _ in range(5):
                        g.parts.burst(self.x, 130, hsv(random.random()), 20, 400, 1.2, 6, 500)
                    if side:
                        g.scores[0 if side < 0 else 1] += 1
                        g.popup(self.x, 190, 'CANDY! %s +1' % g.who(side), GOLD, 26)
                    else:
                        g.popup(self.x, 190, 'CANDY!', GOLD, 26)

    def draw_front(self, s):
        if self.burst > 0:
            return
        x = int(self.x)
        pygame.draw.line(s, (200, 200, 200), (x, 0), (x, 90), 2)
        cols = [(255, 60, 120), (60, 200, 255), (255, 220, 0), (120, 255, 100)]
        for k in range(4):
            pygame.draw.rect(s, cols[(k + self.hits) % 4], (x - 36 + k * 18, 92 + k % 2 * 4, 18, 56))
        pygame.draw.rect(s, (255, 255, 255), (x - 44, 100, 12, 8))
        pygame.draw.rect(s, (255, 255, 255), (x + 32, 100, 12, 8))
        pygame.draw.rect(s, BLACK, (x - 14, 110, 4, 6))
        pygame.draw.rect(s, BLACK, (x + 10, 110, 4, 6))
        for k in range(3 - self.hits):
            pygame.draw.rect(s, GOLD, (x - 22 + k * 18, 162, 12, 8))

@reg
class CoinFlip(Event):
    name = 'COIN FLIP'
    sub = 'HEADS = PLAYER 1 +1   TAILS = THE OTHER +1'
    dur = 2.8

    def start(self):
        self.heads = random.random() < 0.5
        self.paid = False
        self.g.play('flip')

    def pay(self):
        if self.paid:
            return
        self.paid = True
        g = self.g
        side = -1 if self.heads else 1
        g.scores[0 if side < 0 else 1] += 1
        g.play('cash')
        g.popup(W / 2, 330, '%s +1' % g.who(side), GOLD, 34)

    def update(self, dt):
        if self.t > 2.2:
            self.pay()

    def end(self):
        self.pay()

    def draw_front(self, s):
        k = clamp(self.t / 2.2, 0, 1)
        y = H / 2 - 160 * math.sin(k * math.pi)
        w = int(abs(math.cos(self.t * 14)) * 44) + 4 if k < 1 else 44
        x = W // 2
        pygame.draw.ellipse(s, GOLD, (x - w // 2, y - 22, w, 44))
        pygame.draw.ellipse(s, (255, 250, 150), (x - w // 2, y - 22, w, 44), 4)
        if k >= 1 and w > 20:
            self.g.text_at(s, 'H' if self.heads else 'T', x, y, 30, (120, 80, 0))

@reg
class TaxMan(Event):
    name = 'THE TAX MAN'
    sub = 'THE LEADER PAYS 1 POINT'
    dur = 0

    @classmethod
    def ok(cls, g):
        return g.scores[0] != g.scores[1] and max(g.scores) >= 2

    def start(self):
        g = self.g
        i = 0 if g.scores[0] > g.scores[1] else 1
        g.scores[i] -= 1
        g.play('cash')
        g.flash((60, 200, 90), 90)
        g.popup(W / 4 if i == 0 else 3 * W / 4, 120, '-1 TAXES!', (255, 100, 100), 34)
