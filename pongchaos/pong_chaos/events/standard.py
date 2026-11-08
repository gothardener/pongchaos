from __future__ import annotations
import math
import random
import pygame
from ..core import *
from .base import *


fevent('TURBO BALL', 'bts', 1.55, 8, 'HOLD ON TO YOUR PADDLES', 'time')
fevent('SLOW MOTION', 'ts', 0.45, 8, 'MATRIX TIME', 'time')
fevent('GIANT BALL', 'bsize', 2.7, 8, "IT'S HUGE", 'size')
fevent('TINY BALL', 'bsize', 0.55, 8, 'WHERE DID IT GO?', 'size')
fevent('WRAP-AROUND WALLS', 'wrap', 1, 9, 'THE WALLS ARE GONE', 'walls')
fevent('RUBBER WALLS', 'rubber', 1, 10, 'WALLS MAKE THE BALL FASTER', 'walls')
fevent('SWAPPED CONTROLS', 'swap', 1, 8, 'YOU CONTROL THE OTHER PADDLE', 'swap')

@reg
class DoublePoints(Event):
    name = 'DOUBLE POINTS'
    sub = 'GOALS COUNT TWICE'
    dur = 10
    group = 'score'

    def goal_mult(self, ball):
        return 2

    def start(self):
        self.g.flash(GOLD, 50)

@reg
class TripleTrouble(Event):
    name = 'TRIPLE TROUBLE'
    sub = 'GOALS COUNT THREE TIMES'
    dur = 8
    group = 'score'

    def goal_mult(self, ball):
        return 3

    def start(self):
        self.g.flash(GOLD, 60)

@reg
class ZaWarudo(Event):
    name = 'ZA WARUDO!'
    sub = 'TIME HAS STOPPED... MOVE YOUR PADDLE!'
    dur = 1.9
    group = 'time'

    def start(self):
        self.g.fset('ts', self, 0.0)
        self.g.play('timestop')
        self.g.flash(WHITE, 160)

@reg
class Rewind(Event):
    name = 'REWIND'
    sub = 'DEJA VU...'
    dur = 2.6
    group = 'time'

    @classmethod
    def ok(cls, g):
        return len(g.hist) > 100

    def start(self):
        self.g.fset('rewind', self)
        self.g.play('rewind')

    def update(self, dt):
        g = self.g
        for _ in range(2):
            if not g.hist:
                self.done = True
                return
            snap = g.hist.pop()
            for b, x, y, vx, vy in snap:
                if b.alive and b in g.balls and (not b.stuck):
                    b.x, b.y, b.vx, b.vy = (x, y, vx, vy)
        g.parts.burst(W / 2, random.uniform(0, H), (120, 200, 255), 2, 200, 0.4)

    def post(self, s):
        if int(self.t * 20) % 3 == 0:
            out = s.copy()
            for _ in range(4):
                y = random.randint(0, H - 20)
                out.blit(s, (random.randint(-25, 25), y), (0, y, W, random.randint(4, 14)))
            return out
        return s

@reg
class PulsingBall(Event):
    name = 'PULSING BALL'
    sub = 'BIG... small... BIG... small...'
    dur = 9
    group = 'size'

    def update(self, dt):
        self.g.fset('bsize', self, max(0.3, 1 + 0.95 * math.sin(self.t * 5)))

@reg
class InvisibleBall(Event):
    name = 'INVISIBLE BALL'
    sub = 'TRUST YOUR INSTINCTS'
    dur = 7

    def update(self, dt):
        self.g.ball_hidden = self.t % 1.1 > 0.18

    def end(self):
        self.g.ball_hidden = False

@reg
class Zigzag(Event):
    name = 'ZIGZAG BALL'
    dur = 8
    group = 'steer'

    def update(self, dt):
        g = self.g
        for b in g.real_balls():
            g.steer(b, 1500 * math.sin(self.t * 9) * g.bdt)

@reg
class DrunkBall(Event):
    name = 'DRUNK BALL'
    sub = 'IT HAD A FEW TOO MANY'
    dur = 8
    group = 'steer'

    def start(self):
        self.cd = 0

    def update(self, dt):
        g = self.g
        self.cd -= g.bdt
        if self.cd <= 0:
            self.cd = 0.17
            for b in g.real_balls():
                g.steer(b, random.uniform(-330, 330))

@reg
class Gravity(Event):
    name = 'GRAVITY!'
    sub = 'THE BALL FALLS DOWN'
    dur = 8
    group = 'grav'
    acc = 750

    def update(self, dt):
        for b in self.g.real_balls():
            b.vy = clamp(b.vy + self.acc * self.g.bdt, -750, 750)

    def draw_back(self, s):
        d = 1 if self.acc > 0 else -1
        for i in range(12):
            x = 40 + i * 64
            y = (self.t * 140 * d + i * 97) % H
            pygame.draw.polygon(s, (45, 45, 45), [(x - 6, y - 6 * d), (x + 6, y - 6 * d), (x, y + 6 * d)])

@reg
class AntiGravity(Gravity):
    name = 'ANTI-GRAVITY'
    sub = 'THE BALL FLOATS UP'
    acc = -750

@reg
class Hurricane(Event):
    name = 'HURRICANE'
    sub = 'THE WIND CHANGES DIRECTION!'
    dur = 9
    group = 'grav'

    def wind(self):
        return math.sin(self.t * 1.9)

    def update(self, dt):
        g = self.g
        for b in g.real_balls():
            g.steer(b, 900 * self.wind() * g.bdt)

    def draw_back(self, s):
        w = self.wind()
        for i in range(26):
            x = i * 53 % W
            y = (i * 211 + self.t * 520 * w) % H
            pygame.draw.line(s, (60, 60, 70), (x, y), (x, y + 26 * sign(w)), 2)

@reg
class BlackHole(Event):
    name = 'BLACK HOLE'
    sub = 'IT EATS THE BALL AND SPITS IT SOMEWHERE ELSE'
    dur = 10
    group = 'grav'

    def start(self):
        self.pos = (random.uniform(300, 500), random.uniform(160, 440))

    def update(self, dt):
        g = self.g
        cx, cy = self.pos
        for b in g.real_balls():
            if b.stuck or b.captured:
                continue
            dx, dy = (cx - b.x, cy - b.y)
            d = math.hypot(dx, dy) + 1
            a = 13000000.0 / (d * d + 10000)
            b.vx += dx / d * a * g.bdt
            b.vy += dy / d * a * g.bdt
            if d < 24:
                g.parts.burst(b.x, b.y, (170, 120, 255), 18, 260, 0.6)
                b.x, b.y = (random.uniform(120, W - 120), random.uniform(80, H - 80))
                ang = random.uniform(0, math.tau)
                sp = max(b.speed(), 380)
                b.vx, b.vy = (math.cos(ang) * sp, math.sin(ang) * sp)
                if abs(b.vx) < 150:
                    b.vx = 150 * sign(b.vx)
                g.parts.burst(b.x, b.y, (170, 120, 255), 18, 260, 0.6)
                g.play('whoosh')
                g.shake(5)

    def draw_front(self, s):
        cx, cy = (int(self.pos[0]), int(self.pos[1]))
        for i in range(6):
            r = int(66 - i * 9 + 4 * math.sin(self.t * 4 + i))
            pygame.draw.circle(s, tint((130, 70, 255), 0.35 + i * 0.12), (cx, cy), max(2, r), 2)
        for i in range(18):
            a = self.t * 3 + i * 0.45
            r = 74 - i * 3.6
            pygame.draw.rect(s, (200, 170, 255), (int(cx + math.cos(a) * r), int(cy + math.sin(a) * r * 0.8), 3, 3))
        pygame.draw.circle(s, BLACK, (cx, cy), 17)
        pygame.draw.circle(s, WHITE, (cx, cy), 17, 1)

@reg
class TeleportBall(Event):
    name = 'TELEPORTING BALL'
    dur = 8
    group = 'steer'

    def start(self):
        self.cd = 1.2

    def update(self, dt):
        g = self.g
        self.cd -= g.bdt
        if self.cd <= 0:
            self.cd = 1.3
            for b in g.real_balls():
                if b.stuck:
                    continue
                g.parts.burst(b.x, b.y, (0, 255, 255), 16, 240, 0.5)
                b.y = random.uniform(60, H - 60)
                g.parts.burst(b.x, b.y, (255, 0, 255), 16, 240, 0.5)
                g.play('pop')

@reg
class Mitosis(Event):
    name = 'MITOSIS'
    sub = 'EVERY HIT SPLITS THE BALL'
    dur = 10

    def on_hit(self, ball, paddle):
        g = self.g
        if len(g.balls) < 6 and (not ball.fake):
            g.clone_ball(ball, spread=0.45)
            g.play('pop')

@reg
class Fireball(Event):
    name = 'FIREBALL'
    sub = 'EVERY HIT MAKES IT FASTER'
    dur = 10

    def start(self):
        self.g.fset('fire', self)

    def on_hit(self, ball, paddle):
        ball.set_speed(min(MAX_SPEED * 0.9, ball.speed() * 1.12))

    def update(self, dt):
        for b in self.g.real_balls():
            self.g.parts.burst(b.x, b.y, random.choice(((255, 140, 20), (255, 60, 0), (255, 220, 60))), 2, 90, 0.5, 6, -60)

@reg
class GoldenBall(Event):
    name = 'GOLDEN BALL'
    sub = 'THE NEXT GOAL IS WORTH 3'
    dur = 12
    group = 'score'

    def start(self):
        self.g.fset('gold', self)
        self.g.flash(GOLD, 80)

    def goal_mult(self, ball):
        return 3

@reg
class MagnetPaddles(Event):
    name = 'MAGNET PADDLES'
    sub = 'THE BALL CURVES TOWARDS THE PADDLE'
    dur = 8
    group = 'steer'
    k = 1

    def update(self, dt):
        g = self.g
        for b in g.real_balls():
            p = g.paddle(1 if b.vx > 0 else -1)
            diff = p.cy() - b.y
            if abs(diff) > 12:
                g.steer(b, self.k * sign(diff) * 800 * g.bdt)

    def draw_back(self, s):
        for p in self.g.paddles:
            for i in range(3):
                r = int((self.t * 60 + i * 20) % 60)
                pygame.draw.circle(s, (50, 30, 70), (int(p.x + 7), int(p.cy())), r, 1)

@reg
class RepelPaddles(MagnetPaddles):
    name = 'REPEL PADDLES'
    sub = 'THE BALL FLEES FROM THE PADDLE'
    k = -1

@reg
class UTurn(Event):
    name = 'U-TURN!'
    sub = 'THE BALL CHANGES ITS MIND'
    dur = 0

    def start(self):
        g = self.g
        for b in g.real_balls():
            if not b.stuck:
                b.vx = -b.vx
                g.parts.burst(b.x, b.y, (255, 255, 0), 20, 250, 0.5)
        g.play('rewind')

@reg
class BallReset(Event):
    name = 'BALL TELEPORTS HOME'
    sub = 'BACK TO THE CENTER!'
    dur = 0

    def start(self):
        g = self.g
        for b in g.real_balls():
            if b.stuck:
                continue
            g.parts.burst(b.x, b.y, WHITE, 20, 250, 0.5)
            b.x, b.y = (W / 2, H / 2)
            a = random.uniform(-0.6, 0.6)
            d = random.choice((-1, 1))
            sp = max(BASE_SPEED, b.speed() * 0.8)
            b.vx, b.vy = (d * math.cos(a) * sp, math.sin(a) * sp)
            g.parts.burst(b.x, b.y, WHITE, 20, 250, 0.5)
        g.play('pop')

@reg
class Multiball(Event):
    name = 'MULTIBALL!'
    sub = 'TWO MORE BALLS'
    dur = 0

    def start(self):
        g = self.g
        rb = g.real_balls()
        if rb:
            for _ in range(2):
                g.clone_ball(rb[0])
        g.play('powerup')

@reg
class BallStorm(Event):
    name = 'BALL STORM!!!'
    sub = 'FIVE MORE BALLS. GOOD LUCK.'
    dur = 0

    def start(self):
        g = self.g
        rb = g.real_balls()
        if rb:
            for _ in range(5):
                g.clone_ball(rb[0], spread=1.2)
        g.play('powerup')
        g.shake(8)

@reg
class Decoys(Event):
    name = 'DECOY BALLS'
    sub = 'ONLY ONE IS REAL...'
    dur = 10

    def start(self):
        g = self.g
        rb = g.real_balls()
        if rb:
            for _ in range(4):
                g.clone_ball(rb[0], fake=True, spread=1.0)

    def end(self):
        g = self.g
        for b in g.balls:
            if b.fake:
                b.alive = False
                g.parts.burst(b.x, b.y, WHITE, 10, 160, 0.4)
        g.balls = [b for b in g.balls if b.alive]
pevent('SHRUNKEN PADDLE', 'h', 0.5, 9, 'one', '', 'psize')
pevent('GIANT PADDLE', 'h', 1.8, 9, 'one', '', 'psize')
pevent('MICRO PADDLES', 'h', 0.45, 8, 'both', 'TINY!', 'psize')
pevent('INVERTED CONTROLS', 'invert', 1, 8, 'one', 'UP IS DOWN')
pevent('ROCKET PADDLE', 'speed', 1.9, 8, 'one', 'ZOOM')
pevent('MUDDY PADDLE', 'speed', 0.38, 8, 'one', 'SO SLOW...')
pevent('ICE RINK', 'slip', 1, 9, 'both', 'SLIPPERY!')
pevent('SPLIT PADDLE', 'split', 1, 9, 'one', 'WITH A GAP IN THE MIDDLE', 'pshape')
pevent('CLONE PADDLES', 'clone', 1, 9, 'both', 'A MIRROR IMAGE APPEARS', 'pshape')
pevent('GHOST PADDLES', 'ghost', 1, 8, 'both', 'INVISIBLE!', 'pshape')
pevent('BURGER PADDLE', 'food', 'burger', 10, 'one', 'THE BALL STICKS TO THE BURGER', 'pshape')
pevent('PIZZA PADDLE', 'food', 'pizza', 10, 'one', 'THE BALL BOUNCES RANDOMLY', 'pshape')
pevent('DONUT PADDLE', 'food', 'donut', 10, 'one', 'THE BALL FITS THROUGH THE HOLE', 'pshape', extra=[('h', 1.35)])
pevent('AUTOPILOT', 'auto', 1, 5, 'both', 'HANDS OFF THE KEYBOARD', 'ctrl')
pevent('ICE AGE', 'frozen', 1, 2.4, 'one', 'FROZEN SOLID', 'ctrl')

@reg
class PaddleDrift(Event):
    name = 'DRIFTING PADDLES'
    sub = 'THE PADDLES WANDER'
    dur = 9

    def update(self, dt):
        for i, p in enumerate(self.g.paddles):
            p.xoff = (45 + 45 * math.sin(self.t * 1.7 + i * 2)) * -p.side

    def end(self):
        for p in self.g.paddles:
            p.xoff = 0

@reg
class Hiccups(Event):
    name = 'PADDLE HICCUPS'
    dur = 8

    def start(self):
        self.side = random.choice((-1, 1))
        self.sub = self.g.who(self.side)
        self.cd = 0.4

    def update(self, dt):
        g = self.g
        self.cd -= dt
        if self.cd <= 0:
            self.cd = random.uniform(0.3, 0.6)
            p = g.paddle(self.side)
            p.y = clamp(p.y + random.choice((-1, 1)) * random.uniform(40, 90), 0, H - p.h)
            g.play('beep')
            g.parts.burst(p.x + 7, p.cy(), (255, 255, 0), 8, 140, 0.3)

@reg
class PaddleTeleport(Event):
    name = 'PADDLE GLITCH'
    sub = 'PADDLES KEEP TELEPORTING'
    dur = 8

    def start(self):
        self.cd = 1.2

    def update(self, dt):
        g = self.g
        self.cd -= dt
        if self.cd <= 0:
            self.cd = 1.5
            for p in g.paddles:
                g.parts.burst(p.x + 7, p.cy(), (0, 255, 255), 14, 200, 0.4)
                p.y = random.uniform(0, H - p.h)
                g.parts.burst(p.x + 7, p.cy(), (255, 0, 255), 14, 200, 0.4)
            g.play('glitch')

@reg
class MindControl(Event):
    name = 'MIND CONTROL'
    dur = 7
    group = 'steer'

    def start(self):
        self.side = random.choice((-1, 1))
        self.sub = self.g.who(self.side) + ' STEERS THE BALL WITH THEIR KEYS!'
        self.g.play('ufo')

    def update(self, dt):
        g = self.g
        d = g.side_steer_dir(self.side)
        for b in g.real_balls():
            if not b.stuck:
                g.steer(b, d * 1500 * g.bdt)
                if random.random() < 0.4:
                    g.parts.burst(b.x, b.y, (190, 110, 255), 1, 90, 0.5, 4)

    def draw_front(self, s):
        g = self.g
        p = g.paddle(self.side)
        for b in g.real_balls():
            pts = []
            for i in range(9):
                k = i / 8.0
                x = p.x + 7 + (b.x - p.x - 7) * k
                y = p.cy() + (b.y - p.cy()) * k + math.sin(self.t * 14 + i) * 7 * math.sin(k * math.pi)
                pts.append((x, y))
            pygame.draw.lines(s, (190, 110, 255), False, pts, 2)
            pygame.draw.circle(s, (190, 110, 255), (int(b.x), int(b.y)), int(b.size * 1.2 + 4 * math.sin(self.t * 10)), 1)

@reg
class Lasers(Event):
    name = 'LASER BEAMS'
    sub = 'WATCH THE RED LINES!'
    dur = 10
    group = 'haz1'

    def start(self):
        self.beams = []
        self.cd = 0.3

    def update(self, dt):
        g = self.g
        s = g.sdt
        self.cd -= s
        if self.cd <= 0:
            self.cd = random.uniform(0.9, 1.5)
            if random.random() < 0.6:
                self.beams.append({'h': True, 'pos': random.uniform(40, H - 40), 't': 0.0, 'fired': False, 'hit': set()})
            else:
                self.beams.append({'h': False, 'pos': random.uniform(120, W - 120), 't': 0.0, 'fired': False, 'hit': set()})
            g.play('warn')
        for bm in self.beams[:]:
            bm['t'] += s
            if bm['t'] >= 0.95 and (not bm['fired']):
                bm['fired'] = True
                g.play('laser')
                g.shake(7)
            if bm['fired']:
                pos = bm['pos']
                for b in g.real_balls():
                    if id(b) in bm['hit']:
                        continue
                    near = abs(b.y - pos) < 9 + b.size / 2 if bm['h'] else abs(b.x - pos) < 9 + b.size / 2
                    if near:
                        bm['hit'].add(id(b))
                        if bm['h']:
                            b.vy = -b.vy
                        else:
                            b.vx = -b.vx
                        g.parts.burst(b.x, b.y, (255, 80, 80), 16, 300, 0.5)
                        g.play('zap')
                for p in g.paddles:
                    if id(p) in bm['hit']:
                        continue
                    for r in p.rects():
                        c = r[1] - 9 < pos < r[1] + r[3] + 9 if bm['h'] else r[0] - 9 < pos < r[0] + r[2] + 9
                        if c:
                            bm['hit'].add(id(p))
                            p.mod(None, 'frozen', 1, 1.2)
                            g.parts.burst(p.x + 7, p.cy(), (255, 80, 80), 20, 300, 0.6)
                            g.play('zap')
                            break
            if bm['t'] > 1.3:
                self.beams.remove(bm)

    def draw_front(self, s):
        for bm in self.beams:
            pos = int(bm['pos'])
            if not bm['fired']:
                if int(bm['t'] * 14) % 2 == 0:
                    for k in range(0, W if bm['h'] else H, 20):
                        if bm['h']:
                            pygame.draw.line(s, (255, 40, 40), (k, pos), (k + 10, pos), 2)
                        else:
                            pygame.draw.line(s, (255, 40, 40), (pos, k), (pos, k + 10), 2)
            else:
                f = 1 - (bm['t'] - 0.95) / 0.35
                th = max(2, int(18 * f))
                if bm['h']:
                    pygame.draw.rect(s, (255, 60, 60), (0, pos - th // 2, W, th))
                    pygame.draw.rect(s, WHITE, (0, pos - th // 4, W, max(1, th // 2)))
                else:
                    pygame.draw.rect(s, (255, 60, 60), (pos - th // 2, 0, th, H))
                    pygame.draw.rect(s, WHITE, (pos - th // 4, 0, max(1, th // 2), H))

@reg
class Bombs(Event):
    name = 'BOMBS AWAY'
    sub = 'THEY SHRINK PADDLES AND LAUNCH THE BALL'
    dur = 10
    group = 'haz1'

    def start(self):
        self.bombs = []
        self.cd = 0.4

    def update(self, dt):
        g = self.g
        s = g.sdt
        self.cd -= s
        if self.cd <= 0:
            self.cd = random.uniform(0.8, 1.3)
            self.bombs.append([random.uniform(150, W - 150), random.uniform(60, H - 60), 0.0])
        for bb in self.bombs[:]:
            bb[2] += s
            if int(bb[2] * 10) != int((bb[2] - s) * 10) and bb[2] > 0.8:
                g.play('tick', 0.5)
            if bb[2] >= 1.5:
                self.bombs.remove(bb)
                g.play('boom')
                g.shake(15)
                g.flash((255, 200, 100), 90)
                g.parts.burst(bb[0], bb[1], (255, 180, 40), 50, 480, 0.9, 7)
                g.parts.burst(bb[0], bb[1], (255, 255, 200), 25, 300, 0.6, 5)
                for b in g.real_balls():
                    dx, dy = (b.x - bb[0], b.y - bb[1])
                    d = math.hypot(dx, dy)
                    if d < 95 and (not b.stuck):
                        d = max(d, 1)
                        sp = max(b.speed(), 380) * 1.15
                        vx, vy = (dx / d * sp, dy / d * sp)
                        if abs(vx) < 160:
                            vx = 160 * sign(vx if vx else random.choice((-1, 1)))
                        b.vx, b.vy = (vx, vy)
                for p in g.paddles:
                    for r in p.rects():
                        if circle_rect(bb[0], bb[1], 95, r):
                            p.mod(None, 'h', 0.6, 3.5)
                            p.mod(None, 'frozen', 1, 0.5)
                            break

    def draw_front(self, s):
        for bb in self.bombs:
            x, y = (int(bb[0]), int(bb[1]))
            near = bb[2] > 0.8
            pygame.draw.circle(s, (60, 0, 0) if near else (30, 30, 30), (x, y), 95, 1)
            red = near and int(bb[2] * 12) % 2 == 0
            pygame.draw.circle(s, (255, 40, 40) if red else (40, 40, 40), (x, y), 12)
            pygame.draw.circle(s, WHITE, (x, y), 12, 1)
            pygame.draw.line(s, (200, 200, 200), (x + 4, y - 11), (x + 9, y - 18), 2)
            pygame.draw.rect(s, (255, 220, 40), (x + 8, y - 21, 4, 4))

@reg
class Meteors(Event):
    name = 'METEOR SHOWER'
    dur = 10
    group = 'haz2'

    def start(self):
        self.m = []
        self.cd = 0.2

    def update(self, dt):
        g = self.g
        s = g.sdt
        self.cd -= s
        if self.cd <= 0:
            self.cd = random.uniform(0.35, 0.7)
            self.m.append([random.uniform(0, W + 200), -30, random.uniform(-260, -120), random.uniform(330, 470), random.uniform(10, 17)])
        for q in self.m[:]:
            q[0] += q[2] * s
            q[1] += q[3] * s
            g.parts.burst(q[0], q[1], random.choice(((255, 140, 20), (255, 220, 80))), 1, 60, 0.4, 5)
            dead = q[1] > H + 40 or q[0] < -60
            for b in g.real_balls():
                if not b.stuck and math.hypot(b.x - q[0], b.y - q[1]) < q[4] + b.size / 2:
                    sp = max(b.speed(), 380)
                    a = math.atan2(b.y - q[1], b.x - q[0])
                    b.vx, b.vy = (math.cos(a) * sp, math.sin(a) * sp)
                    if abs(b.vx) < 160:
                        b.vx = 160 * sign(b.vx)
                    dead = True
            for p in g.paddles:
                for r in p.rects():
                    if circle_rect(q[0], q[1], q[4], r):
                        p.mod(None, 'h', 0.72, 3.0)
                        dead = True
            if dead and q in self.m:
                self.m.remove(q)
                if 0 < q[1] < H:
                    g.parts.burst(q[0], q[1], (255, 160, 40), 18, 280, 0.5, 5)
                    g.play('splat', 0.5)

    def draw_front(self, s):
        for q in self.m:
            x, y, r = (int(q[0]), int(q[1]), int(q[4]))
            pygame.draw.line(s, (255, 120, 20), (x, y), (x - q[2] * 0.12, y - q[3] * 0.12), max(2, r // 2))
            pygame.draw.circle(s, (150, 110, 80), (x, y), r)
            pygame.draw.circle(s, (220, 190, 150), (x, y), r, 2)

@reg
class Lightning(Event):
    name = 'LIGHTNING STORM'
    sub = 'STRIKES FREEZE PADDLES & SCRAMBLE THE BALL'
    dur = 10
    group = 'haz2'

    def start(self):
        self.k = []
        self.cd = 0.5

    def update(self, dt):
        g = self.g
        s = g.sdt
        self.cd -= s
        if self.cd <= 0:
            self.cd = random.uniform(0.9, 1.6)
            rb = g.real_balls()
            if rb and random.random() < 0.6:
                b = random.choice(rb)
                x, y = (clamp(b.x + b.vx * 0.5, 80, W - 80), clamp(b.y + b.vy * 0.5, 40, H - 40))
            else:
                x, y = (random.uniform(60, W - 60), random.uniform(60, H - 60))
            self.k.append([x, y, 0.0, False])
        for q in self.k[:]:
            q[2] += s
            if q[2] >= 0.8 and (not q[3]):
                q[3] = True
                g.play('thunder')
                g.flash(WHITE, 150)
                g.shake(12)
                g.parts.burst(q[0], q[1], (255, 255, 120), 30, 380, 0.6, 5)
                for b in g.real_balls():
                    if math.hypot(b.x - q[0], b.y - q[1]) < 60 and (not b.stuck):
                        a = random.uniform(0, math.tau)
                        sp = max(b.speed(), 380) * 1.1
                        b.vx, b.vy = (math.cos(a) * sp, math.sin(a) * sp)
                        if abs(b.vx) < 160:
                            b.vx = 160 * sign(b.vx)
                for p in g.paddles:
                    for r in p.rects():
                        if circle_rect(q[0], q[1], 60, r):
                            p.mod(None, 'frozen', 1, 1.2)
                            break
            if q[2] > 1.0:
                self.k.remove(q)

    def draw_front(self, s):
        for q in self.k:
            x, y = (int(q[0]), int(q[1]))
            if not q[3]:
                r = int(60 * (1 - q[2] / 0.8)) + 4
                pygame.draw.circle(s, (150, 150, 60), (x, y), 60, 1)
                pygame.draw.circle(s, (255, 255, 120), (x, y), max(2, r), 2)
            else:
                pts = [(x, 0)]
                cx = x
                for i in range(1, 8):
                    cx = x + random.randint(-26, 26) * (1 - i / 8.0)
                    pts.append((cx, y * i / 8.0))
                pts.append((x, y))
                pygame.draw.lines(s, (255, 255, 255), False, pts, 5)
                pygame.draw.lines(s, (150, 180, 255), False, pts, 2)

@reg
class Earthquake(Event):
    name = 'EARTHQUAKE'
    sub = 'EVERYTHING SHAKES'
    dur = 6

    def post(self, s):
        out = pygame.Surface((W, H))
        out.blit(s, (random.choice((-8, -4, 0, 4, 8)), random.choice((-8, -4, 0, 4, 8))))
        return out

    def start(self):
        self.cd = 0

    def update(self, dt):
        g = self.g
        g.shake(9)
        self.cd -= g.bdt
        if self.cd <= 0:
            self.cd = 0.14
            for b in g.real_balls():
                g.steer(b, random.uniform(-260, 260))
        for p in g.paddles:
            p.y = clamp(p.y + random.uniform(-3, 3), 0, H - p.h)
        if random.random() < 0.3:
            g.parts.burst(random.uniform(0, W), 0, (120, 120, 120), 1, 40, 0.8, 4, 300)

@reg
class Zombies(Event):
    name = 'ZOMBIE HORDE'
    sub = 'THEY WANT THE BALL...'
    dur = 12
    group = 'haz3'

    def start(self):
        self.z = []
        self.cd = 0.2
        self.n = 0
        self.g.play('zombie')

    def update(self, dt):
        g = self.g
        s = g.sdt
        self.cd -= s
        if self.cd <= 0 and self.n < 9:
            self.cd = 0.9
            self.n += 1
            edge = random.choice(('t', 'b', 'l', 'r'))
            if edge == 't':
                x, y = (random.uniform(100, W - 100), -20)
            elif edge == 'b':
                x, y = (random.uniform(100, W - 100), H + 20)
            elif edge == 'l':
                x, y = (90, random.uniform(40, H - 40))
            else:
                x, y = (W - 90, random.uniform(40, H - 40))
            self.z.append([x, y, random.uniform(75, 120), random.random() * 6])
            if self.n % 3 == 1:
                g.play('zombie', 0.6)
        rb = g.real_balls()
        for q in self.z[:]:
            if not rb:
                break
            tgt = min(rb, key=lambda b: math.hypot(b.x - q[0], b.y - q[1]))
            dx, dy = (tgt.x - q[0], tgt.y - q[1])
            d = math.hypot(dx, dy) + 1e-06
            q[0] += dx / d * q[2] * s
            q[1] += dy / d * q[2] * s
            q[3] += s * 8
            if d < 18 + tgt.size / 2 and (not tgt.stuck):
                self.z.remove(q)
                g.play('splat')
                g.parts.burst(q[0], q[1], (90, 200, 70), 26, 300, 0.7, 6)
                g.parts.burst(q[0], q[1], (190, 20, 20), 10, 220, 0.6, 4)
                tgt.set_speed(max(260, tgt.speed() * 0.78))
                g.steer(tgt, random.choice((-1, 1)) * random.uniform(200, 380))
                g.popup(q[0], q[1] - 20, 'CHOMP!', (120, 255, 90), 22)

    def end(self):
        g = self.g
        for q in self.z:
            g.parts.burst(q[0], q[1], (90, 200, 70), 12, 200, 0.6, 5)

    def draw_front(self, s):
        g = self.g
        rb = g.real_balls()
        for q in self.z:
            x, y = (int(q[0]), int(q[1]))
            tx, ty = (rb[0].x, rb[0].y) if rb else (W / 2, H / 2)
            a = math.atan2(ty - y, tx - x)
            leg = int(3 * math.sin(q[3]))
            pygame.draw.rect(s, (50, 50, 120), (x - 6, y + 6 + leg // 2, 5, 9))
            pygame.draw.rect(s, (50, 50, 120), (x + 1, y + 6 - leg // 2, 5, 9))
            pygame.draw.rect(s, (70, 150, 70), (x - 8, y - 8, 16, 16))
            for sd in (-1, 1):
                ax, ay = (x + math.cos(a) * 16, y + math.sin(a) * 16 + sd * 5)
                pygame.draw.line(s, (100, 190, 100), (x, y + sd * 5), (ax, ay), 4)
            pygame.draw.rect(s, (110, 200, 110), (x - 6, y - 17, 12, 11))
            pygame.draw.rect(s, (255, 30, 30), (x - 4, y - 14, 3, 3))
            pygame.draw.rect(s, (255, 30, 30), (x + 1, y - 14, 3, 3))

@reg
class Minefield(Event):
    name = 'MINEFIELD'
    sub = "DON'T TOUCH THE BLINKING ONES"
    dur = 14
    group = 'world'

    def start(self):
        self.mines = [[random.uniform(130, W - 130), random.uniform(50, H - 50)] for _ in range(7)]

    def update(self, dt):
        g = self.g
        for m in self.mines[:]:
            for b in g.real_balls():
                if math.hypot(b.x - m[0], b.y - m[1]) < 14 + b.size / 2:
                    self.mines.remove(m)
                    g.play('boom', 0.8)
                    g.shake(10)
                    g.parts.burst(m[0], m[1], (255, 160, 40), 40, 400, 0.8, 6)
                    a = math.atan2(b.y - m[1], b.x - m[0]) + random.uniform(-0.6, 0.6)
                    sp = max(b.speed(), 380) * 1.2
                    b.vx, b.vy = (math.cos(a) * sp, math.sin(a) * sp)
                    if abs(b.vx) < 160:
                        b.vx = 160 * sign(b.vx)
                    break

    def draw_front(self, s):
        for m in self.mines:
            x, y = (int(m[0]), int(m[1]))
            pygame.draw.circle(s, (70, 70, 70), (x, y), 12)
            pygame.draw.circle(s, (160, 160, 160), (x, y), 12, 2)
            for a in range(0, 360, 45):
                r = math.radians(a)
                pygame.draw.line(s, (160, 160, 160), (x + math.cos(r) * 11, y + math.sin(r) * 11), (x + math.cos(r) * 17, y + math.sin(r) * 17), 3)
            if int(self.t * 3 + m[0]) % 2 == 0:
                pygame.draw.circle(s, (255, 40, 40), (x, y), 4)

@reg
class UFO(Event):
    name = 'UFO ABDUCTION'
    sub = 'SOMETHING IS ABOVE THE FIELD...'
    dur = 16
    group = 'ufo'

    @classmethod
    def ok(cls, g):
        return bool(g.real_balls())

    def start(self):
        self.x = random.choice((-50, W + 50))
        self.y = 70.0
        self.st = 'in'
        self.tm = 0.0
        self.ball = None
        self.tx = 400
        self.g.play('ufo')

    def update(self, dt):
        g = self.g
        s = g.sdt
        self.tm += s
        if self.st == 'in':
            rb = [b for b in g.real_balls() if not b.stuck]
            if not rb:
                self.done = True
                return
            tgt = min(rb, key=lambda b: abs(b.x - self.x))
            dx = tgt.x - self.x
            self.x += clamp(dx, -330 * s, 330 * s)
            if abs(dx) < 28:
                self.ball = tgt
                tgt.captured = True
                self.st = 'beam'
                self.tm = 0.0
                g.play('ufo')
        elif self.st == 'beam':
            b = self.ball
            k = min(1.0, s * 7)
            b.x += (self.x - b.x) * k
            b.y += (self.y + 28 - b.y) * k
            if self.tm > 1.0:
                self.st = 'carry'
                self.tm = 0.0
                self.tx = random.uniform(200, W - 200)
        elif self.st == 'carry':
            b = self.ball
            self.x += clamp(self.tx - self.x, -300 * s, 300 * s)
            b.x, b.y = (self.x, self.y + 28)
            if abs(self.tx - self.x) < 4 or self.tm > 2.0:
                b.captured = False
                a = random.uniform(0.3, 1.2)
                sp = max(b.speed(), BASE_SPEED)
                b.vx = random.choice((-1, 1)) * math.cos(a) * sp
                b.vy = math.sin(a) * sp
                b.stuck = None
                g.parts.burst(b.x, b.y, (120, 255, 160), 20, 260, 0.6)
                g.play('whoosh')
                self.st = 'out'
        else:
            self.y -= 220 * s
            if self.y < -60:
                self.done = True

    def end(self):
        if self.ball:
            self.ball.captured = False

    def draw_front(self, s):
        x, y = (int(self.x), int(self.y))
        if self.st in ('beam', 'carry'):
            for i in range(0, 520, 5):
                w = 6 + i // 8
                col = (40, 120, 70) if i // 5 % 2 else (90, 220, 130)
                pygame.draw.line(s, col, (x - w, y + 16 + i * 0.08), (x + w, y + 16 + i * 0.08), 1)
        pygame.draw.ellipse(s, (160, 220, 255), (x - 14, y - 22, 28, 28))
        pygame.draw.ellipse(s, (150, 150, 170), (x - 34, y - 8, 68, 24))
        pygame.draw.ellipse(s, (220, 220, 235), (x - 34, y - 8, 68, 24), 2)
        for i in range(5):
            c = (255, 255, 80) if (int(self.g.t * 6) + i) % 2 else (255, 80, 80)
            pygame.draw.circle(s, c, (x - 24 + i * 12, y + 5), 3)

@reg
class Shootout(Event):
    name = 'SHOOTOUT'
    sub = 'PADDLES FIRE LASERS - HIT THE OTHER PADDLE!'
    dur = 10
    group = 'haz3'

    def start(self):
        self.bul = []
        self.cd = [0.1, 0.5]

    def update(self, dt):
        g = self.g
        s = g.sdt
        for i, p in enumerate(g.paddles):
            self.cd[i] -= s
            if self.cd[i] <= 0 and (not p.has('frozen')):
                self.cd[i] = 0.7
                r = random.choice(p.rects())
                self.bul.append([p.x + p.xoff + (p.w if p.side < 0 else 0), r[1] + r[3] / 2, -p.side * 560.0, p.side])
                g.play('shoot', 0.5)
        for q in self.bul[:]:
            q[0] += q[2] * s
            dead = q[0] < -20 or q[0] > W + 20
            brect = (q[0] - 7, q[1] - 2, 14, 4)
            for b in g.real_balls():
                if not b.stuck and rect_hit(brect, (b.x - b.size / 2, b.y - b.size / 2, b.size, b.size)):
                    b.vx = sign(q[2]) * max(abs(b.vx), 300) * 1.1
                    g.parts.burst(b.x, b.y, (255, 200, 60), 12, 220, 0.4)
                    dead = True
            opp = g.paddle(-q[3])
            for r in opp.rects():
                if rect_hit(brect, r):
                    opp.mod(None, 'frozen', 1, 0.7)
                    g.parts.burst(q[0], q[1], (255, 60, 60), 16, 260, 0.5)
                    g.play('zap', 0.6)
                    dead = True
                    break
            if dead:
                self.bul.remove(q)

    def draw_front(self, s):
        for q in self.bul:
            pygame.draw.rect(s, (255, 230, 80), (int(q[0] - 7), int(q[1] - 2), 14, 4))
            pygame.draw.rect(s, WHITE, (int(q[0] - 3), int(q[1] - 1), 6, 2))

@reg
class PacMan(Event):
    name = 'PAC-MAN TAKEOVER'
    sub = 'EAT THE DOTS! AVOID THE GHOSTS! POWER PELLETS FLIP THE TABLES'
    dur = 15
    group = 'world'

    def start(self):
        g = self.g
        g.fset('pac', self)
        self.dots = []
        for x in range(100, 701, 50):
            for y in (150, 300, 450):
                self.dots.append([x, y, 0])
        for x, y in ((50, 70), (750, 70), (50, 530), (750, 530)):
            self.dots.append([x, y, 1])
        cols = [(255, 0, 0), (255, 184, 255), (0, 255, 255), (255, 184, 82)]
        self.ghosts = [{'x': 340 + i * 40, 'y': 300.0, 'c': c, 'dead': 0.0, 'sp': 70 + i * 12} for i, c in enumerate(cols)]
        self.scared = 0.0
        self.eaten = 0
        self.total = len(self.dots)
        self.w = 0
        g.play('pacdeath', 0.6)

    def update(self, dt):
        g = self.g
        s = g.sdt
        self.scared = max(0.0, self.scared - s)
        rb = g.real_balls()
        for b in rb:
            for d in self.dots[:]:
                if math.hypot(b.x - d[0], b.y - d[1]) < (12 if d[2] == 0 else 16) + b.size / 2:
                    self.dots.remove(d)
                    self.eaten += 1
                    self.w ^= 1
                    g.play('waka1' if self.w else 'waka2', 0.5)
                    if d[2] == 1:
                        self.scared = 6.0
                        g.play('powerup')
                        g.flash((60, 60, 255), 60)
                        g.parts.burst(d[0], d[1], (255, 255, 255), 14, 220, 0.5)
                    else:
                        b.set_speed(min(MAX_SPEED * 0.8, b.speed() * 1.012))
        for gh in self.ghosts:
            if gh['dead'] > 0:
                gh['dead'] -= s
                continue
            if not rb:
                break
            tgt = min(rb, key=lambda b: math.hypot(b.x - gh['x'], b.y - gh['y']))
            dx, dy = (tgt.x - gh['x'], tgt.y - gh['y'])
            d = math.hypot(dx, dy) + 1e-06
            k = -0.8 if self.scared > 0 else 1.0
            gh['x'] = clamp(gh['x'] + dx / d * gh['sp'] * k * s, 20, W - 20)
            gh['y'] = clamp(gh['y'] + dy / d * gh['sp'] * k * s, 20, H - 20)
            for b in rb:
                if math.hypot(b.x - gh['x'], b.y - gh['y']) < 14 + b.size / 2 and (not b.stuck):
                    if self.scared > 0:
                        gh['dead'] = 5.0
                        g.play('eat')
                        g.popup(gh['x'], gh['y'], '200', (0, 255, 255), 26)
                        g.parts.burst(gh['x'], gh['y'], gh['c'], 20, 260, 0.6)
                        gh['x'], gh['y'] = (W / 2, H / 2)
                    else:
                        g.bounce_circle(b, gh['x'], gh['y'], 14, 1.03)
                        gh['x'] = clamp(gh['x'] - (b.x - gh['x']) * 0.4, 20, W - 20)
                        gh['y'] = clamp(gh['y'] - (b.y - gh['y']) * 0.4, 20, H - 20)
                        g.play('bump', 0.5)
        if not self.dots and rb:
            side = rb[0].last_hit or random.choice((-1, 1))
            g.scores[0 if side < 0 else 1] += 1
            g.popup(W / 2, H / 2, 'BOARD CLEARED! +1 FOR ' + g.who(side), (255, 230, 0), 30)
            g.play('powerup')
            self.done = True

    def draw_back(self, s):
        blue = (33, 33, 255)
        pygame.draw.rect(s, blue, (6, 6, W - 12, H - 12), 3, border_radius=12)
        pygame.draw.rect(s, tint(blue, 0.5), (12, 12, W - 24, H - 24), 1, border_radius=10)
        for d in self.dots:
            if d[2] == 0:
                pygame.draw.rect(s, (255, 184, 174), (int(d[0] - 2), int(d[1] - 2), 4, 4))
            elif int(self.g.t * 4) % 2 == 0:
                pygame.draw.circle(s, (255, 184, 174), (int(d[0]), int(d[1])), 8)

    def draw_front(self, s):
        for gh in self.ghosts:
            if gh['dead'] > 0:
                continue
            x, y = (int(gh['x']), int(gh['y']))
            scared = self.scared > 0
            col = (30, 30, 255) if scared else gh['c']
            if scared and self.scared < 1.5 and (int(self.g.t * 8) % 2 == 0):
                col = WHITE
            pygame.draw.circle(s, col, (x, y - 2), 12)
            pygame.draw.rect(s, col, (x - 12, y - 2, 24, 12))
            wob = int(self.g.t * 8) % 2
            for k in range(3):
                pygame.draw.polygon(s, BLACK, [(x - 12 + k * 8, y + 11), (x - 8 + k * 8, y + 6 + 2 * wob), (x - 4 + k * 8, y + 11)])
            if scared:
                pygame.draw.rect(s, WHITE, (x - 6, y - 5, 3, 3))
                pygame.draw.rect(s, WHITE, (x + 3, y - 5, 3, 3))
            else:
                for ex in (-5, 5):
                    pygame.draw.circle(s, WHITE, (x + ex, y - 4), 4)
                    pygame.draw.circle(s, (20, 20, 255), (x + ex + 1, y - 4), 2)

@reg
class SpaceInvaders(Event):
    name = 'SPACE INVADERS'
    sub = 'THE BALL IS YOUR CANNON'
    dur = 13
    group = 'world'

    def start(self):
        cols = [(255, 60, 60), (255, 160, 0), (60, 255, 60), (80, 160, 255)]
        self.inv = []
        for r in range(4):
            for c in range(7):
                self.inv.append([(c - 3) * 38.0, 150.0 + r * 36, cols[r]])
        self.g.play('event3')

    def pos(self, i):
        return (W / 2 + i[0] + 130 * math.sin(self.t * 0.9), i[1] + 8 * math.sin(self.t * 1.7) + self.t * 4)

    def update(self, dt):
        g = self.g
        for i in self.inv[:]:
            x, y = self.pos(i)
            r = (x - 11, y - 8, 22, 16)
            for b in g.real_balls():
                if g.bounce_rect(b, r, 1.03):
                    self.inv.remove(i)
                    g.play('zap', 0.6)
                    g.parts.burst(x, y, i[2], 18, 260, 0.6, 5)
                    break
        if not self.inv:
            g.popup(W / 2, H / 2, 'INVASION REPELLED!', (60, 255, 60), 36)
            self.done = True

    def draw_front(self, s):
        fr = int(self.t * 2) % 2
        for i in self.inv:
            x, y = self.pos(i)
            s.blit(self.g.sprite(INV2 if fr else INV1, 2, i[2]), (int(x - 11), int(y - 8)))

@reg
class BrickWall(Event):
    name = 'BREAKOUT!'
    sub = 'SMASH THE BRICKS'
    dur = 13
    group = 'world'

    def start(self):
        self.br = []
        for c in range(3):
            for r in range(12):
                self.br.append([368 + c * 29, 14 + r * 47, 26, 43, hsv(r / 12.0)])

    def update(self, dt):
        g = self.g
        for k in self.br[:]:
            for b in g.real_balls():
                if g.bounce_rect(b, (k[0], k[1], k[2], k[3]), 1.015):
                    self.br.remove(k)
                    g.play('pop', 0.6)
                    g.parts.burst(k[0] + 13, k[1] + 21, k[4], 12, 220, 0.5, 5)
                    break

    def draw_front(self, s):
        for k in self.br:
            pygame.draw.rect(s, k[4], (k[0], k[1], k[2], k[3]))
            pygame.draw.rect(s, tint(k[4], 0.5), (k[0], k[1], k[2], k[3]), 2)
            pygame.draw.rect(s, tint(k[4], 1.0), (k[0] + 3, k[1] + 3, k[2] - 12, 3))

@reg
class Bumpers(Event):
    name = 'PINBALL BUMPERS'
    sub = 'BOING!'
    dur = 13
    group = 'world'

    def start(self):
        self.b = []
        tries = 0
        while len(self.b) < 4 and tries < 100:
            tries += 1
            x, y = (random.uniform(230, 570), random.uniform(90, 510))
            if all((math.hypot(x - o[0], y - o[1]) > 110 for o in self.b)):
                self.b.append([x, y, 0.0])

    def update(self, dt):
        g = self.g
        for o in self.b:
            o[2] = max(0.0, o[2] - dt * 4)
            for b in g.real_balls():
                if g.bounce_circle(b, o[0], o[1], 26, 1.08):
                    b.set_speed(clamp(b.speed() + 40, 200, MAX_SPEED))
                    o[2] = 1.0
                    g.play('bump')
                    g.parts.burst(o[0], o[1], (255, 80, 120), 10, 220, 0.4)

    def draw_front(self, s):
        for o in self.b:
            r = int(26 + 6 * o[2])
            x, y = (int(o[0]), int(o[1]))
            pygame.draw.circle(s, (255, 50, 90), (x, y), r)
            pygame.draw.circle(s, WHITE, (x, y), r, 3)
            pygame.draw.circle(s, (255, 200, 210), (x, y), max(4, r // 2), 2)

@reg
class MovingBarrier(Event):
    name = 'THE MOVING WALL'
    dur = 11
    group = 'world'

    def rect(self):
        y = (H - 150) / 2 + (H - 150) / 2 * 0.9 * math.sin(self.t * 1.4)
        return (W / 2 - 11, y, 22, 150)

    def update(self, dt):
        g = self.g
        r = self.rect()
        for b in g.real_balls():
            if g.bounce_rect(b, r, 1.02):
                g.play('hit', 0.6)

    def draw_front(self, s):
        r = self.rect()
        pygame.draw.rect(s, WHITE, r)
        for k in range(0, 150, 20):
            pygame.draw.rect(s, (230, 60, 60), (r[0], r[1] + k, 22, 10))

@reg
class Pillars(Event):
    name = 'PILLARS'
    sub = 'WATCH YOUR ANGLES'
    dur = 12
    group = 'world'

    def start(self):
        self.r = []
        tries = 0
        while len(self.r) < 5 and tries < 200:
            tries += 1
            w, h = (26, random.uniform(60, 140))
            c = (random.uniform(210, 560), random.uniform(30, H - 30 - h), w, h)
            if all((not rect_hit((c[0] - 50, c[1] - 30, c[2] + 100, c[3] + 60), o) for o in self.r)):
                self.r.append(c)

    def update(self, dt):
        for r in self.r:
            for b in self.g.real_balls():
                if self.g.bounce_rect(b, r, 1.02):
                    self.g.play('hit', 0.5)

    def draw_front(self, s):
        for r in self.r:
            pygame.draw.rect(s, (110, 110, 120), r)
            pygame.draw.rect(s, WHITE, r, 2)
            for k in range(int(r[3] // 14)):
                pygame.draw.line(s, (80, 80, 90), (r[0] + 3, r[1] + 7 + k * 14), (r[0] + r[2] - 3, r[1] + 7 + k * 14))

@reg
class Asteroids(Event):
    name = 'ASTEROIDS'
    sub = 'VECTOR ROCKS DRIFT THROUGH THE COURT'
    dur = 13
    group = 'world'

    def start(self):
        self.rocks = []
        for r in (30, 22, 22, 16, 16):
            ang = random.uniform(0, math.tau)
            sp = random.uniform(35, 85)
            shape = [r * random.uniform(0.72, 1.2) for _ in range(11)]
            self.rocks.append({'x': random.uniform(230, 570), 'y': random.uniform(60, 540), 'vx': math.cos(ang) * sp, 'vy': math.sin(ang) * sp, 'r': r, 'a': 0.0, 'va': random.uniform(-1, 1), 'shape': shape})

    def update(self, dt):
        g = self.g
        s = g.sdt
        for k in self.rocks:
            k['x'] = (k['x'] + k['vx'] * s) % W
            k['y'] = (k['y'] + k['vy'] * s) % H
            k['a'] += k['va'] * s
            for b in g.real_balls():
                if g.bounce_circle(b, k['x'], k['y'], k['r'] * 0.92, 1.04):
                    g.play('bump', 0.5)
                    g.parts.burst(b.x, b.y, (200, 200, 200), 8, 180, 0.4)

    def draw_front(self, s):
        for k in self.rocks:
            n = len(k['shape'])
            pts = [(k['x'] + math.cos(k['a'] + i * math.tau / n) * k['shape'][i], k['y'] + math.sin(k['a'] + i * math.tau / n) * k['shape'][i]) for i in range(n)]
            pygame.draw.polygon(s, BLACK, pts)
            pygame.draw.polygon(s, WHITE, pts, 2)

@reg
class CoinRain(Event):
    name = 'COIN RAIN'
    sub = 'CATCH COINS WITH THE BALL - 3 COINS = 1 POINT'
    dur = 11
    group = 'pick'

    def start(self):
        self.coins = []
        self.cd = 0.1
        self.have = [0, 0]

    def update(self, dt):
        g = self.g
        s = g.sdt
        self.cd -= s
        if self.cd <= 0:
            self.cd = 0.33
            self.coins.append([random.uniform(100, W - 100), -10.0, random.uniform(0, 6)])
        for c in self.coins[:]:
            c[1] += 130 * s
            c[2] += s * 7
            got = False
            for b in g.real_balls():
                if math.hypot(b.x - c[0], b.y - c[1]) < 13 + b.size / 2:
                    got = True
                    side = b.last_hit or random.choice((-1, 1))
                    i = 0 if side < 0 else 1
                    self.have[i] += 1
                    g.play('coin', 0.6)
                    g.parts.burst(c[0], c[1], GOLD, 10, 200, 0.5)
                    if self.have[i] >= 3:
                        self.have[i] = 0
                        g.scores[i] += 1
                        g.popup(c[0], c[1] - 20, '+1 POINT!', GOLD, 30)
                        g.play('powerup')
                    else:
                        g.popup(c[0], c[1] - 20, '%d/3' % self.have[i], GOLD, 22)
                    break
            if got or c[1] > H + 20:
                self.coins.remove(c)

    def draw_front(self, s):
        for c in self.coins:
            w = max(2, int(abs(math.cos(c[2])) * 11))
            pygame.draw.ellipse(s, GOLD, (int(c[0] - w), int(c[1] - 11), 2 * w, 22))
            pygame.draw.ellipse(s, (255, 250, 160), (int(c[0] - w), int(c[1] - 11), 2 * w, 22), 2)

@reg
class MysteryBox(Event):
    name = 'MYSTERY BOXES'
    sub = 'HIT ONE TO GIVE THE LAST HITTER A POWER-UP'
    dur = 14
    group = 'pick'

    def start(self):
        self.box = [[random.uniform(250, 550), random.uniform(80, 520)] for _ in range(2)]

    def update(self, dt):
        g = self.g
        for bx in self.box[:]:
            for b in g.real_balls():
                if rect_hit((bx[0] - 14, bx[1] - 14, 28, 28), (b.x - b.size / 2, b.y - b.size / 2, b.size, b.size)):
                    self.box.remove(bx)
                    side = b.last_hit or random.choice((-1, 1))
                    p, o = (g.paddle(side), g.paddle(-side))
                    k = random.randint(0, 4)
                    msg = ('MEGA PADDLE!', 'SPEED BOOST!', 'FOE FROZEN!', 'FOE SHRUNK!', 'FREE POINT!')[k]
                    if k == 0:
                        p.mod(None, 'h', 1.8, 9)
                    elif k == 1:
                        p.mod(None, 'speed', 1.7, 9)
                    elif k == 2:
                        o.mod(None, 'frozen', 1, 1.8)
                    elif k == 3:
                        o.mod(None, 'h', 0.55, 7)
                    else:
                        g.scores[0 if side < 0 else 1] += 1
                    g.play('powerup')
                    g.popup(bx[0], bx[1] - 24, msg, (255, 255, 80), 28)
                    g.parts.burst(bx[0], bx[1], (255, 255, 80), 26, 300, 0.7, 5)
                    break

    def draw_front(self, s):
        for bx in self.box:
            y = int(bx[1] + 4 * math.sin(self.t * 4 + bx[0]))
            x = int(bx[0])
            pygame.draw.rect(s, (230, 160, 20), (x - 14, y - 14, 28, 28))
            pygame.draw.rect(s, WHITE, (x - 14, y - 14, 28, 28), 2)
            self.g.text_at(s, '?', x, y, 26, WHITE)

@reg
class UpsideDown(Event):
    name = 'UPSIDE DOWN'
    sub = 'THE WORLD FLIPPED'
    dur = 8
    group = 'post'

    def post(self, s):
        return pygame.transform.flip(s, False, True)

@reg
class MirrorWorld(Event):
    name = 'MIRROR WORLD'
    sub = 'LEFT IS RIGHT'
    dur = 8
    group = 'post'

    def post(self, s):
        return pygame.transform.flip(s, True, False)

@reg
class DrunkScreen(Event):
    name = 'DRUNK MODE'
    sub = 'WHOA...'
    dur = 9
    group = 'post'

    def post(self, s):
        out = pygame.Surface((W, H))
        for y in range(0, H, 4):
            dx = _sn(26 * math.sin(self.t * 2.2 + y * 0.03))
            out.blit(s, (dx, y), (0, y, W, 4))
        return out

@reg
class BassDrop(Event):
    name = 'BASS DROP'
    dur = 8
    group = 'post'

    def start(self):
        self.g.play('boom', 0.6)

    def post(self, s):
        ph = self.t * 2.2 % 1.0
        if ph > 0.2:
            return s
        out = pygame.Surface((W, H))
        out.blit(s, (0, 12))
        return out

@reg
class PotatoMode(Event):
    name = 'POTATO MODE'
    sub = 'LOW-RES CHAOS'
    dur = 8
    group = 'post'

    def post(self, s):
        small = pygame.transform.scale(s, (W // 6, H // 6))
        return pygame.transform.scale(small, (W, H))

@reg
class Negative(Event):
    name = 'NEGATIVE'
    sub = 'COLORS INVERTED'
    dur = 8
    group = 'post'

    def post(self, s):
        inv = pygame.Surface((W, H))
        inv.fill((255, 255, 255))
        inv.blit(s, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
        return inv

@reg
class Glitch(Event):
    name = 'CRT GLITCH'
    dur = 7
    group = 'post'

    def start(self):
        self.strips = []
        self.cd = 0
        self.g.play('glitch')

    def post(self, s):
        if self.t > self.cd:
            self.cd = self.t + 0.09
            self.strips = [(random.randint(0, H - 30), random.randint(6, 40), random.randint(-50, 50)) for _ in range(random.randint(3, 7))]
            if random.random() < 0.3:
                self.g.play('glitch', 0.3)
        out = s.copy()
        for y, h, dx in self.strips:
            out.blit(s, (dx, y), (0, y, W, h))
        return out

@reg
class Disco(Event):
    name = 'DISCO FEVER'
    sub = 'EVERYTHING IS RAINBOW'
    dur = 10
    group = 'disco'

    def start(self):
        self.g.fset('disco', self)

    def draw_back(self, s):
        for yy in range(0, H, 24):
            pygame.draw.rect(s, tint(hsv(self.t * 0.4 + yy / float(H)), 0.35), (0, yy, W, 12))

@reg
class LightsOut(Event):
    name = 'LIGHTS OUT'
    sub = 'SPOTLIGHTS ONLY'
    dur = 9
    group = 'post'

    def draw_front(self, s):
        g = self.g
        vis = []
        for b in g.balls:
            if not b.captured:
                vis.append((b.x, b.y, 110))
        for p in g.paddles:
            for r in p.rects():
                vis.append((r[0] + r[2] / 2, r[1] + r[3] / 2, 60 + r[3] / 2))
        for y in range(0, H, 4):
            segs = []
            for cx, cy, rr in vis:
                dy = abs(y + 2 - cy)
                if dy < rr:
                    dx = math.sqrt(rr * rr - dy * dy)
                    segs.append((cx - dx, cx + dx))
            segs.sort()
            x = 0
            for a, b2 in segs:
                if a > x:
                    pygame.draw.rect(s, BLACK, (x, y, a - x, 4))
                x = max(x, b2)
            if x < W:
                pygame.draw.rect(s, BLACK, (x, y, W - x, 4))

@reg
class ScoreSwap(Event):
    name = 'SCORE SWAP'
    sub = 'THE SCORES JUST TRADED PLACES'
    dur = 0

    @classmethod
    def ok(cls, g):
        return g.scores[0] != g.scores[1]

    def start(self):
        g = self.g
        g.scores.reverse()
        g.flash((255, 0, 255), 120)
        g.play('rewind')

@reg
class ComebackGift(Event):
    name = 'COMEBACK GIFT'
    sub = 'A POINT FOR THE UNDERDOG'
    dur = 0

    @classmethod
    def ok(cls, g):
        return g.scores[0] != g.scores[1] and min(g.scores) < WIN_SCORE - 2

    def start(self):
        g = self.g
        i = 0 if g.scores[0] < g.scores[1] else 1
        g.scores[i] += 1
        g.play('powerup')
        g.popup(W / 4 if i == 0 else 3 * W / 4, 110, '+1', (130, 255, 90), 40)
