from __future__ import annotations
import math
import random
import pygame
from ..core import *
from .base import *


@reg
class MarioObby(Mode):
    name = 'SUPER PONG BROS'
    sub = 'RACE TO THE FLAG! JUMP PITS, PIPES AND GOOMBAS'
    dur = 15
    limit = 12.5
    LH = 300
    GY = 240
    LEN = 2000
    hint1 = 'A/D OR ARROWS RUN    W / UP / SPACE JUMP'
    hint2 = 'P1: A D W    P2: ARROWS    JUMP ON GOOMBAS!'

    def begin(self):
        GY, LEN = (self.GY, self.LEN)
        self.solids = []
        gaps = []
        self.edefs = []
        x = 420
        while x < LEN - 450:
            f = random.choice(('gap', 'gap', 'pipe', 'stairs', 'goomba', 'goomba', 'block'))
            if f == 'gap':
                w = random.randint(80, 120)
                gaps.append((x, x + w))
                x += w + random.randint(220, 300)
            elif f == 'pipe':
                h = random.choice((40, 60, 70))
                self.solids.append((x, GY - h, 40, h, 'p'))
                x += 40 + random.randint(220, 300)
            elif f == 'stairs':
                for i in range(3):
                    self.solids.append((x + i * 28, GY - (i + 1) * 24, 28, (i + 1) * 24, 's'))
                x += 84 + random.randint(240, 320)
            elif f == 'goomba':
                self.edefs.append((x, random.randint(50, 90)))
                x += random.randint(260, 340)
            else:
                self.solids.append((x, GY - 90, 60, 20, 'b'))
                x += 60 + random.randint(220, 300)
        self.gaps = gaps
        pos = 0
        for g0, g1 in gaps:
            self.solids.append((pos, GY, g0 - pos, 60, 'g'))
            pos = g1
        self.solids.append((pos, GY, LEN + 300 - pos, 60, 'g'))
        self.flag = LEN - 110
        self.resolved = False
        self.racers = []
        for side in (-1, 1):
            self.racers.append({'side': side, 'x': 60.0, 'y': float(GY), 'vx': 0.0, 'vy': 0.0, 'on': True, 'safe': 60.0, 'stun': 0.0, 'inv': 0.0, 'cam': 0.0, 'en': [{'x': float(cx), 'cx': cx, 'r': rg, 'd': 1, 'alive': True} for cx, rg in self.edefs]})

    def hit(self, r, s):
        return r['x'] - 8 < s[0] + s[2] and r['x'] + 8 > s[0] and (r['y'] - 16 < s[1] + s[3]) and (r['y'] > s[1])

    def ground_at(self, px):
        for s in self.solids:
            if s[4] == 'g' and s[0] <= px <= s[0] + s[2]:
                return True
        return False

    def lane_y(self, r):
        return 0 if r['side'] < 0 else self.LH

    def respawn(self, r):
        r['x'], r['y'], r['vy'], r['vx'] = (r['safe'], float(self.GY), 0.0, 0.0)
        r['stun'], r['inv'], r['on'] = (0.5, 1.4, True)
        self.g.play('uhoh', 0.6)
        self.g.parts.burst(r['x'] - r['cam'], self.lane_y(r) + r['y'], WHITE, 10, 160, 0.4)

    def ai(self, r):
        GY = self.GY
        J = False
        if r['on']:
            x = r['x']
            if r['y'] >= GY - 0.5 and (not self.ground_at(x + 34)):
                J = True
            for s in self.solids:
                if s[4] != 'g' and s[0] < x + 46 and (s[0] + s[2] > x + 12) and (s[1] < r['y'] - 2) and (s[1] + s[3] >= r['y'] - 4):
                    J = True
            for e in r['en']:
                if e['alive'] and 0 < e['x'] - x < 72:
                    J = True
        return (False, True, J)

    def step(self, r, dt, L, R, J, spd):
        r['vx'] = ((1 if R else 0) - (1 if L else 0)) * spd
        if J and r['on']:
            r['vy'] = -640.0
            r['on'] = False
            self.g.play('bump', 0.4)
        r['vy'] = min(900.0, r['vy'] + 1700 * dt)
        r['x'] = max(8.0, r['x'] + r['vx'] * dt)
        for s in self.solids:
            if self.hit(r, s):
                if r['x'] < s[0] + s[2] / 2:
                    r['x'] = s[0] - 8
                else:
                    r['x'] = s[0] + s[2] + 8
        r['y'] += r['vy'] * dt
        r['on'] = False
        for s in self.solids:
            if self.hit(r, s):
                if r['vy'] >= 0:
                    r['y'] = float(s[1])
                    r['vy'] = 0.0
                    r['on'] = True
                else:
                    r['y'] = float(s[1] + s[3] + 16)
                    r['vy'] = 0.0
        if r['y'] > self.LH + 60:
            self.respawn(r)
        if r['on'] and r['y'] >= self.GY - 0.5 and all((not a - 36 < r['x'] < b + 36 for a, b in self.gaps)):
            r['safe'] = r['x']

    def tick(self, dt):
        g = self.g
        GY = self.GY
        for r in self.racers:
            side = r['side']
            cpu = is_cpu(g, side)
            r['inv'] = max(0.0, r['inv'] - dt)
            spd = 210.0
            if r['stun'] > 0:
                r['stun'] -= dt
                L = R = J = False
            elif cpu:
                L, R, J = self.ai(r)
                spd *= (0.8, 0.9, 1.0)[g.diff]
            else:
                L, R, U, D, F = human_keys(g, side)
                J = U or F
            self.step(r, dt, L, R, J, spd)
            for e in r['en']:
                if not e['alive']:
                    continue
                e['x'] += 45 * e['d'] * dt
                if abs(e['x'] - e['cx']) > e['r']:
                    e['d'] = -e['d']
                if abs(r['x'] - e['x']) < 18 and r['y'] > GY - 16 and (r['y'] - 16 < GY):
                    if r['vy'] > 0 and r['y'] < GY - 6:
                        e['alive'] = False
                        r['vy'] = -420.0
                        g.play('pop')
                        g.popup(r['x'] - r['cam'], self.lane_y(r) + GY - 40, 'SPLAT', (255, 200, 80), 20)
                    elif r['inv'] <= 0:
                        self.respawn(r)
            r['cam'] = clamp(r['x'] - 260, 0, self.LEN + 300 - W)
            if r['x'] >= self.flag and (not self.resolved):
                self.resolved = True
                self.award(side, 2, '%s REACHES THE FLAG! +2' % g.who(side))
                self.end_soon(1.4)
                return

    def on_timeout(self):
        if self.resolved:
            return
        a, b = self.racers
        if abs(a['x'] - b['x']) > 20:
            lead = a if a['x'] > b['x'] else b
            self.award(lead['side'], 1, 'FARTHEST RUNNER +1')

    def draw_front(self, s):
        g = self.g
        GY = self.GY
        for i, r in enumerate(self.racers):
            oy = i * self.LH
            cam = r['cam']
            s.set_clip((0, oy, W, self.LH))
            pygame.draw.rect(s, (92, 148, 252), (0, oy, W, self.LH))
            for cxw in (120, 520, 980, 1500, 2000, 2500):
                sx = (cxw - cam * 0.5) % (W + 160) - 80
                pygame.draw.rect(s, WHITE, (sx, oy + 56, 64, 16))
                pygame.draw.rect(s, WHITE, (sx + 16, oy + 40, 32, 16))
            for sol in self.solids:
                sx = sol[0] - cam
                if sx + sol[2] < 0 or sx > W:
                    continue
                x, y, w, h, k = (sx, oy + sol[1], sol[2], sol[3], sol[4])
                if k == 'g':
                    pygame.draw.rect(s, (200, 76, 12), (x, y, w, h))
                    pygame.draw.rect(s, (80, 200, 40), (x, y, w, 8))
                    k0 = int(max(0, -x) // 40 * 40)
                    for kx in range(k0, int(min(w, W - x)) + 1, 40):
                        pygame.draw.rect(s, (120, 40, 8), (x + kx, y + 8, 4, h - 8))
                    pygame.draw.rect(s, (120, 40, 8), (x, y + 32, w, 4))
                elif k == 'p':
                    pygame.draw.rect(s, (0, 168, 0), (x, y, w, h))
                    pygame.draw.rect(s, (80, 255, 80), (x - 4, y, w + 8, 16))
                    pygame.draw.rect(s, (0, 80, 0), (x - 4, y, w + 8, 16), 4)
                elif k == 's':
                    pygame.draw.rect(s, (216, 120, 48), (x, y, w, h))
                    pygame.draw.rect(s, (96, 40, 8), (x, y, w, h), 4)
                else:
                    pygame.draw.rect(s, (240, 176, 48), (x, y, w, h))
                    pygame.draw.rect(s, (120, 60, 8), (x, y, w, h), 4)
            for e in r['en']:
                if not e['alive']:
                    continue
                ex = e['x'] - cam
                if -20 < ex < W + 20:
                    pygame.draw.rect(s, (160, 80, 16), (ex - 10, oy + GY - 16, 20, 12))
                    pygame.draw.rect(s, (80, 40, 8), (ex - 10, oy + GY - 4, 8, 4))
                    pygame.draw.rect(s, (80, 40, 8), (ex + 2, oy + GY - 4, 8, 4))
                    pygame.draw.rect(s, WHITE, (ex - 6, oy + GY - 12, 4, 4))
                    pygame.draw.rect(s, WHITE, (ex + 2, oy + GY - 12, 4, 4))
            fx = self.flag - cam
            if -60 < fx < W + 60:
                pygame.draw.rect(s, WHITE, (fx, oy + GY - 120, 4, 120))
                pygame.draw.polygon(s, (255, 40, 40), [(fx + 4, oy + GY - 120), (fx + 44, oy + GY - 104), (fx + 4, oy + GY - 88)])
                pygame.draw.rect(s, (60, 60, 60), (fx - 8, oy + GY - 8, 20, 8))
            if not (r['inv'] > 0 and int(self.t * 12) % 2 == 0):
                sx = r['x'] - cam
                top = oy + r['y'] - 16
                col = WHITE if r['side'] < 0 else GOLD
                pygame.draw.rect(s, col, (sx - 8, top + 4, 16, 12))
                pygame.draw.rect(s, (255, 40, 40), (sx - 8, top - 4, 16, 8))
                pygame.draw.rect(s, (255, 40, 40), (sx - 12, top + 2, 8, 4))
                pygame.draw.rect(s, BLACK, (sx + 2, top + 8, 4, 4))
            g.text_at(s, g.who(r['side']), 12, oy + 14, 15, WHITE, center=False)
        s.set_clip(None)
        pygame.draw.rect(s, WHITE, (0, self.LH - 2, W, 4))
        self.hint(s)

@reg
class Football(Mode):
    name = 'FOOTBALL MATCH'
    sub = 'KICK THE BALL INTO THE GOAL! FIRST TO 2'
    dur = 15
    limit = 12
    GOAL0 = 220
    GOAL1 = 380
    hint1 = 'WASD OR ARROWS: RUN INTO THE BALL TO KICK IT'
    hint2 = 'P1: WASD    P2: ARROWS    RUN INTO THE BALL TO KICK'

    def begin(self):
        self.gs = [0, 0]
        self.pl = []
        for side in (-1, 1):
            for kind in ('st', 'gk'):
                self.pl.append({'side': side, 'kind': kind, 'x': 0.0, 'y': 0.0, 'vx': 0.0, 'vy': 0.0, 'cd': 0.0})
        self.reset_pos()

    def reset_pos(self):
        for p in self.pl:
            s = p['side']
            if p['kind'] == 'st':
                p['x'], p['y'] = (W / 2 + s * 150.0, H / 2.0)
            else:
                p['x'], p['y'] = (70.0 if s < 0 else W - 70.0, H / 2.0)
            p['vx'] = p['vy'] = 0.0
        self.ball = [W / 2.0, H / 2.0, 0.0, 0.0]
        self.pause = 1.0

    def cpu_dir(self, p):
        bx, by = (self.ball[0], self.ball[1])
        goalx = 0 if p['side'] > 0 else W
        gx, gy = (goalx - bx, H / 2 - by)
        gd = math.hypot(gx, gy) or 1.0
        ux, uy = (gx / gd, gy / gd)
        rx, ry = (bx - p['x'], by - p['y'])
        rd = math.hypot(rx, ry) or 1.0
        if (rx * ux + ry * uy) / rd > 0.6 or rd < 28:
            tx, ty = (bx, by)
        else:
            tx, ty = (bx - ux * 34, by - uy * 34)
        dx, dy = (tx - p['x'], ty - p['y'])
        d = math.hypot(dx, dy)
        if d < 4:
            return (0.0, 0.0)
        return (dx / d, dy / d)

    def tick(self, dt):
        g = self.g
        if self.pause > 0:
            self.pause -= dt
        bx, by, bvx, bvy = self.ball
        for p in self.pl:
            p['cd'] -= dt
            if p['kind'] == 'gk':
                dy = clamp(by, self.GOAL0 + 14, self.GOAL1 - 14) - p['y']
                dx = 0.0
                dy = 0.0 if abs(dy) < 6 else sign(dy)
                spd = 170.0
            else:
                spd = 235.0
                if is_cpu(g, p['side']):
                    dx, dy = self.cpu_dir(p)
                    spd *= (0.7, 0.85, 0.97)[g.diff]
                else:
                    L, R, U, D, F = human_keys(g, p['side'])
                    dx = (1 if R else 0) - (1 if L else 0)
                    dy = (1 if D else 0) - (1 if U else 0)
                    if dx and dy:
                        dx *= 0.7071
                        dy *= 0.7071
            p['vx'], p['vy'] = (dx * spd, dy * spd)
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            if p['kind'] == 'gk':
                p['y'] = clamp(p['y'], self.GOAL0 + 14, self.GOAL1 - 14)
            else:
                p['x'] = clamp(p['x'], 54, W - 54)
                p['y'] = clamp(p['y'], 14, H - 14)
        if self.pause > 0:
            return
        f = max(0.0, 1 - 0.8 * dt)
        bvx *= f
        bvy *= f
        sp = math.hypot(bvx, bvy)
        if sp > 700:
            bvx, bvy = (bvx * 700 / sp, bvy * 700 / sp)
        bx += bvx * dt
        by += bvy * dt
        r = 7
        if by < r:
            by, bvy = (r, abs(bvy))
        if by > H - r:
            by, bvy = (H - r, -abs(bvy))
        opening = self.GOAL0 + 6 < by < self.GOAL1 - 6
        if not opening:
            if bx < 40 + r:
                bx, bvx = (40 + r, abs(bvx))
            if bx > W - 40 - r:
                bx, bvx = (W - 40 - r, -abs(bvx))
        else:
            if bx < 8:
                bx, bvx = (8, abs(bvx))
            if bx > W - 8:
                bx, bvx = (W - 8, -abs(bvx))
        for p in self.pl:
            d = math.hypot(bx - p['x'], by - p['y'])
            if d < 21 and p['cd'] <= 0:
                nx, ny = ((bx - p['x']) / max(d, 1.0), (by - p['y']) / max(d, 1.0))
                spd = 340 + 0.5 * math.hypot(p['vx'], p['vy'])
                bvx = nx * spd + p['vx'] * 0.5
                bvy = ny * spd + p['vy'] * 0.5
                bx, by = (p['x'] + nx * 22, p['y'] + ny * 22)
                p['cd'] = 0.12
                g.play('hit', 0.7)
                g.parts.burst(bx, by, WHITE, 6, 150, 0.3)
        self.ball = [bx, by, bvx, bvy]
        scorer = 0
        if bx < 26 and opening:
            scorer = 1
        elif bx > W - 26 and opening:
            scorer = -1
        if scorer:
            idx = 0 if scorer < 0 else 1
            self.gs[idx] += 1
            self.award(scorer, 1, 'GOAL!  %s +1' % g.who(scorer))
            g.play('score')
            g.parts.burst(bx, by, GOLD, 30, 360, 0.8, 6)
            self.reset_pos()
            if self.gs[idx] >= 2:
                self.end_soon(1.6)

    def draw_front(self, s):
        g = self.g
        for i in range(8):
            pygame.draw.rect(s, (24, 120, 24) if i % 2 else (40, 160, 40), (i * 100, 0, 100, H))
        pygame.draw.rect(s, WHITE, (40, 4, W - 80, H - 8), 4)
        pygame.draw.rect(s, WHITE, (W // 2 - 2, 4, 4, H - 8))
        pygame.draw.circle(s, WHITE, (W // 2, H // 2), 60, 4)
        for gx in (0, W - 40):
            pygame.draw.rect(s, (30, 30, 30), (gx, self.GOAL0, 40, self.GOAL1 - self.GOAL0))
            pygame.draw.rect(s, WHITE, (gx, self.GOAL0, 40, self.GOAL1 - self.GOAL0), 4)
        for p in self.pl:
            if p['kind'] == 'st':
                col = (255, 96, 48) if p['side'] < 0 else (64, 144, 255)
            else:
                col = (255, 224, 64) if p['side'] < 0 else (64, 255, 200)
            s.blit(g.sprite(MAN, 4, col), (int(p['x'] - 10), int(p['y'] - 14)))
        bx, by = (self.ball[0], self.ball[1])
        pygame.draw.rect(s, WHITE, (bx - 6, by - 6, 12, 12))
        g.text_at(s, '%d - %d' % (self.gs[0], self.gs[1]), W // 2, 24, 30, WHITE)
        self.hint(s)

@reg
class TankBattle(Mode):
    name = 'TANK BATTLE'
    sub = 'DESTROY THE ENEMY TANK! FIRST TO 2 KILLS'
    dur = 15
    limit = 12
    hint1 = 'A/D TURN   W/S DRIVE   SPACE FIRE (SHOTS RICOCHET)'
    hint2 = 'P1: A D W S SPACE    P2: ARROWS + ENTER'

    def mk(self, side):
        return {'side': side, 'x': 70.0 if side < 0 else W - 70.0, 'y': H / 2.0, 'a': 0.0 if side < 0 else math.pi, 'hp': 2, 'cd': 0.0, 'dead': 0.0, 'stk': 0.0, 'px': 0.0, 'py': 0.0, 'esc': 0.0, 'escd': 1}

    def begin(self):
        self.walls = []
        tries = 0
        while len(self.walls) < 5 and tries < 80:
            tries += 1
            w = random.choice((40, 80, 120))
            h = random.choice((40, 80, 120))
            x = random.randrange(180, 360, 20)
            y = random.randrange(40, H - 40 - h, 20)
            r = (x, y, w, h)
            if x + w > W // 2 - 20:
                continue
            if any((rect_hit((x - 40, y - 40, w + 80, h + 80), o) for o in self.walls)):
                continue
            self.walls.append(r)
        for x, y, w, h in list(self.walls):
            self.walls.append((W - x - w, y, w, h))
        self.walls.append((W // 2 - 20, H // 2 - 60, 40, 120))
        self.tanks = [self.mk(-1), self.mk(1)]
        self.bul = []
        self.kills = [0, 0]

    def in_wall(self, x, y):
        for w in self.walls:
            if w[0] - 2 < x < w[0] + w[2] + 2 and w[1] - 2 < y < w[1] + w[3] + 2:
                return True
        return False

    def free(self, t, x, y):
        if x < 16 or x > W - 16 or y < 16 or (y > H - 16):
            return False
        for w in self.walls:
            if circle_rect(x, y, 15, w):
                return False
        o = self.tanks[1] if t is self.tanks[0] else self.tanks[0]
        if o['dead'] <= 0 and math.hypot(x - o['x'], y - o['y']) < 30:
            return False
        return True

    def drive(self, t, d):
        nx = t['x'] + math.cos(t['a']) * d
        ny = t['y'] + math.sin(t['a']) * d
        if self.free(t, nx, t['y']):
            t['x'] = nx
        if self.free(t, t['x'], ny):
            t['y'] = ny

    def clear_line(self, a, b):
        for i in range(1, 14):
            k = i / 14.0
            if self.in_wall(a['x'] + (b['x'] - a['x']) * k, a['y'] + (b['y'] - a['y']) * k):
                return False
        return True

    def ai(self, t, dt):
        g = self.g
        e = self.tanks[0]
        if e['dead'] > 0:
            return (False, False, False, False, False)
        t['stk'] += dt
        if t['stk'] >= 0.5:
            moved = math.hypot(t['x'] - t['px'], t['y'] - t['py'])
            t['px'], t['py'], t['stk'] = (t['x'], t['y'], 0.0)
            if moved < 8 and t['esc'] <= 0:
                t['esc'] = 0.7
                t['escd'] = random.choice((-1, 1))
        if t['esc'] > 0:
            t['esc'] -= dt
            return (t['escd'] < 0, t['escd'] > 0, False, True, False)
        dx, dy = (e['x'] - t['x'], e['y'] - t['y'])
        d = math.hypot(dx, dy)
        diff = (math.atan2(dy, dx) - t['a'] + math.pi) % math.tau - math.pi
        L, R = (diff < -0.06, diff > 0.06)
        U = abs(diff) < 1.0 and d > 200
        D = d < 110 and abs(diff) < 0.6
        F = abs(diff) < 0.1 and self.clear_line(t, e) and (random.random() < (0.04, 0.07, 0.12)[g.diff])
        return (L, R, U, D, F)

    def hurt(self, t, q):
        g = self.g
        t['hp'] -= 1
        g.play('zap', 0.7)
        g.parts.burst(t['x'], t['y'], (255, 200, 60), 12, 240, 0.5)
        if t['hp'] <= 0:
            t['dead'] = 1.6
            g.play('boom', 0.8)
            g.parts.burst(t['x'], t['y'], (255, 120, 20), 40, 400, 0.9, 6)
            idx = 0 if q[5] < 0 else 1
            self.kills[idx] += 1
            self.award(q[5], 1, 'TANK DESTROYED! %s +1' % g.who(q[5]))
            if self.kills[idx] >= 2:
                self.end_soon(1.6)

    def tick(self, dt):
        g = self.g
        for t in self.tanks:
            if t['dead'] > 0:
                t['dead'] -= dt
                if t['dead'] <= 0:
                    n = self.mk(t['side'])
                    t.update(n)
                continue
            t['cd'] -= dt
            if is_cpu(g, t['side']):
                L, R, U, D, F = self.ai(t, dt)
            else:
                L, R, U, D, F = human_keys(g, t['side'])
            t['a'] += ((1 if R else 0) - (1 if L else 0)) * 2.7 * dt
            mv = (130 if U else 0) - (90 if D else 0)
            if mv:
                self.drive(t, mv * dt)
            if F and t['cd'] <= 0:
                t['cd'] = 0.55
                c, sn = (math.cos(t['a']), math.sin(t['a']))
                self.bul.append([t['x'] + c * 26, t['y'] + sn * 26, c * 430, sn * 430, 2.4, t['side'], 0])
                g.play('shoot', 0.6)
        for q in self.bul[:]:
            q[4] -= dt
            q[0] += q[2] * dt
            if self.in_wall(q[0], q[1]) or q[0] < 0 or q[0] > W:
                q[0] -= q[2] * dt
                q[2] = -q[2]
                q[6] += 1
                g.play('tick', 0.4)
            q[1] += q[3] * dt
            if self.in_wall(q[0], q[1]) or q[1] < 0 or q[1] > H:
                q[1] -= q[3] * dt
                q[3] = -q[3]
                q[6] += 1
                g.play('tick', 0.4)
            dead = q[4] <= 0 or q[6] > 4
            for t in self.tanks:
                if t['dead'] <= 0 and t['side'] != q[5] and (math.hypot(q[0] - t['x'], q[1] - t['y']) < 18):
                    dead = True
                    self.hurt(t, q)
                    break
            if dead and q in self.bul:
                self.bul.remove(q)

    def draw_tank(self, s, t):
        x, y, a = (t['x'], t['y'], t['a'])
        c, sn = (math.cos(a), math.sin(a))
        col = (255, 208, 32) if t['side'] < 0 else (72, 160, 255)

        def P(lx, ly):
            return (x + c * lx - sn * ly, y + sn * lx + c * ly)
        pygame.draw.polygon(s, tint(col, 0.5), [P(-18, -15), P(18, -15), P(18, 15), P(-18, 15)])
        pygame.draw.polygon(s, col, [P(-14, -9), P(14, -9), P(14, 9), P(-14, 9)])
        pygame.draw.line(s, col, (x, y), P(28, 0), 6)
        pygame.draw.circle(s, WHITE, (int(x), int(y)), 6)
        for i in range(t['hp']):
            pygame.draw.rect(s, WHITE, (x - 14 + i * 10, y - 30, 6, 4))

    def draw_front(self, s):
        g = self.g
        s.fill((24, 72, 24))
        pygame.draw.rect(s, (200, 200, 200), (0, 0, W, H), 8)
        for w in self.walls:
            pygame.draw.rect(s, (216, 144, 64), w)
            pygame.draw.rect(s, (120, 60, 16), w, 4)
        for t in self.tanks:
            if t['dead'] <= 0:
                self.draw_tank(s, t)
        for q in self.bul:
            pygame.draw.rect(s, WHITE, (q[0] - 4, q[1] - 4, 8, 8))
        g.text_at(s, '%d - %d' % (self.kills[0], self.kills[1]), W // 2, 24, 30, WHITE)
        self.hint(s)

@reg
class SnakeMode(Mode):
    name = 'SNAKE ARENA'
    sub = "EAT 4 APPLES BEFORE THE OTHER SNAKE! DON'T CRASH"
    dur = 15
    limit = 12
    GW = 20
    GH = 15
    hint1 = 'STEER WITH WASD OR ARROWS'
    hint2 = 'P1: WASD    P2: ARROWS'

    def mk(self, side):
        x = 3 if side < 0 else 16
        d = (1, 0) if side < 0 else (-1, 0)
        return {'side': side, 'body': [(x - d[0] * i, 7) for i in range(3)], 'dir': d, 'nd': d, 'ate': 0}

    def begin(self):
        self.sn = [self.mk(-1), self.mk(1)]
        self.step_t = 0.0
        self.apple = None
        self.spawn_apple()

    def spawn_apple(self):
        occ = set()
        for s in self.sn:
            occ.update(s['body'])
        free = [(x, y) for x in range(self.GW) for y in range(self.GH) if (x, y) not in occ]
        self.apple = random.choice(free) if free else None

    def cpu_dir(self, s):
        h, d = (s['body'][0], s['dir'])
        occ = set()
        for o in self.sn:
            occ.update(o['body'][:-1])
        ax, ay = self.apple if self.apple else (10, 7)
        best, bs = (d, 1000000000.0)
        for c in (d, (d[1], -d[0]), (-d[1], d[0])):
            n = (h[0] + c[0], h[1] + c[1])
            if not (0 <= n[0] < self.GW and 0 <= n[1] < self.GH) or n in occ:
                continue
            sc = abs(n[0] - ax) + abs(n[1] - ay) - (0.5 if c == d else 0)
            if sc < bs:
                best, bs = (c, sc)
        return best

    def advance(self):
        g = self.g
        for s in self.sn:
            if is_cpu(g, s['side']):
                s['nd'] = self.cpu_dir(s)
            s['dir'] = s['nd']
        heads = [(s['body'][0][0] + s['dir'][0], s['body'][0][1] + s['dir'][1]) for s in self.sn]
        crash = [False, False]
        for i in range(2):
            nh = heads[i]
            if not (0 <= nh[0] < self.GW and 0 <= nh[1] < self.GH):
                crash[i] = True
            for o in self.sn:
                if nh in o['body'][:-1]:
                    crash[i] = True
        if heads[0] == heads[1]:
            crash = [True, True]
        if crash[0] or crash[1]:
            g.play('boom', 0.7)
            for i in range(2):
                if crash[i]:
                    h = self.sn[i]['body'][0]
                    g.parts.burst(h[0] * 40 + 20, h[1] * 40 + 20, (255, 120, 20), 24, 300, 0.7, 6)
            if crash[0] and crash[1]:
                g.popup(W / 2, H / 2, 'DOUBLE CRASH!', WHITE, 30)
            else:
                self.award(self.sn[1 if crash[0] else 0]['side'], 1, 'CRASH! +1')
            self.end_soon(1.4)
            return
        for i, s in enumerate(self.sn):
            s['body'].insert(0, heads[i])
            if heads[i] == self.apple:
                s['ate'] += 1
                g.play('coin')
                self.spawn_apple()
                if s['ate'] >= 4:
                    self.award(s['side'], 2, '4 APPLES! %s +2' % g.who(s['side']))
                    self.end_soon(1.4)
                    return
            else:
                s['body'].pop()

    def on_timeout(self):
        a, b = self.sn
        if a['ate'] != b['ate']:
            self.award((a if a['ate'] > b['ate'] else b)['side'], 1, 'MOST APPLES +1')

    def tick(self, dt):
        g = self.g
        for s in self.sn:
            if is_cpu(g, s['side']):
                continue
            L, R, U, D, F = human_keys(g, s['side'])
            d = s['dir']
            if U and d != (0, 1):
                s['nd'] = (0, -1)
            elif D and d != (0, -1):
                s['nd'] = (0, 1)
            elif L and d != (1, 0):
                s['nd'] = (-1, 0)
            elif R and d != (-1, 0):
                s['nd'] = (1, 0)
        self.step_t += dt
        while self.step_t >= 0.11 and self.over_t is None:
            self.step_t -= 0.11
            self.advance()

    def draw_front(self, s):
        g = self.g
        s.fill(BLACK)
        pygame.draw.rect(s, (32, 64, 200), (0, 0, W, H), 4)
        if self.apple:
            ax, ay = self.apple
            pygame.draw.rect(s, (255, 40, 40), (ax * 40 + 8, ay * 40 + 12, 24, 24))
            pygame.draw.rect(s, (80, 255, 80), (ax * 40 + 16, ay * 40 + 4, 8, 8))
        for sn in self.sn:
            col = (80, 255, 80) if sn['side'] < 0 else (255, 80, 200)
            for i, (cx, cy) in enumerate(sn['body']):
                pygame.draw.rect(s, WHITE if i == 0 else col, (cx * 40 + 4, cy * 40 + 4, 32, 32))
            g.text_at(s, '%d/4' % sn['ate'], W // 4 if sn['side'] < 0 else 3 * W // 4, 92, 18, col)
        self.hint(s)
