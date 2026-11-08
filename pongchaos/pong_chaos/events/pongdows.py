from __future__ import annotations
import math
import random
import pygame
from ..core import *
from .base import *

from .ui import bubble, para

XP_MSG = [('ERROR', 'PADDLE.EXE HAS STOPPED WORKING'), ('WARNING', 'YOUR BALL IS INFECTED WITH 47 VIRUSES'), ('SYSTEM', 'NOT ENOUGH RAM. TRY DOWNLOADING MORE.'), ('QUESTION', 'DO YOU WANT TO WIN? [YES] [YES]'), ('CLIPPY', 'IT LOOKS LIKE YOU ARE PLAYING PONG. NEED HELP?'), ('ERROR', 'KEYBOARD NOT FOUND. PRESS ANY KEY.'), ('UPDATE', 'WINDOWS NEEDS TO RESTART TO FINISH RESTARTING'), ('ALERT', 'FREE SMILEYS!!! CLICK NOWWW'), ('ERROR', 'THE CPU HAS PERFORMED AN ILLEGAL MOVE'), ('MESSENGER', 'TOASTER99 SENT YOU A WINK'), ('DISK', 'C: IS FULL OF PONG. DELETE SOME PONG?'), ('ERROR', 'MOUSE MOVED. RESTART TO APPLY CHANGES.')]
XP_CLIPPY = ['IT LOOKS LIKE YOU ARE LOSING!', 'NEED HELP CLOSING WINDOWS?', 'HAVE YOU TRIED TURNING IT OFF?', "I CAN'T HELP. I'M JUST A PAPERCLIP."]

def xp_cursor(s, x, y, col, tag, click=False):
    x, y = (int(x), int(y))
    pts = [(px_ * 1.4, py_ * 1.4) for px_, py_ in [(0, 0), (0, 22), (6, 17), (11, 28), (15, 26), (10, 16), (18, 16)]]
    pygame.draw.polygon(s, BLACK, [(x + px_ * 1.0 + 2, y + py_ * 1.0 + 2) for px_, py_ in pts])
    pygame.draw.polygon(s, col, [(x + px_, y + py_) for px_, py_ in pts])
    pygame.draw.polygon(s, BLACK, [(x + px_, y + py_) for px_, py_ in pts], 2)
    if click:
        pygame.draw.circle(s, col, (x, y), 18, 2)

@reg
class PongdowsXP(Mode):
    name = 'PONGDOWS XP'
    sub = 'TWO CURSORS. ONE DESKTOP. CLOSE THE WINDOWS FIRST!'
    dur = 19
    cap = 19
    limit = 17
    weight = 2.5
    BOOT = 1.5
    hint1 = 'WASD / ARROWS MOVE     SPACE / ENTER CLICK'
    hint2 = 'P1: WASD + SPACE     P2: ARROWS + ENTER'

    def begin(self):
        self.wins = []
        self.closed = [0, 0]
        self.cur = [[220.0, 300.0], [580.0, 300.0]]
        self.fp = [False, False]
        self.clk = [0.0, 0.0]
        self.spawn_t = 0.2
        self.tgt = None
        self.think = 0.4
        self.clippy = 0
        self.g.play('xpstart')

    def new_window(self, near=None):
        r = random.random()
        kind = 'gold' if r < 0.08 else 'flee' if r < 0.2 else 'virus' if r < 0.34 else 'norm'
        w, h = (random.randint(220, 270), random.randint(104, 128))
        if near:
            x, y = (near[0] + random.randint(-60, 60), near[1] + random.randint(-40, 40))
        else:
            x, y = (random.randint(110, W - w - 20), random.randint(30, H - 110 - h))
        x, y = (clamp(x, 100, W - w - 10), clamp(y, 24, H - 100 - h))
        title, msg = random.choice(XP_MSG)
        if kind == 'gold':
            title, msg = ('WINNER!!', 'CLOSE ME FIRST FOR 3 POINTS')
        elif kind == 'virus':
            title, msg = ('FREE SMILEYS', 'TOTALLY SAFE. DEFINITELY NOT A VIRUS.')
        elif kind == 'flee':
            title, msg = ('UNCLOSABLE', 'I AM TOO FAST FOR YOU')
        ang = random.uniform(0, math.tau)
        self.wins.append({'x': float(x), 'y': float(y), 'w': w, 'h': h, 'title': title, 'msg': msg, 'kind': kind, 'vx': math.cos(ang) * 150, 'vy': math.sin(ang) * 150})
        self.g.play('xperr', 0.5)

    def xrect(self, w):
        return (w['x'] + w['w'] - 24, w['y'] + 3, 20, 18)

    def inside(self, w, px, py):
        return w['x'] <= px <= w['x'] + w['w'] and w['y'] <= py <= w['y'] + w['h']

    def covered(self, idx):
        w = self.wins[idx]
        xr = self.xrect(w)
        cx, cy = (xr[0] + xr[2] / 2, xr[1] + xr[3] / 2)
        return any((self.inside(w2, cx, cy) for w2 in self.wins[idx + 1:]))

    def click(self, i):
        g = self.g
        c = self.cur[i]
        self.clk[i] = 0.18
        g.play('click', 0.5)
        for idx in range(len(self.wins) - 1, -1, -1):
            w = self.wins[idx]
            if self.inside(w, c[0], c[1]):
                xr = self.xrect(w)
                if xr[0] - 4 <= c[0] <= xr[0] + xr[2] + 4 and xr[1] - 4 <= c[1] <= xr[1] + xr[3] + 6:
                    self.close(w, i)
                else:
                    self.wins.append(self.wins.pop(idx))
                return

    def close(self, w, i):
        g = self.g
        self.wins.remove(w)
        k = w['kind']
        side = -1 if i == 0 else 1
        cx, cy = (w['x'] + w['w'] / 2, w['y'] + w['h'] / 2)
        col = (120, 220, 255) if i == 0 else (255, 140, 200)
        if k == 'virus':
            g.play('uhoh')
            g.popup(cx, cy, 'VIRUS! 2 MORE!', (255, 80, 80), 22)
            self.new_window((cx, cy))
            self.new_window((cx, cy))
            return
        n = 3 if k == 'gold' else 2 if k == 'flee' else 1
        self.closed[i] += n
        g.play('coin' if n == 1 else 'powerup')
        g.parts.burst(cx, cy, col, 14, 260, 0.5, 5)
        g.popup(cx, cy, '+%d' % n, col, 26)

    def tick(self, dt):
        g = self.g
        if self.t < self.BOOT:
            return
        for k in range(2):
            self.clk[k] = max(0.0, self.clk[k] - dt)
        self.spawn_t -= dt
        if self.spawn_t <= 0 and self.t < self.limit - 2.5 and (len(self.wins) < 9):
            self.spawn_t = max(0.42, 1.05 - (self.t - self.BOOT) * 0.05)
            self.new_window()
        for w in self.wins:
            if w['kind'] == 'flee':
                best = None
                for c in self.cur:
                    d = math.hypot(c[0] - (w['x'] + w['w'] / 2), c[1] - (w['y'] + w['h'] / 2))
                    if best is None or d < best[0]:
                        best = (d, c)
                if best[0] < 170:
                    dx, dy = (w['x'] + w['w'] / 2 - best[1][0], w['y'] + w['h'] / 2 - best[1][1])
                    d = math.hypot(dx, dy) or 1.0
                    w['vx'], w['vy'] = (dx / d * 230, dy / d * 230)
                w['x'] += w['vx'] * dt
                w['y'] += w['vy'] * dt
                if w['x'] < 100 or w['x'] > W - w['w'] - 10:
                    w['vx'] = -w['vx']
                    w['x'] = clamp(w['x'], 100, W - w['w'] - 10)
                if w['y'] < 24 or w['y'] > H - 100 - w['h']:
                    w['vy'] = -w['vy']
                    w['y'] = clamp(w['y'], 24, H - 100 - w['h'])
        for i, side in enumerate((-1, 1)):
            c = self.cur[i]
            if is_cpu(g, side):
                self.cpu_move(dt)
                continue
            L, R, U, D, F = human_keys(g, side)
            if g.mode == 1 and side < 0 and pygame.key.get_pressed()[pygame.K_RETURN]:
                F = True
            c[0] = clamp(c[0] + (int(R) - int(L)) * 360 * dt, 0, W - 4)
            c[1] = clamp(c[1] + (int(D) - int(U)) * 360 * dt, 0, H - 80)
            if F and (not self.fp[i]):
                self.click(i)
            self.fp[i] = F

    def cpu_move(self, dt):
        g = self.g
        c = self.cur[1]
        self.think -= dt
        if self.tgt is not None and self.tgt not in self.wins:
            self.tgt = None
        if self.tgt is None and self.wins and (self.think <= 0):
            best = None
            for idx, w in enumerate(self.wins):
                if self.covered(idx):
                    continue
                xr = self.xrect(w)
                d = math.hypot(xr[0] + 10 - c[0], xr[1] + 9 - c[1])
                bonus = -80 if w['kind'] == 'gold' else 120 if w['kind'] == 'virus' else 0
                if best is None or d + bonus < best[0]:
                    best = (d + bonus, w)
            if best:
                self.tgt = best[1]
        if self.tgt is None:
            return
        xr = self.xrect(self.tgt)
        dx, dy = (xr[0] + 10 - c[0], xr[1] + 9 - c[1])
        d = math.hypot(dx, dy)
        sp = (230, 290, 360)[g.diff] * dt
        if d > 6:
            c[0] += dx / d * min(sp, d)
            c[1] += dy / d * min(sp, d)
        else:
            self.click(1)
            self.tgt = None
            self.think = random.uniform(0.25, 0.55) * (1.3, 1.0, 0.75)[g.diff]

    def on_timeout(self):
        g = self.g
        a, b = self.closed
        if a == b:
            g.popup(W / 2, H / 2, 'TIE! %d - %d' % (a, b), WHITE, 30)
        else:
            w = -1 if a > b else 1
            self.award(w, 2 if abs(a - b) >= 4 else 1, '%s WINS %d - %d' % (g.who(w), max(a, b), min(a, b)))

    def draw_window(self, s, w):
        g = self.g
        x, y, ww, hh = (int(w['x']), int(w['y']), w['w'], w['h'])
        k = w['kind']
        tcol = {'norm': (0, 84, 227), 'virus': (200, 30, 30), 'gold': (230, 170, 0), 'flee': (140, 40, 200)}[k]
        pygame.draw.rect(s, (10, 40, 110), (x + 5, y + 5, ww, hh))
        pygame.draw.rect(s, tcol, (x, y, ww, hh))
        pygame.draw.rect(s, (236, 233, 216), (x + 4, y + 26, ww - 8, hh - 30))
        g.text_at(s, w['title'], x + 10, y + 8, 15, WHITE, center=False)
        xr = self.xrect(w)
        pygame.draw.rect(s, (214, 76, 52), (xr[0], xr[1], xr[2], xr[3]))
        pygame.draw.rect(s, WHITE, (xr[0], xr[1], xr[2], xr[3]), 2)
        pygame.draw.line(s, WHITE, (xr[0] + 5, xr[1] + 4), (xr[0] + 15, xr[1] + 14), 2)
        pygame.draw.line(s, WHITE, (xr[0] + 15, xr[1] + 4), (xr[0] + 5, xr[1] + 14), 2)
        pygame.draw.circle(s, (230, 60, 50) if k != 'gold' else GOLD, (x + 26, y + 52), 12)
        g.text_at(s, '!' if k != 'gold' else '$', x + 26, y + 52, 15, WHITE)
        para(g, s, w['msg'], x + 46, y + 38, 15, BLACK, ww - 58)
        pygame.draw.rect(s, (210, 208, 195), (x + ww // 2 - 30, y + hh - 28, 60, 18))
        pygame.draw.rect(s, (90, 90, 90), (x + ww // 2 - 30, y + hh - 28, 60, 18), 2)
        g.text_at(s, 'OK', x + ww // 2, y + hh - 19, 15, BLACK)

    def draw_front(self, s):
        g = self.g
        if self.t < self.BOOT:
            s.fill(BLACK)
            for i, c in enumerate(((240, 70, 40), (80, 200, 60), (50, 120, 240), (255, 200, 40))):
                pygame.draw.rect(s, c, (W // 2 - 70 + i % 2 * 74, 150 + i // 2 * 74, 66, 66))
            g.text_at(s, 'PONGDOWS XP', W // 2, 340, 46, WHITE)
            for k in range(3):
                pygame.draw.rect(s, (60, 120, 255), (W // 2 - 70 + (int(g.t * 10) + k * 2) % 14 * 10, 420, 16, 16))
            pygame.draw.rect(s, (110, 110, 110), (W // 2 - 80, 410, 160, 36), 2)
            return
        for i, c in enumerate(((50, 110, 225), (70, 130, 235), (100, 160, 245), (130, 185, 250))):
            pygame.draw.rect(s, c, (0, i * 95, W, 96))
        for cxx, cyy, ww in ((150, 90, 90), (520, 60, 120), (680, 170, 80)):
            xx = (cxx + g.t * 8) % (W + 200) - 100
            pygame.draw.ellipse(s, WHITE, (xx, cyy, ww, ww // 3))
            pygame.draw.ellipse(s, WHITE, (xx + ww // 4, cyy - ww // 6, ww // 2, ww // 3))
        pygame.draw.polygon(s, (70, 170, 50), [(0, H - 70), (0, 380), (220, 330), (480, 360), (800, 300), (800, H - 70)])
        pygame.draw.polygon(s, (100, 200, 60), [(0, H - 70), (0, 450), (300, 400), (600, 430), (800, 390), (800, H - 70)])
        icons = (('MY PC', (180, 190, 210)), ('RECYCLE', (120, 200, 120)), ('PONG.EXE', (255, 255, 255)), ('VIRUS?', (230, 70, 70)), ('HOMEWORK', (240, 230, 150)))
        for i, (nm, c) in enumerate(icons):
            ix, iy = (24, 26 + i * 84)
            pygame.draw.rect(s, c, (ix + 8, iy, 40, 36))
            pygame.draw.rect(s, BLACK, (ix + 8, iy, 40, 36), 2)
            g.text_at(s, nm, ix + 28 - len(nm) * 6, iy + 46, 15, WHITE, center=False)
        pygame.draw.rect(s, (36, 92, 220), (0, H - 70, W, 40))
        pygame.draw.rect(s, (80, 140, 255), (0, H - 70, W, 3))
        pygame.draw.rect(s, (60, 165, 60), (0, H - 70, 124, 40))
        g.text_at(s, 'START', 62, H - 50, 22, WHITE)
        g.text_at(s, '12:%02d PM' % min(59, int(g.t) % 60), W - 70, H - 50, 15, WHITE)
        pygame.draw.lines(s, (230, 230, 240), False, [(W - 100, H - 196), (W - 100, H - 140), (W - 86, H - 128), (W - 72, H - 140), (W - 72, H - 188), (W - 86, H - 198), (W - 86, H - 160)], 6)
        pygame.draw.rect(s, WHITE, (W - 106, H - 194, 8, 8))
        pygame.draw.rect(s, WHITE, (W - 90, H - 194, 8, 8))
        pygame.draw.rect(s, BLACK, (W - 103, H - 191, 4, 4))
        pygame.draw.rect(s, BLACK, (W - 87, H - 191, 4, 4))
        for w in self.wins:
            self.draw_window(s, w)
        bubble(g, s, XP_CLIPPY[int(g.t / 3) % len(XP_CLIPPY)], W - 330, H - 252, W - 100, H - 200)
        g.text_at(s, 'P1 CLOSED: %d' % self.closed[0], 130, 12, 15, (255, 255, 255))
        g.text_at(s, '%s CLOSED: %d' % (g.who(1), self.closed[1]), W - 150, 12, 15, (255, 255, 255))
        for i, (c, col) in enumerate(zip(self.cur, ((120, 230, 255), (255, 130, 220)))):
            xp_cursor(s, c[0], c[1], col, 'P%d' % (i + 1), self.clk[i] > 0)
            g.text_at(s, 'P1' if i == 0 else g.who(1), c[0] + 24, c[1] + 34, 15, col)
        if self.t < 6.0:
            self.hint(s, H - 128)
