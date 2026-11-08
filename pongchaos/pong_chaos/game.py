from __future__ import annotations
import math
import random
from collections import deque
import pygame
from .core import *
from .audio import Sfx
from .entities import Ball, Paddle, Particles
from .events import EVENTS, MOOD

class Game:

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        pygame.display.set_caption('PONG: CHAOS EDITION')
        try:
            self.screen = pygame.display.set_mode((W, H), pygame.SCALED | pygame.RESIZABLE)
        except Exception:
            self.screen = pygame.display.set_mode((W, H))
        self.canvas = pygame.Surface((W, H))
        self.clock = pygame.time.Clock()
        print('Synthesizing sounds... (a couple of seconds)')
        self.sfx = Sfx()
        self.fonts = {}
        self.txt_cache = {}
        self.sprite_cache = {}
        self.parts = Particles()
        self.popups = []
        self.state = 'menu'
        self.menu_idx = 0
        self.mode = 1
        self.diff = 1
        self.chaos = 1
        self.t = 0.0
        self.shake_amt = 0.0
        self.flash_a = 0.0
        self.flash_col = WHITE
        self.banner = None
        self.demo = Ball(self, 200, 200, 330, 240)
        self.scan = None
        self.fac = {}
        self.balls = []
        self.events = []
        self.recent = deque(maxlen=14)
        self.hist = deque(maxlen=240)
        self.scores = [0, 0]
        self.paddles = [Paddle(-1, 'p1'), Paddle(1, 'ai')]
        self.bsize_cur = 1.0
        self.ball_hidden = False
        self.sdt = 0.0
        self.bdt = 0.0
        self.timer = 0.0
        self.next_event = 3.0
        self.winner = None
        self.last_scorer = 0
        self.count_i = 3
        self.pause_prev = 'play'
        self.music_until = 0.0
        self.queue = []
        self.sfx.start_music()

    def make_scanlines(self):
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        for y in range(0, H, 3):
            pygame.draw.line(s, (0, 0, 0, 55), (0, y), (W, y))
        for i in range(14):
            a = int(80 * (1 - i / 14.0) ** 2)
            pygame.draw.rect(s, (0, 0, 0, a), (i, i, W - 2 * i, H - 2 * i), 1)
        return s

    def render(self, text, size, color):
        color = atari(color)
        key = (text, size, color)
        s = self.txt_cache.get(key)
        if s is None:
            if len(self.txt_cache) > 700:
                self.txt_cache.clear()
            px = text_px(size)
            adv = 6 * px
            lines = wrap_text(str(text).upper(), max(8, (W - 32) // adv))
            wpx = max((len(l_) for l_ in lines)) * adv - px
            hpx = len(lines) * 9 * px - 2 * px
            s = pygame.Surface((max(px, wpx), max(px, hpx)), pygame.SRCALPHA)
            for li, l_ in enumerate(lines):
                x = (wpx - (len(l_) * adv - px)) // 2
                y = li * 9 * px
                for ch in l_:
                    pat = _F.get(ch, _F['?'])
                    for i, c in enumerate(pat):
                        if c == '1':
                            _raw_rect(s, color, (x + i % 5 * px, y + i // 5 * px, px, px))
                    x += adv
            self.txt_cache[key] = s
        return s

    def text_at(self, surf, text, x, y, size=20, color=WHITE, center=True, shadow=False):
        s = self.render(text, size, color)
        r = s.get_rect()
        if center:
            surf.blit(s, (_sn(x - r.w // 2), _sn(y - r.h // 2)))
        else:
            surf.blit(s, (_sn(x), _sn(y)))

    def alpha_rect(self, surf, rect, color, alpha):
        x, y, w, h = rect
        if alpha >= 160:
            pygame.draw.rect(surf, color, (x, y, w, h))
            return
        for yy in range(int(y), int(y + h), 4):
            pygame.draw.rect(surf, color, (x, yy, w, 2))

    def sprite(self, bitmap, px, color):
        key = (id(bitmap), px, color)
        s = self.sprite_cache.get(key)
        if s is None:
            s = pygame.Surface((len(bitmap[0]) * px, len(bitmap) * px), pygame.SRCALPHA)
            col = atari(color)
            for j, row in enumerate(bitmap):
                for i, c in enumerate(row):
                    if c == '1':
                        _raw_rect(s, col, (i * px, j * px, px, px))
            self.sprite_cache[key] = s
        return s

    def play(self, name, vol=1.0):
        self.sfx.play(name, vol)

    def shake(self, a):
        pass

    def flash(self, col, a=120):
        self.flash_col = col
        self.flash_a = max(self.flash_a, a)

    def popup(self, x, y, text, color=WHITE, size=26):
        self.popups.append([x, y, text, color, 1.1, 1.1, size])

    def fg(self):
        return hsv(self.t * 0.7) if self.fhas('disco') else WHITE

    def disp_scores(self):
        for ev in self.events:
            f = getattr(ev, 'fake_scores', None)
            if f:
                return f
        return self.scores

    def fset(self, key, owner, val=1.0):
        self.fac.setdefault(key, {})[owner] = val

    def fget(self, key):
        r = 1.0
        for v in self.fac.get(key, {}).values():
            r *= v
        return r

    def fhas(self, key):
        return bool(self.fac.get(key))

    def release(self, owner):
        for d in self.fac.values():
            d.pop(owner, None)
        for p in self.paddles:
            p.unmod(owner)

    def paddle(self, side):
        return self.paddles[0 if side < 0 else 1]

    def who(self, side):
        if side < 0:
            return 'PLAYER 1'
        return 'CPU' if self.mode == 1 else 'PLAYER 2'

    def real_balls(self):
        return [b for b in self.balls if b.alive and (not b.fake)]

    def restore_ball(self):
        self.balls = []
        a = random.uniform(-0.5, 0.5)
        d = random.choice((-1, 1))
        self.balls.append(Ball(self, W / 2, H / 2, d * math.cos(a) * BASE_SPEED, math.sin(a) * BASE_SPEED))
        self.hist.clear()
        self.next_event = 4.0
        if self.state == 'play':
            self.state = 'count'
            self.timer = 2.0
            self.count_i = 3

    def add_ball(self, x, y, vx, vy, fake=False):
        if len(self.balls) >= 10:
            return None
        b = Ball(self, x, y, vx, vy, fake)
        self.balls.append(b)
        return b

    def clone_ball(self, src, fake=False, spread=0.9):
        a = math.atan2(src.vy, src.vx) + random.uniform(-spread, spread)
        if random.random() < 0.5:
            a = math.pi - a
        sp = max(src.speed(), BASE_SPEED * 0.9)
        b = self.add_ball(src.x, src.y, math.cos(a) * sp, math.sin(a) * sp, fake)
        if b:
            b.last_hit = src.last_hit
            self.parts.burst(b.x, b.y, WHITE, 8, 150, 0.4)
        return b

    def steer(self, b, dvy):
        sp = b.speed()
        if sp < 1:
            return
        vy = clamp(b.vy + dvy, -sp * 0.88, sp * 0.88)
        b.vy = vy
        b.vx = sign(b.vx) * math.sqrt(max(sp * sp - vy * vy, 1.0))

    def bounce_rect(self, b, r, kick=1.0):
        s = b.size / 2
        if not rect_hit((b.x - s, b.y - s, 2 * s, 2 * s), r):
            return False
        ol = b.x + s - r[0]
        orr = r[0] + r[2] - (b.x - s)
        ot = b.y + s - r[1]
        ob = r[1] + r[3] - (b.y - s)
        m = min(ol, orr, ot, ob)
        if m == ol:
            b.x -= ol
            b.vx = -abs(b.vx)
        elif m == orr:
            b.x += orr
            b.vx = abs(b.vx)
        elif m == ot:
            b.y -= ot
            b.vy = -abs(b.vy)
        else:
            b.y += ob
            b.vy = abs(b.vy)
        if kick != 1.0:
            b.set_speed(clamp(b.speed() * kick, 150, MAX_SPEED))
        return True

    def bounce_circle(self, b, cx, cy, r, kick=1.0):
        s = b.size / 2
        dx, dy = (b.x - cx, b.y - cy)
        d = math.hypot(dx, dy)
        if d >= r + s * 0.9:
            return False
        if d < 1e-06:
            dx, dy, d = (1.0, 0.0, 1.0)
        nx, ny = (dx / d, dy / d)
        b.x = cx + nx * (r + s * 0.9)
        b.y = cy + ny * (r + s * 0.9)
        dot = b.vx * nx + b.vy * ny
        if dot < 0:
            b.vx -= 2 * dot * nx
            b.vy -= 2 * dot * ny
        if kick != 1.0:
            b.set_speed(clamp(b.speed() * kick, 150, MAX_SPEED))
        return True

    def raw_dir(self, ctrl):
        k = pygame.key.get_pressed()
        up = dn = False
        if ctrl == 'p1':
            up = k[pygame.K_w]
            dn = k[pygame.K_s]
            if self.mode == 1:
                up = up or k[pygame.K_UP]
                dn = dn or k[pygame.K_DOWN]
        elif ctrl == 'p2':
            up = k[pygame.K_UP]
            dn = k[pygame.K_DOWN]
        return (1 if dn else 0) - (1 if up else 0)

    def ai_dir(self, p):
        side = p.side
        best, bd = (None, 1000000000.0)
        for b in self.balls:
            if b.alive and b.vx * side > 0 and (not b.captured):
                d = abs(p.x - b.x)
                if d < bd:
                    bd, best = (d, b)
        h = p.h
        if best is None:
            target = H / 2
        else:
            if self.t > p.ai_t:
                p.ai_t = self.t + 0.5
                spread = (55, 30, 10)[self.diff]
                p.ai_err = clamp(random.gauss(0, spread), -h * 0.45, h * 0.45)
            t = (p.x - best.x) / best.vx if abs(best.vx) > 1 else 0
            y = best.y + best.vy * t
            y = y % (2 * H)
            if y > H:
                y = 2 * H - y
            react = (0.5, 0.75, 1.0)[self.diff]
            if abs(p.x - best.x) > W * react + 80:
                y = H / 2
            target = y + p.ai_err
        diff = target - p.cy()
        if abs(diff) < 8:
            return 0.0
        return (1.0 if diff > 0 else -1.0) * (0.62, 0.85, 1.0)[self.diff]

    def paddle_dir(self, p):
        ctrl = p.controller
        if self.fhas('swap'):
            ctrl = self.paddles[1].controller if p.side < 0 else self.paddles[0].controller
        if p.has('auto'):
            ctrl = 'ai'
        d = self.ai_dir(p) if ctrl == 'ai' else float(self.raw_dir(ctrl))
        if p.has('invert'):
            d = -d
        return d

    def side_steer_dir(self, side):
        p = self.paddle(side)
        if p.controller == 'ai':
            opp = self.paddle(-side)
            return 1.0 if H - opp.cy() > H / 2 else -1.0
        return float(self.raw_dir(p.controller))

    def new_match(self):
        self.sfx.change_music('calm')
        self.scores = [0, 0]
        self.paddles = [Paddle(-1, 'p1'), Paddle(1, 'ai' if self.mode == 1 else 'p2')]
        self.recent.clear()
        self.queue = []
        self.fac = {}
        self.events = []
        self.parts.p = []
        self.popups = []
        self.banner = None
        self.winner = None
        self.serve(random.choice((-1, 1)) * -1)

    def serve(self, scorer):
        self.balls = []
        self.hist.clear()
        d = -scorer if scorer else random.choice((-1, 1))
        a = random.uniform(-0.5, 0.5)
        self.balls.append(Ball(self, W / 2, H / 2, d * math.cos(a) * BASE_SPEED, math.sin(a) * BASE_SPEED))
        self.state = 'count'
        self.timer = 2.7
        self.count_i = 3
        self.next_event = (3.0, 1.6, 0.8)[self.chaos]
        for p in self.paddles:
            p.y = clamp(p.y, 0, H - p.h)

    def end_all_events(self):
        for ev in self.events:
            try:
                ev.end()
            except Exception as e:
                print('event end error', ev.name, e)
            self.release(ev)
        self.events = []
        self.fac = {}
        for p in self.paddles:
            p.mods = []
            p.xoff = 0.0
        self.ball_hidden = False

    def goal_value(self, b=None):
        m = 1.0
        for ev in self.events:
            m *= ev.goal_mult(b)
        return int(m)

    def ball_out(self, b, scorer):
        b.alive = False
        if b.fake:
            self.parts.burst(clamp(b.x, 0, W), b.y, WHITE, 8, 150, 0.4)
            self.balls = [x for x in self.balls if x.alive]
            return
        pts = self.goal_value(b)
        self.scores[0 if scorer < 0 else 1] += pts
        px = 0 if scorer > 0 else W
        self.parts.burst(clamp(b.x, 0, W), b.y, WHITE, 40, 420, 0.9, 6)
        self.parts.burst(px, b.y, GOLD if pts > 1 else WHITE, 26, 300, 0.8, 5)
        self.play('score')
        self.shake(12)
        self.flash(WHITE, 70)
        if pts > 1:
            self.popup(W / 2, H / 2, '+%d!' % pts, GOLD, 56)
        self.balls = [x for x in self.balls if x.alive]
        if not self.real_balls():
            self.end_all_events()
            self.balls = []
            self.state = 'point'
            self.timer = 1.3
            self.last_scorer = scorer

    def wall_hit(self, b):
        self.play('wall', 0.7)
        self.parts.burst(b.x, b.y, (200, 200, 200), 5, 120, 0.3, 3)
        if self.fhas('rubber'):
            b.set_speed(min(MAX_SPEED * 0.9, b.speed() * 1.08))
            self.play('bump', 0.4)
        for ev in self.events:
            ev.on_wall(b)

    def paddle_hit(self, b, p, r):
        s = b.size / 2
        side = p.side
        if b.fake:
            b.alive = False
            self.play('pop', 0.6)
            self.parts.burst(b.x, b.y, (255, 255, 120), 14, 220, 0.5)
            self.popup(b.x, b.y - 20, 'FAKE!', (255, 255, 120), 20)
            return
        b.x = r[0] + r[2] + s if side < 0 else r[0] - s
        rel = clamp((b.y - (r[1] + r[3] / 2)) / (r[3] / 2 + 1e-06), -1, 1)
        sp = min(MAX_SPEED, b.speed() * 1.045 + 8)
        food = p.food()
        ang = rel * math.radians(55)
        if food == 'pizza':
            ang = random.uniform(-1, 1) * math.radians(62)
        b.last_hit = side
        if food == 'burger' and b.cool <= 0 and (not b.stuck):
            b.stuck = p
            b.stick_t = 0.9
            b.stick_off = clamp(b.y - p.cy(), -p.h / 2, p.h / 2)
            b.stick_sp = sp
            b.vx = b.vy = 0
            self.play('eat')
            self.popup(b.x, b.y - 24, 'NOM!', (255, 200, 80), 22)
            self.parts.burst(b.x, b.y, (255, 190, 80), 12, 150, 0.5)
            return
        b.vx = -side * sp * math.cos(ang)
        b.vy = sp * math.sin(ang) + p.vy * 0.12
        self.play('hit')
        self.shake(3)
        self.parts.burst(b.x, b.y, (255, 255, 255), 10, 200, 0.4, 4)
        if food == 'pizza':
            self.parts.burst(b.x, b.y, (255, 120, 40), 8, 160, 0.5)
        for ev in list(self.events):
            ev.on_hit(b, p)

    def update_balls(self, bdt):
        if bdt <= 0:
            return
        for _ in range(2):
            h = bdt / 2
            for b in self.balls[:]:
                if not b.alive or b.captured:
                    continue
                s = b.size / 2
                b.cool -= h
                if b.stuck:
                    p = b.stuck
                    b.stick_t -= h
                    b.y = clamp(p.cy() + b.stick_off, s, H - s)
                    b.x = p.x + p.xoff + p.w + s if p.side < 0 else p.x + p.xoff - s
                    if b.stick_t <= 0:
                        rel = clamp(b.stick_off / (p.h / 2 + 1e-06), -1, 1)
                        ang = rel * math.radians(55) + random.uniform(-0.2, 0.2)
                        b.vx = -p.side * b.stick_sp * 1.12 * math.cos(ang)
                        b.vy = b.stick_sp * 1.12 * math.sin(ang)
                        b.stuck = None
                        b.cool = 0.35
                        self.play('pop')
                        self.parts.burst(b.x, b.y, (255, 200, 80), 10, 200, 0.5)
                    continue
                b.x += b.vx * h
                b.y += b.vy * h
                if self.fhas('wrap'):
                    if b.y < -s:
                        b.y = H + s
                        self.play('whoosh', 0.4)
                    elif b.y > H + s:
                        b.y = -s
                        self.play('whoosh', 0.4)
                elif b.y < s:
                    b.y = s
                    b.vy = abs(b.vy)
                    self.wall_hit(b)
                elif b.y > H - s:
                    b.y = H - s
                    b.vy = -abs(b.vy)
                    self.wall_hit(b)
                brect = (b.x - s, b.y - s, 2 * s, 2 * s)
                for p in self.paddles:
                    if b.vx * p.side <= 0:
                        continue
                    hit = None
                    for r in p.rects():
                        if rect_hit(brect, r):
                            hit = r
                            break
                    if hit:
                        self.paddle_hit(b, p, hit)
                        break
        self.balls = [b for b in self.balls if b.alive]

    def check_goals(self):
        for b in self.balls[:]:
            if b.captured or b.stuck:
                continue
            m = b.size + 10
            if b.x < -m:
                self.ball_out(b, +1)
            elif b.x > W + m:
                self.ball_out(b, -1)
            if self.state != 'play':
                break

    def pick_event(self):
        groups = {e.group for e in self.events if e.group}
        active = {type(e) for e in self.events}
        pool = [c for c in EVENTS if c not in self.recent and c not in active and c.ok(self) and (c.group is None or c.group not in groups)]
        if not pool:
            pool = [c for c in EVENTS if c not in active and c.ok(self)]
        if not pool:
            return None
        return random.choices(pool, [c.weight for c in pool])[0]

    def start_event(self, cls=None):
        if cls is None:
            cls = self.pick_event()
        if cls is None:
            return
        if getattr(cls, 'is_mode', False):
            if self.fhas('takeover') or not self.real_balls():
                return
            self.end_all_events()
        elif self.fhas('takeover'):
            return
        ev = cls(self)
        ev.dur = min(ev.dur, ev.cap)
        ev.start()
        self.recent.append(cls)
        self.sfx.change_music(MOOD.get(ev.name) or random.choice(('good', 'evil')))
        self.music_until = self.t + 5.0
        col = random.choice(BANNER_COLORS)
        self.banner = {'name': ev.name, 'sub': ev.sub, 't': 0.0, 'col': col}
        self.play(random.choice(('event', 'event2', 'event3')))
        self.flash(col, 55)
        self.shake(5)
        if ev.dur > 0 and (not ev.done):
            self.events.append(ev)
        else:
            try:
                ev.end()
            except Exception as e:
                print('event end error', e)
            self.release(ev)

    def update_events(self, dt):
        for ev in self.events[:]:
            ev.t += dt
            ev.update(dt)
            if ev.t >= ev.dur or ev.done:
                ev.end()
                self.release(ev)
                self.events.remove(ev)

    def update(self, dt):
        self.t += dt
        self.shake_amt *= 0.86
        if self.shake_amt < 0.3:
            self.shake_amt = 0
        self.flash_a = max(0, self.flash_a - 260 * dt)
        self.parts.update(dt)
        for q in self.popups:
            q[1] -= 34 * dt
            q[4] -= dt
        self.popups = [q for q in self.popups if q[4] > 0]
        if self.banner:
            self.banner['t'] += dt
        self.bsize_cur += (self.fget('bsize') - self.bsize_cur) * min(1.0, dt * 9)
        st = self.state
        if st == 'menu':
            self.update_demo(dt)
            return
        if st in ('pause',):
            return
        if st == 'over':
            if random.random() < 0.08:
                self.parts.burst(random.uniform(60, W - 60), random.uniform(60, 300), hsv(random.random()), 30, 300, 1.0, 6, 200)
                self.play('pop', 0.4)
            return
        ts = self.fget('ts')
        self.sdt = dt * ts
        self.bdt = self.sdt * self.fget('bts')
        for p in self.paddles:
            p.update(dt, self.paddle_dir(p))
        if st == 'count':
            self.timer -= dt
            i = int(math.ceil(self.timer / 0.9))
            if i != self.count_i and i >= 1:
                self.count_i = i
                self.play('count')
            if self.timer <= 0:
                self.state = 'play'
                self.play('go')
            return
        if st == 'point':
            self.timer -= dt
            if self.timer <= 0:
                if max(self.scores) >= WIN_SCORE:
                    self.state = 'over'
                    self.winner = 0 if self.scores[0] > self.scores[1] else 1
                    self.play('win')
                else:
                    self.serve(self.last_scorer)
            return
        if not self.fhas('rewind') and (not self.fhas('takeover')):
            self.hist.append([(b, b.x, b.y, b.vx, b.vy) for b in self.balls])
            self.update_balls(self.bdt)
        self.update_events(dt)
        if self.queue and self.state == 'play' and (not self.fhas('takeover')):
            self.start_event(self.queue.pop(0))
        if self.sfx.mood != 'calm' and (not self.events) and (self.t > self.music_until):
            self.sfx.change_music('calm')
        if not self.fhas('takeover'):
            self.check_goals()
        if self.state == 'play' and max(self.scores) >= WIN_SCORE:
            self.last_scorer = 1 if self.scores[1] > self.scores[0] else -1
            self.end_all_events()
            self.balls = []
            self.state = 'point'
            self.timer = 1.3
            self.play('score')
            return
        for b in self.balls:
            b.trail.append((b.x, b.y))
            if not b.stuck and (not b.captured) and (ts > 0.05):
                if abs(b.vx) < 110:
                    b.vx = 110 * sign(b.vx)
                sp = b.speed()
                if sp > MAX_SPEED:
                    b.set_speed(MAX_SPEED)
                elif sp < 150:
                    b.set_speed(BASE_SPEED * 0.8)
        self.next_event -= dt
        if self.next_event <= 0:
            lo, hi, k = ((2.5, 12.0, 1.5), (1.0, 10.0, 2.0), (0.4, 7.0, 3.0))[self.chaos]
            cap = (4, 6, 9)[self.chaos]
            if len(self.events) >= cap or self.fhas('takeover'):
                self.next_event = 0.8
            else:
                self.next_event = lo + (hi - lo) * random.random() ** k
                n = 1 + (random.random() < (0.2, 0.4, 0.65)[self.chaos]) + (random.random() < (0.0, 0.2, 0.4)[self.chaos])
                for _ in range(n):
                    self.start_event()
                if n > 1 and self.banner:
                    self.banner['name'] = ('', '', 'DOUBLE CHAOS!', 'TRIPLE CHAOS!')[n]

    def update_demo(self, dt):
        b = self.demo
        b.x += b.vx * dt
        b.y += b.vy * dt
        if b.y < 7 or b.y > H - 7:
            b.vy = -b.vy
            b.y = clamp(b.y, 7, H - 7)
            self.play('wall', 0.2)
        if b.x < 7 or b.x > W - 7:
            b.vx = -b.vx
            b.x = clamp(b.x, 7, W - 7)
            self.play('hit', 0.2)
            self.parts.burst(b.x, b.y, WHITE, 6, 120, 0.4)
        b.trail.append((b.x, b.y))

    def ball_color(self, b):
        if self.fhas('pac'):
            return (255, 230, 0)
        if self.fhas('gold'):
            return GOLD
        if self.fhas('fire'):
            return (255, 150, 30)
        if self.fhas('rainbow'):
            return hsv(self.t * 1.6)
        return self.fg()

    def draw_ball(self, surf, b):
        s = max(4, int(b.size))
        col = self.ball_color(b)
        if self.ball_hidden:
            return
        if self.fhas('pac'):
            r = max(8, int(s * 0.95))
            pygame.draw.circle(surf, col, (int(b.x), int(b.y)), r)
            ang = math.atan2(b.vy, b.vx)
            op = 0.08 + 0.55 * abs(math.sin(self.t * 14))
            pts = [(b.x, b.y)]
            for k in range(7):
                a = ang - op + 2 * op * k / 6
                pts.append((b.x + math.cos(a) * (r + 3), b.y + math.sin(a) * (r + 3)))
            pygame.draw.polygon(surf, BLACK, pts)
        else:
            pygame.draw.rect(surf, col, (int(b.x - s / 2), int(b.y - s / 2), s, s))
            if self.fhas('gold') and random.random() < 0.5:
                self.parts.burst(b.x, b.y, GOLD, 1, 70, 0.4, 3)

    def draw_paddle(self, surf, p):
        rects = p.rects()
        if p.has('ghost'):
            for r in rects:
                pygame.draw.rect(surf, (38, 38, 38), (int(r[0]), int(r[1]), int(r[2]), int(r[3])), 1)
            return
        col = self.fg()
        food = p.food()
        if food:
            self.draw_food(surf, p, rects, food)
        else:
            for r in rects:
                pygame.draw.rect(surf, col, (int(r[0]), int(r[1]), int(r[2]), int(r[3])))
        if p.has('frozen'):
            for r in rects:
                pygame.draw.rect(surf, (170, 235, 255), (int(r[0] - 3), int(r[1] - 3), int(r[2] + 6), int(r[3] + 6)), 2)
                for k in range(3):
                    yy = r[1] + (k + 0.5) * r[3] / 3
                    pygame.draw.line(surf, (220, 250, 255), (r[0] - 6, yy - 4), (r[0] + r[2] + 6, yy + 4), 1)
        if p.has('slip') and random.random() < 0.3:
            self.parts.burst(p.x + 7, p.cy() + random.uniform(-p.h / 2, p.h / 2), (200, 230, 255), 1, 60, 0.4, 3)

    def draw_food(self, surf, p, rects, food):
        y0 = min((r[1] for r in rects))
        y1 = max((r[1] + r[3] for r in rects))
        x = p.x + p.xoff
        pygame.draw.ellipse(surf, (236, 236, 236), (int(x - 7), int(y0 - 4), p.w + 14, int(y1 - y0 + 8)))
        pygame.draw.ellipse(surf, (200, 200, 205), (int(x - 4), int(y0 - 1), p.w + 8, int(y1 - y0 + 2)), 2)
        for r in rects:
            rx, ry, rw, rh = (int(r[0]), int(r[1]), int(r[2]), int(r[3]))
            if food == 'burger':
                layers = [((222, 160, 70), 4), ((60, 190, 60), 2), ((255, 210, 40), 1), ((110, 60, 30), 4), ((222, 160, 70), 3)]
                if p.side > 0:
                    layers.reverse()
                lx = rx
                for c, w_ in layers:
                    pygame.draw.rect(surf, c, (lx, ry, w_, rh), border_radius=2)
                    lx += w_
                pygame.draw.rect(surf, (255, 235, 200), (rx + (1 if p.side < 0 else 10), ry + 3, 2, 2))
            elif food == 'pizza':
                if p.side < 0:
                    pts = [(rx, ry), (rx, ry + rh), (rx + rw + 4, ry + rh / 2)]
                    crust = (rx, ry, 3, rh)
                else:
                    pts = [(rx + rw, ry), (rx + rw, ry + rh), (rx - 4, ry + rh / 2)]
                    crust = (rx + rw - 3, ry, 3, rh)
                pygame.draw.polygon(surf, (255, 200, 60), pts)
                pygame.draw.rect(surf, (205, 140, 60), crust)
                for k in range(max(1, int(rh // 28))):
                    pygame.draw.circle(surf, (210, 40, 40), (rx + rw // 2, int(ry + 12 + k * 26)), 3)
            else:
                pygame.draw.rect(surf, (230, 150, 90), (rx, ry, rw, rh), border_radius=6)
                pygame.draw.rect(surf, (255, 120, 180), (rx + 1, ry + 1, rw - 2, rh - 2), border_radius=6)
                for k in range(int(rh // 12)):
                    c = hsv(k * 0.23 + ry * 0.01)
                    pygame.draw.rect(surf, c, (rx + 3 + k * 5 % 7, int(ry + 4 + k * 12), 3, 2))
        if random.random() < 0.15:
            self.parts.burst(x + 7, random.uniform(y0, y1), (230, 230, 230), 1, 40, 0.8, 3, -40)

    def draw_world(self):
        c = self.canvas
        c.fill(BLACK)
        for ev in self.events:
            ev.draw_back(c)
        col = self.fg()
        if self.fhas('rubber'):
            pygame.draw.rect(c, (255, 60, 200), (0, 0, W, 10))
            pygame.draw.rect(c, (255, 60, 200), (0, H - 10, W, 10))
        elif not self.fhas('wrap'):
            pygame.draw.rect(c, tint(col, 0.8), (0, 0, W, 4))
            pygame.draw.rect(c, tint(col, 0.8), (0, H - 4, W, 4))
        else:
            for x in range(0, W, 24):
                pygame.draw.rect(c, (60, 60, 60), (x, 0, 12, 3))
                pygame.draw.rect(c, (60, 60, 60), (x, H - 3, 12, 3))
        for y in range(0, H, 28):
            pygame.draw.rect(c, tint(col, 0.6), (W // 2 - 2, y + 6, 4, 16))
        for p in self.paddles:
            self.draw_paddle(c, p)
        if self.state == 'menu':
            self.draw_ball(c, self.demo)
        elif self.state == 'count':
            if int(self.t * 6) % 2 == 0:
                for b in self.balls:
                    self.draw_ball(c, b)
        else:
            for b in self.balls:
                self.draw_ball(c, b)
        for ev in self.events:
            ev.draw_front(c)
        self.parts.draw(c)
        sc = self.disp_scores()
        draw_digits(c, str(sc[0]), W // 4, 22, 6, col)
        draw_digits(c, str(sc[1]), 3 * W // 4, 22, 6, col)
        gv = self.goal_value()
        if gv > 1 and self.state in ('play', 'count'):
            self.text_at(c, 'GOAL = %d POINTS' % gv, W // 2, 76, 20, GOLD, shadow=True)
        for q in self.popups:
            k = clamp(q[4] / q[5] * 2, 0, 1)
            self.text_at(c, q[2], q[0], q[1], q[6], tint(q[3], k), shadow=True)
        self.draw_banner(c)
        self.draw_chips(c)
        for ev in self.events:
            ev.draw_top(c)
        if self.state == 'count':
            n = max(1, int(math.ceil(self.timer / 0.9)))
            self.text_at(c, str(n) if self.timer > 0.05 else 'GO!', W // 2, H // 2 - 70, 90, WHITE, shadow=True)
            self.text_at(c, 'GET READY', W // 2, H // 2 + 110, 24, (200, 200, 200))

    def draw_banner(self, c):
        bn = self.banner
        if not bn:
            return
        t = bn['t']
        life = 2.7
        if t > life:
            self.banner = None
            return
        k = min(1.0, t / 0.2)
        y = int(-40 + (118 + 40) * (1 - (1 - k) ** 3))
        col = bn['col']
        if t > life - 0.5:
            col = tint(col, (life - t) / 0.5)
        flick = 1.0 if int(t * 18) % 2 == 0 or t > 0.4 else 0.4
        self.text_at(c, bn['name'], W // 2, y, 46, tint(col, flick), shadow=True)
        if bn['sub']:
            self.text_at(c, bn['sub'], W // 2, y + 34, 22, tint((230, 230, 230), 1.0 if t < life - 0.5 else (life - t) / 0.5), shadow=True)

    def draw_chips(self, c):
        y = H - 28
        for ev in reversed(self.events[-4:]):
            frac = clamp(1 - ev.t / ev.dur, 0, 1)
            self.text_at(c, ev.name, W // 2 - 10, y, 15, (190, 190, 190), center=False)
            w = self.render(ev.name, 15, (190, 190, 190)).get_width()
            pygame.draw.rect(c, (90, 90, 90), (W // 2 - 10 + w + 8, y + 4, 60, 6), 1)
            pygame.draw.rect(c, (220, 220, 220), (W // 2 - 10 + w + 9, y + 5, int(58 * frac), 4))
            y -= 24

    def apply_post(self, surf):
        for ev in self.events:
            surf = ev.post(surf)
        return surf

    def draw_menu(self):
        c = self.canvas
        c.fill(BLACK)
        for y in range(0, H, 28):
            pygame.draw.rect(c, (40, 40, 40), (W // 2 - 2, y + 6, 4, 16))
        self.draw_ball(c, self.demo)
        self.parts.draw(c)
        off = int(3 * math.sin(self.t * 3))
        self.text_at(c, 'PONG', W // 2, 130, 140, hsv(self.t * 0.25))
        if int(self.t * 2) % 2 == 0:
            self.text_at(c, '- CHAOS EDITION -', W // 2, 222, 30, (255, 230, 0))
        else:
            self.text_at(c, '- CHAOS EDITION -', W // 2, 222, 30, (255, 140, 0))
        items = ['START: %s' % ('1 PLAYER (vs CPU)' if self.mode == 1 else '2 PLAYERS'), 'CPU SKILL: %s' % ('EASY', 'NORMAL', 'HARD')[self.diff], 'CHAOS: %s' % ('CALM', 'NORMAL', 'INSANE')[self.chaos], 'QUIT']
        for i, it in enumerate(items):
            sel = i == self.menu_idx
            col = (255, 255, 255) if sel else (140, 140, 140)
            txt = ('> ' if sel else '  ') + it + (' <' if sel else '  ')
            self.text_at(c, txt, W // 2, 292 + i * 40, 30, col)
        self.text_at(c, 'UP/DOWN SELECT  LEFT/RIGHT CHANGE  ENTER GO', W // 2, 466, 18, (170, 170, 170))
        self.text_at(c, 'E = SUMMON CHAOS   M/N = MUSIC/SFX   X = CLOSE ADS', W // 2, 496, 18, (170, 170, 170))
        nm = sum((1 for e in EVENTS if e.is_mode))
        self.text_at(c, '%d CHAOS EVENTS + %d TAKEOVER GAMES - FIRST TO %d WINS' % (len(EVENTS) - nm, nm, WIN_SCORE), W // 2, 540, 20, (255, 230, 0))

    def render_frame(self):
        if self.state == 'menu':
            self.draw_menu()
            frame = self.canvas
        else:
            self.draw_world()
            frame = self.apply_post(self.canvas)
            c = frame
            if self.state == 'pause':
                self.alpha_rect(c, (0, 0, W, H), BLACK, 150)
                self.text_at(c, 'PAUSED', W // 2, H // 2 - 20, 80, WHITE, shadow=True)
                self.text_at(c, 'P / ESC resume    ENTER menu', W // 2, H // 2 + 40, 22, (200, 200, 200))
            if self.state == 'over':
                self.alpha_rect(c, (0, 150, W, 250), BLACK, 170)
                nm = self.who(-1 if self.winner == 0 else 1)
                self.text_at(c, '%s WINS!' % nm, W // 2, 215, 70, GOLD, shadow=True)
                self.text_at(c, '%d - %d' % (self.scores[0], self.scores[1]), W // 2, 285, 50, WHITE, shadow=True)
                self.text_at(c, 'ENTER rematch    ESC menu', W // 2, 350, 24, (210, 210, 210))
        if self.flash_a > 1:
            th = 16 if self.flash_a > 60 else 8
            for r_ in ((0, 0, W, th), (0, H - th, W, th), (0, 0, th, H), (W - th, 0, th, H)):
                pygame.draw.rect(frame, self.flash_col, r_)
        small = pygame.transform.scale(frame, (W // 2, H // 2))
        pygame.transform.scale(small, (W, H), self.screen)
        pygame.display.flip()

    def on_key(self, key):
        grab = self.state not in ('menu', 'over', 'pause') and any((getattr(e, 'grabs_keys', False) for e in self.events))
        if key == pygame.K_F11:
            try:
                pygame.display.toggle_fullscreen()
            except Exception:
                pass
        elif key == pygame.K_m and (not grab):
            self.sfx.toggle_music()
        elif key == pygame.K_n and (not grab):
            self.sfx.sfx_on = not self.sfx.sfx_on
        if self.state == 'menu':
            if key in (pygame.K_UP, pygame.K_w):
                self.menu_idx = (self.menu_idx - 1) % 4
                self.play('wall', 0.5)
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.menu_idx = (self.menu_idx + 1) % 4
                self.play('wall', 0.5)
            elif key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d):
                dlt = 1 if key in (pygame.K_RIGHT, pygame.K_d) else -1
                if self.menu_idx == 0:
                    self.mode = 3 - self.mode
                elif self.menu_idx == 1:
                    self.diff = (self.diff + dlt) % 3
                elif self.menu_idx == 2:
                    self.chaos = (self.chaos + dlt) % 3
                self.play('hit', 0.5)
            elif key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                if self.menu_idx == 3:
                    return False
                if self.menu_idx in (1, 2):
                    self._cycle()
                else:
                    self.play('go', 0.6)
                    self.new_match()
            elif key == pygame.K_ESCAPE:
                return False
        elif self.state == 'over':
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self.new_match()
            elif key == pygame.K_ESCAPE:
                self.state = 'menu'
                self.end_all_events()
        elif self.state == 'pause':
            if key in (pygame.K_p, pygame.K_ESCAPE):
                self.state = self.pause_prev
            elif key == pygame.K_RETURN:
                self.state = 'menu'
                self.end_all_events()
        else:
            if key in (pygame.K_p, pygame.K_ESCAPE):
                self.pause_prev = self.state
                self.state = 'pause'
            elif key == pygame.K_e and self.state == 'play' and (not grab):
                self.start_event()
            for ev in list(self.events):
                ev.on_key(key)
        return None

    def _cycle(self):
        if self.menu_idx == 1:
            self.diff = (self.diff + 1) % 3
        elif self.menu_idx == 2:
            self.chaos = (self.chaos + 1) % 3
        self.play('hit', 0.5)
        return True

    def run(self):
        running = True
        while running:
            dt = min(self.clock.tick(FPS) / 1000.0, 1 / 30.0)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.KEYDOWN:
                    if self.on_key(e.key) is False:
                        running = False
            self.update(dt)
            self.render_frame()
        pygame.quit()
