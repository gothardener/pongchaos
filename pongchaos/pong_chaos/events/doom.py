from __future__ import annotations
import math
import random
import pygame
from ..core import *
from .base import *


DOOM_MAP = ['111111111111', '100000000001', '102200002201', '102000000201', '100000330001', '100000330001', '100000000001', '102000000201', '102200002201', '100000000001', '100000000001', '111111111111']
DOOM_COL = {'1': (210, 160, 110), '2': (225, 70, 55), '3': (70, 190, 100)}
DEMON = ['..h..........h..', '..hh........hh..', '...hrrrrrrrrh...', '..rrrrrrrrrrrr..', '.rrrrrwwwwrrrrr.', '.rrrrwwggwwrrrr.', '.rrrrwwggwwrrrr.', '.rrrrrwwwwrrrrr.', '.rrrrrrrrrrrrrr.', '.rrdrrrrrrrrdrr.', '..rrkkkkkkkkrr..', '..rrkwkwkwkwrr..', '...rrkkkkkkrr...', '....rrrrrrrr....', '.....d.dd.d.....', '....d..dd..d....']
DEMON_PAL = {'r': (205, 40, 40), 'd': (110, 10, 20), 'w': (240, 240, 240), 'g': (70, 255, 90), 'k': (24, 0, 8), 'h': (230, 200, 150)}

def _col_runs(rows, pal):
    cols = []
    for x in range(len(rows[0])):
        runs, y = ([], 0)
        while y < len(rows):
            ch = rows[y][x]
            if ch == '.':
                y += 1
                continue
            y0 = y
            while y < len(rows) and rows[y][x] == ch:
                y += 1
            runs.append((y0, y, pal[ch]))
        cols.append(runs)
    return cols
DEMON_RUNS = _col_runs(DEMON, DEMON_PAL)

def doom_cast(ox, oy, dx, dy):
    mx, my = (int(ox), int(oy))
    ddx = abs(1.0 / dx) if dx else 1e+30
    ddy = abs(1.0 / dy) if dy else 1e+30
    if dx < 0:
        sx, sdx = (-1, (ox - mx) * ddx)
    else:
        sx, sdx = (1, (mx + 1.0 - ox) * ddx)
    if dy < 0:
        sy, sdy = (-1, (oy - my) * ddy)
    else:
        sy, sdy = (1, (my + 1.0 - oy) * ddy)
    side = 0
    t = '1'
    for _ in range(40):
        if sdx < sdy:
            sdx += ddx
            mx += sx
            side = 0
        else:
            sdy += ddy
            my += sy
            side = 1
        if not (0 <= my < 12 and 0 <= mx < 12):
            break
        t = DOOM_MAP[my][mx]
        if t != '0':
            break
    dist = sdx - ddx if side == 0 else sdy - ddy
    wx = oy + dist * dy if side == 0 else ox + dist * dx
    return (max(dist, 0.001), side, wx - math.floor(wx), t)

def doom_free(x, y, r=0.28):
    for ox, oy in ((-r, -r), (r, -r), (-r, r), (r, r)):
        cx, cy = (int(x + ox), int(y + oy))
        if not (0 <= cx < 12 and 0 <= cy < 12) or DOOM_MAP[cy][cx] != '0':
            return False
    return True

@reg
class PongDoom(Mode):
    name = 'PONGDOOM'
    sub = 'THE CPU IS NOW A DEMON. SHOOT IT. DODGE THE BALLS.'
    dur = 25
    cap = 25
    limit = 22
    weight = 2.5
    hint1 = 'A / D TURN    W / S WALK    SPACE FIRE'
    hint2 = 'P2 (THE DEMON): ARROWS MOVE    ENTER = FIREBALL'
    VY, VH, N = (72, 448, 200)

    def begin(self):
        self.px, self.py, self.a = (1.5, 6.5, 0.0)
        self.mx, self.my = (10.5, 6.5)
        self.hp, self.mhp = (100.0, 90.0)
        self.cool = 0.0
        self.mcool = 1.6
        self.balls = []
        self.muzzle = 0.0
        self.hurt = 0.0
        self.pain = 0.0
        self.strafe, self.strafe_t = (1, 1.0)
        self.fp = [False, False]
        self.bob = 0.0
        self.dead = False

    def walk(self, x, y, dx, dy):
        if doom_free(x + dx, y):
            x += dx
        if doom_free(x, y + dy):
            y += dy
        return (x, y)

    def los(self):
        dx, dy = (self.px - self.mx, self.py - self.my)
        d = math.hypot(dx, dy) or 1.0
        return (doom_cast(self.mx, self.my, dx / d, dy / d)[0] > d - 0.1, d)

    def demon_fire(self, err=0.0):
        g = self.g
        dx, dy = (self.px - self.mx, self.py - self.my)
        a = math.atan2(dy, dx) + random.uniform(-err, err)
        self.balls.append([self.mx, self.my, math.cos(a) * 4.6, math.sin(a) * 4.6])
        g.play('fball', 0.8)

    def shoot(self):
        g = self.g
        self.cool = 0.38
        self.muzzle = 0.12
        g.play('shotgun', 0.9)
        clear, d = self.los()
        ang = math.atan2(self.my - self.py, self.mx - self.px) - self.a
        ang = (ang + math.pi) % math.tau - math.pi
        if clear and abs(ang) < math.atan2(0.55, d):
            self.mhp -= 18 + random.random() * 6
            self.hurt = 0.25
            g.play('zombie', 0.7)

    def tick(self, dt):
        g = self.g
        if self.dead:
            return
        self.cool -= dt
        self.muzzle = max(0.0, self.muzzle - dt)
        self.hurt = max(0.0, self.hurt - dt)
        self.pain = max(0.0, self.pain - dt)
        L, R, U, D, F = human_keys(g, -1)
        if g.mode == 1 and pygame.key.get_pressed()[pygame.K_RETURN]:
            F = True
        self.a += (int(R) - int(L)) * 2.5 * dt
        mv = (int(U) - int(D)) * 3.0 * dt
        self.px, self.py = self.walk(self.px, self.py, math.cos(self.a) * mv, math.sin(self.a) * mv)
        if mv:
            self.bob += dt * 10
        if F and (not self.fp[0]) and (self.cool <= 0):
            self.shoot()
        self.fp[0] = F
        clear, d = self.los()
        tx, ty = ((self.px - self.mx) / (d or 1), (self.py - self.my) / (d or 1))
        self.mcool -= dt
        if is_cpu(g, 1):
            self.strafe_t -= dt
            if self.strafe_t <= 0:
                self.strafe = random.choice((-1, 1))
                self.strafe_t = random.uniform(0.7, 1.6)
            to = 1 if d > 6.2 else -1 if d < 3.0 else 0
            sp = (1.5, 1.9, 2.3)[g.diff]
            vx = tx * to * sp - ty * self.strafe * sp
            vy = ty * to * sp + tx * self.strafe * sp
            if not doom_free(self.mx + vx * dt * 3, self.my + vy * dt * 3):
                self.strafe = -self.strafe
            self.mx, self.my = self.walk(self.mx, self.my, vx * dt, vy * dt)
            if self.mcool <= 0 and clear:
                self.demon_fire((0.2, 0.12, 0.06)[g.diff])
                self.mcool = random.uniform(1.0, 1.7) * (1.35, 1.0, 0.8)[g.diff]
        else:
            L2, R2, U2, D2, F2 = human_keys(g, 1)
            vx = tx * (int(U2) - int(D2)) * 2.4 - ty * (int(R2) - int(L2)) * 2.4
            vy = ty * (int(U2) - int(D2)) * 2.4 + tx * (int(R2) - int(L2)) * 2.4
            self.mx, self.my = self.walk(self.mx, self.my, vx * dt, vy * dt)
            if F2 and (not self.fp[1]) and (self.mcool <= 0):
                self.demon_fire(0.0)
                self.mcool = 0.7
            self.fp[1] = F2
        for b in list(self.balls):
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            if not doom_free(b[0], b[1], 0.05):
                self.balls.remove(b)
            elif math.hypot(b[0] - self.px, b[1] - self.py) < 0.42:
                self.balls.remove(b)
                self.hp -= 18
                self.pain = 0.3
                g.play('dmg')
                g.flash((255, 0, 0), 110)
        if self.mhp <= 0:
            self.dead = True
            g.play('win')
            self.award(-1, 2, 'DEMON SLAIN! %s +2' % g.who(-1))
            self.end_soon(1.8)
        elif self.hp <= 0:
            self.dead = True
            g.play('pacdeath')
            self.award(1, 2, 'YOU DIED! %s +2' % g.who(1))
            self.end_soon(1.8)

    def on_timeout(self):
        g = self.g
        a, b = (self.hp / 100.0, self.mhp / 90.0)
        if abs(a - b) < 0.02:
            g.popup(W / 2, H / 2, 'STANDOFF - NO WINNER', WHITE, 26)
        else:
            self.award(-1 if a > b else 1, 1, 'MORE HEALTH! %s +1' % g.who(-1 if a > b else 1))

    def project(self, wx, wy, inv, dirx, diry, plx, ply):
        sx, sy = (wx - self.px, wy - self.py)
        return (inv * (diry * sx - dirx * sy), inv * (-ply * sx + plx * sy))

    def draw_front(self, s):
        g = self.g
        VY, VH, N = (self.VY, self.VH, self.N)
        cw = W // N
        s.fill(BLACK)
        q = VH // 8
        for i in range(4):
            pygame.draw.rect(s, (40 + i * 10, 12, 20 + i * 5), (0, VY + i * q, W, q + 2))
            pygame.draw.rect(s, (46 + i * 14, 40 + i * 12, 40 + i * 12), (0, VY + VH // 2 + i * q, W, q + 2))
        dirx, diry = (math.cos(self.a), math.sin(self.a))
        plx, ply = (-diry * 0.66, dirx * 0.66)
        zb = [99.0] * N
        for i in range(N):
            cam = 2.0 * i / N - 1.0
            dist, side, wx, t = doom_cast(self.px, self.py, dirx + plx * cam, diry + ply * cam)
            zb[i] = dist
            h = min(int(VH / dist), VH * 3)
            y0 = VY + (VH - h) // 2
            sh = max(0.38, 1.0 - dist * 0.06) * (0.72 if side else 1.0) * (0.86 if int(wx * 4) % 2 else 1.0)
            base = DOOM_COL[t]
            top, bot = (max(VY, y0), min(VY + VH, y0 + h))
            pygame.draw.rect(s, (int(base[0] * sh), int(base[1] * sh), int(base[2] * sh)), (i * cw, top, cw, max(2, bot - top)))
        inv = 1.0 / (plx * diry - dirx * ply)
        sprites = []
        if self.mhp > 0:
            tx, ty = self.project(self.mx, self.my, inv, dirx, diry, plx, ply)
            sprites.append((ty, 'd', tx, ty, None))
        for b in self.balls:
            tx, ty = self.project(b[0], b[1], inv, dirx, diry, plx, ply)
            sprites.append((ty, 'b', tx, ty, b))
        sprites.sort(key=lambda z: -z[0])
        for _, kind, tx, ty, b in sprites:
            if ty < 0.25:
                continue
            scx = int(N / 2.0 * (1 + tx / ty))
            if kind == 'd':
                sh_ = int(VH / ty * 1.2)
                wcols = max(2, sh_ // cw)
                left = scx - wcols // 2
                top = VY + VH // 2 - sh_ // 2 - int(math.sin(g.t * 3) * 10 / ty)
                sc = sh_ / 16.0
                flash = self.hurt > 0 and int(g.t * 24) % 2
                for c in range(left, left + wcols):
                    if 0 <= c < N and ty < zb[c]:
                        tex = min(15, int((c - left) * 16 / wcols))
                        for y0, y1, col in DEMON_RUNS[tex]:
                            yy = top + int(y0 * sc)
                            hh = max(2, int((y1 - y0) * sc) + 1)
                            yy2 = max(yy, VY)
                            hh = min(yy + hh, VY + VH) - yy2
                            if hh > 0:
                                pygame.draw.rect(s, WHITE if flash else col, (c * cw, yy2, cw, hh))
            else:
                c = scx
                if 0 <= c < N and ty < zb[c]:
                    r = max(3, int(VH / ty * 0.09))
                    cy = VY + VH // 2 + int(VH / ty * 0.06)
                    pygame.draw.rect(s, (255, 150, 30), (c * cw - r - 4, cy - r - 4, 2 * r + 8, 2 * r + 8))
                    pygame.draw.rect(s, WHITE, (c * cw - r, cy - r, 2 * r, 2 * r))
        if self.pain > 0:
            g.alpha_rect(s, (0, VY, W, VH), (255, 0, 0), 100)
        cx, cy = (W // 2, VY + VH // 2)
        pygame.draw.rect(s, WHITE, (cx - 14, cy - 1, 10, 2))
        pygame.draw.rect(s, WHITE, (cx + 6, cy - 1, 10, 2))
        pygame.draw.rect(s, WHITE, (cx - 1, cy - 14, 2, 10))
        pygame.draw.rect(s, WHITE, (cx - 1, cy + 6, 2, 10))
        rec = int(self.muzzle / 0.12 * 26)
        bobx = int(math.sin(self.bob) * 8)
        gx, gy = (W // 2 + 110 + bobx, VY + VH + rec)
        pygame.draw.rect(s, (215, 215, 222), (gx - 14, gy - 150, 28, 150))
        pygame.draw.rect(s, (130, 130, 140), (gx - 14, gy - 150, 5, 150))
        pygame.draw.rect(s, (70, 70, 80), (gx - 46, gy - 60, 92, 60))
        pygame.draw.rect(s, (190, 140, 90), (gx - 26, gy - 30, 52, 30))
        if self.muzzle > 0:
            pygame.draw.polygon(s, (255, 230, 60), [(gx, gy - 214), (gx + 16, gy - 170), (gx + 44, gy - 160), (gx + 14, gy - 146), (gx, gy - 120), (gx - 14, gy - 146), (gx - 44, gy - 160), (gx - 16, gy - 170)])
            pygame.draw.rect(s, WHITE, (gx - 8, gy - 190, 16, 16))
        pygame.draw.rect(s, (30, 24, 24), (0, VY + VH, W, H - VY - VH))
        pygame.draw.rect(s, (150, 140, 120), (0, VY + VH, W, 4))
        g.text_at(s, 'HEALTH', 90, VY + VH + 16, 15, (255, 80, 80))
        pygame.draw.rect(s, (60, 20, 20), (20, VY + VH + 26, 140, 14))
        pygame.draw.rect(s, (230, 50, 50), (20, VY + VH + 26, int(140 * clamp(self.hp / 100.0, 0, 1)), 14))
        g.text_at(s, g.who(1) + ' DEMON', W - 120, VY + VH + 16, 15, (255, 160, 60))
        pygame.draw.rect(s, (60, 40, 10), (W - 190, VY + VH + 26, 140, 14))
        pygame.draw.rect(s, (255, 150, 30), (W - 190, VY + VH + 26, int(140 * clamp(self.mhp / 90.0, 0, 1)), 14))
        fx, fy = (W // 2 - 20, VY + VH + 10)
        pygame.draw.rect(s, (120, 220, 255), (fx, fy, 40, 34))
        pygame.draw.rect(s, BLACK, (fx + 8, fy + 10, 5, 7))
        pygame.draw.rect(s, BLACK, (fx + 27, fy + 10, 5, 7))
        if self.hp > 55:
            pygame.draw.rect(s, BLACK, (fx + 12, fy + 24, 16, 3))
        else:
            pygame.draw.rect(s, BLACK, (fx + 12, fy + 22, 16, 6))
            if self.hp < 35:
                pygame.draw.rect(s, (230, 40, 40), (fx + 30, fy + 2, 5, 10))
        if 2.8 < self.t < 8.0:
            self.hint(s, VY + 8)
