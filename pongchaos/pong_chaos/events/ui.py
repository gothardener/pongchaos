from __future__ import annotations
import math
import random
import pygame
from ..core import *
from .base import *

from .standard import PaddleDrift

def para(g, s, text, x, y, size, color, maxw, center=False):
    px = text_px(size)
    adv = 6 * px
    lines = wrap_text(str(text).upper(), max(1, int(maxw // adv)))
    for i, ln in enumerate(lines):
        t_ = g.render(ln, size, color)
        xx = x + (maxw - t_.get_width()) // 2 if center else x
        s.blit(t_, (_sn(xx), _sn(y + i * 9 * px)))
    return y + len(lines) * 9 * px

def win95(g, s, x, y, w, h, title, tcol=(0, 0, 170), bg=(200, 200, 200), x_btn=True):
    x, y, w, h = (int(x), int(y), int(w), int(h))
    pygame.draw.rect(s, (16, 16, 16), (x + 6, y + 6, w, h))
    pygame.draw.rect(s, bg, (x, y, w, h))
    pygame.draw.rect(s, WHITE, (x, y, w, 2))
    pygame.draw.rect(s, WHITE, (x, y, 2, h))
    pygame.draw.rect(s, (70, 70, 70), (x, y + h - 2, w, 2))
    pygame.draw.rect(s, (70, 70, 70), (x + w - 2, y, 2, h))
    pygame.draw.rect(s, tcol, (x + 4, y + 4, w - 8, 20))
    g.text_at(s, title, x + 10, y + 8, 15, WHITE, center=False)
    if x_btn:
        pygame.draw.rect(s, bg, (x + w - 24, y + 6, 16, 16))
        pygame.draw.rect(s, BLACK, (x + w - 24, y + 6, 16, 16), 2)
        pygame.draw.line(s, BLACK, (x + w - 20, y + 10), (x + w - 12, y + 18), 2)
        pygame.draw.line(s, BLACK, (x + w - 12, y + 10), (x + w - 20, y + 18), 2)
    return (x + 8, y + 30, w - 16, h - 38)

def button(g, s, x, y, w, h, label, col=(210, 210, 210), tcol=BLACK):
    pygame.draw.rect(s, col, (x, y, w, h))
    pygame.draw.rect(s, WHITE, (x, y, w, 2))
    pygame.draw.rect(s, WHITE, (x, y, 2, h))
    pygame.draw.rect(s, (60, 60, 60), (x, y + h - 2, w, 2))
    pygame.draw.rect(s, (60, 60, 60), (x + w - 2, y, 2, h))
    g.text_at(s, label, x + w // 2, y + h // 2, 15, tcol)

def bubble(g, s, text, x, y, tx, ty, size=15, fill=WHITE, col=BLACK):
    t_ = g.render(text, size, col)
    w, h = (t_.get_width() + 20, t_.get_height() + 16)
    x = clamp(x, 6, W - w - 6)
    y = clamp(y, 6, H - h - 6)
    pygame.draw.polygon(s, fill, [(x + w * 0.3, y + h - 2), (x + w * 0.5, y + h - 2), (tx, ty)])
    pygame.draw.rect(s, fill, (x, y, w, h))
    pygame.draw.rect(s, col, (x, y, w, h), 2)
    s.blit(t_, (_sn(x + 10), _sn(y + 8)))
AD_TEXT = [('HOT SINGLE PADDLES IN YOUR AREA!!', 'CLICK HERE. NO VIRUS.'), ('YOU WON A FREE BALL!', 'CLAIM IT IN 3 SECONDS'), ('DOWNLOAD MORE RAM', '100 PERCENT FREE (NOT FREE)'), ('ONE WEIRD TRICK TO WIN PONG', 'CPUS HATE IT!'), ('LOCAL GRANDMA BEATS YOU AT PONG', 'SEE HOW'), ('GOLDEN PADDLES - 99.99 A MONTH', 'CANCEL ANYTIME* (*NO)'), ('TIRED OF BEING BAD?', 'TRY GETTING GOOD.'), ("YOUR CAR'S WARRANTY IS EXPIRING", 'CALL NOW OR ELSE'), ('YOU ARE THE 1,000,000TH VISITOR', '(THE BALL WAS THE OTHER 999,999)'), ('SMART PADDLE. SMARTER BALL.', 'NOW WITH WIFI')]

@reg
class AdBreak(Event):
    name = 'AD BREAK'
    sub = 'PRESS X TO CLOSE (WHEN IT LETS YOU)'
    dur = 14
    group = 'ad'

    def start(self):
        self.ads = []
        self.cd = 0.0
        self.new_ad()

    def new_ad(self):
        if len(self.ads) >= 4:
            return
        w, h = (random.randint(250, 330), random.randint(150, 200))
        x = random.randint(130, W - 130 - w)
        y = random.randint(70, H - 80 - h)
        head, tail = random.choice(AD_TEXT)
        self.ads.append({'x': x, 'y': y, 'w': w, 'h': h, 'head': head, 'tail': tail, 'age': 0.0, 'col': random.choice(BANNER_COLORS), 'wait': random.uniform(2.0, 3.4)})
        self.g.play('notify')

    def update(self, dt):
        for a in self.ads:
            a['age'] += dt
        self.cd += dt
        if self.cd > 3.2 and self.t < self.dur - 4:
            self.cd = 0.0
            self.new_ad()

    def on_key(self, key):
        if key == pygame.K_x and self.ads:
            a = self.ads[-1]
            if a['age'] >= a['wait']:
                self.ads.pop()
                self.g.play('pop')
                self.g.parts.burst(a['x'] + a['w'] / 2, a['y'] + a['h'] / 2, a['col'], 18, 260, 0.5, 5)
            else:
                a['wait'] += 0.7
                self.g.play('uhoh', 0.5)
                self.g.popup(a['x'] + a['w'] / 2, a['y'], 'NOT YET!', (255, 80, 80), 20)

    def draw_top(self, s):
        g = self.g
        for a in self.ads:
            col = a['col'] if int(g.t * 6) % 2 else tint(a['col'], 0.72)
            cx, cy, cw, ch = win95(g, s, a['x'], a['y'], a['w'], a['h'], 'ADVERTISEMENT', (170, 0, 0))
            pygame.draw.rect(s, col, (cx, cy, cw, ch))
            para(g, s, a['head'], cx + 6, cy + 8, 22, BLACK, cw - 12, True)
            para(g, s, a['tail'], cx + 6, cy + ch - 54, 15, (70, 0, 70), cw - 12, True)
            left = a['wait'] - a['age']
            ok = left <= 0
            button(g, s, cx + cw // 2 - 52, cy + ch - 28, 104, 22, '[X] CLOSE' if ok else 'SKIP IN %d' % (int(left) + 1), (230, 230, 230) if ok else (150, 150, 150), BLACK if ok else (90, 90, 90))
COOKIE_STAGES = [('WE VALUE YOUR PRIVACY', 'THIS GAME USES COOKIES TO SELL YOUR PADDLE POSITION TO 4000 PARTNERS.', '[Y] ACCEPT ALL', '[N] NO THANKS'), ('ARE YOU SURE?', 'WITHOUT COOKIES THE BALL WILL BE SAD. AND SO WILL WE.', '[Y] ACCEPT ALL', '[N] I AM SURE'), ('OPTIONS: PARTNER 1 OF 47', 'EACH PARTNER CAN BE TOGGLED. THEY ARE ALL ON. THEY STAY ON.', '[Y] ACCEPT ALL', '[N] NEXT PARTNER'), ('LAST CHANCE', 'THE COOKIE MONSTER HAS BEEN NOTIFIED OF YOUR REFUSAL.', '[Y] FINE', '[N] NO NO NO')]

@reg
class CookieBanner(Event):
    name = 'COOKIE BANNER'
    sub = 'Y = ACCEPT    N = REFUSE (GOOD LUCK)'
    dur = 14
    group = 'dialog'
    grabs_keys = True

    def start(self):
        self.stage = 0
        self.closed = False

    def close(self, msg, col):
        self.closed = True
        self.g.popup(W / 2, H - 200, msg, col, 26)
        self.done = True

    def on_key(self, key):
        g = self.g
        if self.closed:
            return
        if key == pygame.K_y:
            g.play('coin')
            for _ in range(3):
                g.parts.burst(random.uniform(100, W - 100), H - 130, (205, 140, 70), 10, 300, 0.9, 6, 400)
            self.close('COOKIES ACCEPTED. YUM.', (255, 200, 100))
        elif key == pygame.K_n:
            if self.stage < len(COOKIE_STAGES) - 1:
                self.stage += 1
                g.play('uhoh')
                g.flash((255, 150, 0), 40)
            else:
                for b in g.real_balls():
                    b.set_speed(min(MAX_SPEED * 0.9, b.speed() * 1.18))
                g.play('boom', 0.5)
                self.close('THE COOKIE MONSTER SPEEDS UP THE BALL!', (255, 80, 80))

    def end(self):
        if not self.closed:
            self.g.popup(W / 2, H - 200, 'ACCEPTED FOR YOU!', (255, 200, 100), 24)

    def draw_top(self, s):
        g = self.g
        y0 = H - 168
        pygame.draw.rect(s, (30, 30, 40), (0, y0 - 6, W, 174))
        pygame.draw.rect(s, (245, 245, 245), (0, y0, W, 168))
        pygame.draw.circle(s, (205, 140, 70), (76, y0 + 84), 44)
        for dx, dy in ((-18, -14), (12, -22), (20, 8), (-8, 14), (-26, 12), (6, -2)):
            pygame.draw.rect(s, (80, 40, 20), (76 + dx, y0 + 84 + dy, 8, 8))
        pygame.draw.rect(s, (120, 70, 30), (60, y0 + 76, 4, 4))
        title, body, yes, no = COOKIE_STAGES[self.stage]
        g.text_at(s, title, 150, y0 + 18, 22, (30, 30, 30), center=False)
        para(g, s, body, 150, y0 + 48, 15, (70, 70, 70), W - 190)
        button(g, s, 150, y0 + 112, 250, 40, yes, (60, 190, 90), WHITE)
        button(g, s, 430, y0 + 112, 250, 40, no, (170, 170, 170), (60, 60, 60))

@reg
class UpdateInstalling(Event):
    name = 'SYSTEM UPDATE'
    sub = 'R = RESTART NOW    L = REMIND ME LATER'
    dur = 13
    group = 'fullscreen'

    def start(self):
        self.prog = 0.0
        self.hide = 0.0
        self.restart = 0.0
        self.g.play('notify')

    def update(self, dt):
        g = self.g
        if self.hide > 0:
            self.hide -= dt
            if self.hide <= 0:
                g.play('notify')
                g.popup(W / 2, 150, 'REMINDER: UPDATE!', (255, 220, 60), 24)
            return
        if self.restart > 0:
            self.restart -= dt
            if self.restart <= 0:
                self.done = True
            return
        if self.prog < 99:
            self.prog = min(99.0, self.prog + dt * random.uniform(8, 40))
        elif random.random() < 0.01:
            self.prog = random.uniform(12, 60)
            g.play('uhoh', 0.4)

    def on_key(self, key):
        g = self.g
        if self.hide > 0 or self.restart > 0:
            return
        if key == pygame.K_l:
            self.hide = 2.4
            g.play('pop')
        elif key == pygame.K_r:
            self.restart = 1.6
            g.play('rewind', 0.6)
            g.flash(WHITE, 160)
            for b in g.real_balls():
                b.x, b.y = (W / 2, H / 2)
                a = random.uniform(-0.5, 0.5)
                b.vx, b.vy = (random.choice((-1, 1)) * math.cos(a) * BASE_SPEED, math.sin(a) * BASE_SPEED)
            g.popup(W / 2, H / 2 + 80, 'BALL REBOOTED', (120, 255, 160), 26)

    def draw_top(self, s):
        g = self.g
        if self.hide > 0:
            return
        fail = self.t > self.dur - 1.8
        cx, cy, cw, ch = win95(g, s, 130, 46, 540, 218, 'SYSTEM UPDATE (1 OF 9999)')
        pygame.draw.rect(s, (230, 230, 230), (cx, cy, cw, ch))
        if self.restart > 0:
            g.text_at(s, 'RESTARTING...', cx + cw // 2, cy + 60, 30, (20, 20, 20))
            g.text_at(s, "PLEASE DON'T MOVE YOUR PADDLE", cx + cw // 2, cy + 110, 15, (90, 90, 90))
            return
        g.text_at(s, 'UPDATE FAILED. UNDOING CHANGES...' if fail else 'INSTALLING IMPORTANT UPDATE', cx + cw // 2, cy + 20, 15, (200, 30, 30) if fail else (20, 20, 20))
        pygame.draw.rect(s, WHITE, (cx + 10, cy + 44, cw - 20, 28))
        pygame.draw.rect(s, (90, 90, 90), (cx + 10, cy + 44, cw - 20, 28), 2)
        pygame.draw.rect(s, (40, 80, 220), (cx + 14, cy + 48, int((cw - 28) * self.prog / 100.0), 20))
        g.text_at(s, '%d%%  %s' % (int(self.prog), '|/-\\'[int(g.t * 8) % 4]), cx + cw // 2, cy + 94, 22, (20, 20, 20))
        g.text_at(s, 'DO NOT TURN OFF YOUR PONG', cx + cw // 2, cy + 120, 15, (90, 90, 90))
        button(g, s, cx + 40, cy + ch - 34, 170, 26, '[R] RESTART NOW')
        button(g, s, cx + cw - 210, cy + ch - 34, 170, 26, '[L] REMIND ME LATER')

@reg
class NotResponding(Event):
    name = 'NOT RESPONDING'
    sub = 'THE BALL IS BUFFERING... THEN CATCHES UP'
    dur = 2.4
    group = 'time'

    def start(self):
        self.g.fset('bts', self, 0.0)
        self.g.play('error')

    def end(self):
        g = self.g
        for b in g.real_balls():
            if b.stuck or b.captured:
                continue
            raw = b.y + b.vy * 0.9
            n = int(math.floor(raw / H))
            y = raw % (2 * H)
            if y > H:
                y = 2 * H - y
            b.y = clamp(y, 8, H - 8)
            if n % 2:
                b.vy = -b.vy
            b.x = clamp(b.x + b.vx * 0.9, 90, W - 90)
        g.play('whoosh')
        g.flash(WHITE, 90)

    def draw_top(self, s):
        g = self.g
        g.alpha_rect(s, (0, 0, W, H), (230, 230, 230), 100)
        cx, cy, cw, ch = win95(g, s, 220, 230, 360, 130, 'PONG (NOT RESPONDING)', (130, 130, 150))
        g.text_at(s, 'PONG IS NOT RESPONDING', cx + cw // 2, cy + 22, 15, BLACK)
        g.text_at(s, 'THE BALL WILL RETURN SHORTLY', cx + cw // 2, cy + 46, 15, (80, 80, 80))
        button(g, s, cx + 30, cy + ch - 36, 120, 24, 'WAIT')
        button(g, s, cx + cw - 150, cy + ch - 36, 120, 24, 'END TASK')
        hx, hy = (W // 2, 190)
        pygame.draw.polygon(s, WHITE, [(hx - 14, hy - 20), (hx + 14, hy - 20), (hx, hy), (hx + 14, hy + 20), (hx - 14, hy + 20), (hx, hy)])
        pygame.draw.rect(s, (255, 220, 60), (hx - 6, hy + 8 + int(g.t * 8) % 8, 12, 6))

@reg
class BlueScreen(Event):
    name = 'BLUE SCREEN'
    sub = "THE GAME IS STILL RUNNING. YOU JUST CAN'T SEE IT."
    dur = 3.3
    group = 'fullscreen'

    def start(self):
        self.g.play('error')

    def draw_top(self, s):
        g = self.g
        pygame.draw.rect(s, (0, 0, 170), (0, 0, W, H))
        g.text_at(s, ':(', 90, 110, 100, WHITE)
        para(g, s, "YOUR PONG RAN INTO A PROBLEM AND NEEDS TO RESTART. WE'RE JUST COLLECTING SOME ERROR INFO.", 60, 190, 22, WHITE, W - 120)
        pct = int(clamp(self.t / (self.dur - 0.4), 0, 1) * 100)
        g.text_at(s, '%d%% COMPLETE' % pct, 150, 290, 22, WHITE)
        pygame.draw.rect(s, WHITE, (60, 330, 120, 120), 4)
        qr = random.Random(3)
        for k in range(36):
            if qr.random() < 0.55 or k in (0, 5, 30, 35):
                pygame.draw.rect(s, WHITE, (68 + k % 6 * 18, 68 + 270 + k // 6 * 18, 14, 14))
        para(g, s, 'STOP CODE: BALL_NOT_FOUND', 220, 340, 22, WHITE, 500)
        para(g, s, 'WHAT FAILED: PADDLE.SYS', 220, 380, 15, WHITE, 500)
        para(g, s, '(THE BALL IS FINE. THE BALL IS ALWAYS FINE.)', 220, 410, 15, (170, 170, 255), 500)

@reg
class Captcha(Event):
    name = 'CAPTCHA'
    dur = 10
    group = 'dialog'
    grabs_keys = True
    LETTERS = 'QWRTYUIOASDFGHJKLZXCVB'

    def start(self):
        g = self.g
        if g.mode == 1:
            self.side = -1 if random.random() < 0.7 else 1
        else:
            self.side = random.choice((-1, 1))
        self.code = ''.join((random.choice(self.LETTERS) for _ in range(4)))
        self.pos = 0
        self.sub = '%s IS FROZEN UNTIL THEY TYPE THE LETTERS' % g.who(self.side)
        self.bot = g.mode == 1 and self.side == 1
        self.bot_t = 3.4
        g.paddle(self.side).mod(self, 'frozen', 1)
        g.play('warn')

    def solved(self):
        g = self.g
        g.paddle(self.side).unmod(self)
        g.play('right')
        g.popup(W / 2, 170, 'ROBOT VERIFIED?!' if self.bot else 'HUMAN VERIFIED!', (120, 255, 160), 30)
        self.done = True

    def update(self, dt):
        if self.bot and self.pos < 4:
            self.bot_t -= dt
            if self.bot_t <= 0:
                self.pos = 4
        if self.pos >= 4 and (not self.done):
            self.solved()

    def on_key(self, key):
        if self.pos >= 4 or not 97 <= key <= 122:
            return
        if chr(key).upper() == self.code[self.pos]:
            self.pos += 1
            self.g.play('coin', 0.5)
        else:
            self.pos = 0
            self.g.play('uhoh', 0.6)
            self.g.popup(W / 2, 330, 'WRONG! START OVER', (255, 80, 80), 22)

    def draw_top(self, s):
        g = self.g
        cx, cy, cw, ch = win95(g, s, 190, 150, 420, 250, 'ARE YOU A ROBOT?')
        g.text_at(s, 'TYPE THE LETTERS YOU SEE', cx + cw // 2, cy + 20, 15, BLACK)
        pygame.draw.rect(s, (245, 245, 235), (cx + 20, cy + 44, cw - 40, 86))
        rnd = random.Random(int(g.t * 8))
        for i, ch_ in enumerate(self.code):
            col = hsv(0.15 * i + 0.6, 0.8, 0.7)
            t_ = g.render(ch_, 46, col)
            s.blit(t_, (_sn(cx + 70 + i * 74 + rnd.randint(-4, 4)), _sn(cy + 56 + rnd.randint(-6, 8))))
        for _ in range(7):
            pygame.draw.line(s, (90, 90, 90), (cx + 24, cy + rnd.randint(46, 126)), (cx + cw - 24, cy + rnd.randint(46, 126)), 2)
        for i in range(4):
            done = i < self.pos
            pygame.draw.rect(s, (60, 200, 90) if done else (150, 150, 150), (cx + 110 + i * 48, cy + 144, 36, 20))
        g.text_at(s, "ONLY ROBOTS CAN'T TYPE. PROBABLY.", cx + cw // 2, cy + 184, 15, (90, 90, 90))
TOS = ['1. YOU AGREE TO LOSE.', '2. THE BALL OWNS YOUR PADDLE.', '3. WE MAY SELL YOUR REFLEXES.', '4. NO REFUNDS ON POINTS.', '5. THE CPU IS NOT RESPONSIBLE FOR BEING BETTER.', '6. BY READING THIS YOU OWE US 3 DOLLARS.', '7. DO NOT FEED THE BALL AFTER MIDNIGHT.', '8. YOUR FIRSTBORN PIXEL IS FORFEIT.', '9. SEE CLAUSE 1.', '10. CLAUSE 9 DOES NOT EXIST.', '11. WE ARE NOT LIABLE FOR EXPLODING PADDLES.', '12. THIS AGREEMENT SELF-DESTRUCTS IN 5 SECONDS.', '13. YOU HAVE NOT READ THIS.', "14. YOU STILL HAVEN'T.", '15. THE FINE PRINT IS THE REAL GAME.']

@reg
class TermsOfService(Event):
    name = 'TERMS OF SERVICE'
    sub = 'MASH ENTER 8 TIMES TO AGREE'
    dur = 13
    group = 'dialog'

    def start(self):
        self.n = 0
        self.scroll = 0.0
        self.ok = False

    def update(self, dt):
        self.scroll += dt * (26 + 18 * self.n)

    def on_key(self, key):
        if key in (pygame.K_RETURN, pygame.K_KP_ENTER) and (not self.ok):
            self.n += 1
            self.g.play('tick')
            if self.n >= 8:
                self.ok = True
                self.g.play('cash')
                self.g.popup(W / 2, 140, 'THANKS FOR YOUR SOUL!', (255, 220, 60), 26)
                self.done = True

    def end(self):
        if not self.ok:
            for b in self.g.real_balls():
                b.set_speed(min(MAX_SPEED * 0.9, b.speed() * 1.15))
            self.g.popup(W / 2, 140, 'AGREED BY DEFAULT. BALL SPEEDS UP.', (255, 100, 100), 22)

    def draw_top(self, s):
        g = self.g
        cx, cy, cw, ch = win95(g, s, 120, 90, 560, 380, 'TERMS OF SERVICE v9.7.3.1')
        pygame.draw.rect(s, WHITE, (cx, cy, cw, ch - 56))
        clip = pygame.Surface((cw - 16, ch - 64))
        clip.fill(WHITE)
        for i in range(len(TOS) * 3):
            yy = int(i * 22 - self.scroll) % (len(TOS) * 3 * 22) - 22
            t_ = g.render(TOS[i % len(TOS)], 15, (40, 40, 40))
            clip.blit(t_, (0, yy))
        s.blit(clip, (cx + 8, cy + 4))
        button(g, s, cx + cw // 2 - 110, cy + ch - 46, 220, 34, '[ENTER] I AGREE %d/8' % self.n, (150, 220, 150))

@reg
class LowBattery(Event):
    name = 'LOW BATTERY'
    sub = 'THE PADDLES ARE RUNNING OUT OF JUICE'
    dur = 12
    group = 'ctrl'

    def update(self, dt):
        g = self.g
        f = 1.0 - 0.58 * clamp(self.t / 5.0, 0, 1) if self.t < 8 else 1.0
        for p in g.paddles:
            p.unmod(self)
            p.mod(self, 'speed', f)
        if 8 <= self.t < 8 + dt * 2:
            g.play('powerup')
            g.popup(W / 2, 200, 'CHARGING...', (120, 255, 160), 30)

    def draw_top(self, s):
        g = self.g
        if self.t < 8:
            d = clamp((self.t - 1.5) / 6.0, 0, 0.75)
            for y in range(0, H, 4):
                if y // 4 * 7 % 10 < d * 10:
                    pygame.draw.rect(s, BLACK, (0, y, W, 2))
            pct = max(1, int(12 - self.t * 1.4))
            col = (255, 60, 60) if int(g.t * 3) % 2 else (255, 200, 60)
        else:
            pct = min(100, int((self.t - 8) * 25))
            col = (80, 255, 120)
        bx, by = (W - 140, 78)
        pygame.draw.rect(s, WHITE, (bx, by, 90, 40), 4)
        pygame.draw.rect(s, WHITE, (bx + 90, by + 10, 8, 20))
        pygame.draw.rect(s, col, (bx + 8, by + 8, max(2, int(74 * pct / 100.0)), 24))
        g.text_at(s, '%d%%' % pct, bx + 45, by + 60, 15, col)
SPAM = ['NEW MESSAGE FROM GRANDMA', 'YOUR BALL HAS A VIRUS', '50 PERCENT OFF PADDLES', 'BATTERY AT 100 PERCENT (LOL)', 'SOMEONE LIKED YOUR POINT', 'UPDATE YOUR UPDATER', 'THE CPU POKED YOU', 'YOU HAVE WON NOTHING', 'REMINDER: BLINK', 'DELIVERY ARRIVING: 1 BALL', 'STORAGE FULL: 99 PONGS', 'CPU IS TYPING...', 'FRIEND REQUEST: THE BALL', 'LOW MEMORY: GOLDFISH', 'WEATHER: CHANCE OF PONG', 'YOUR PADDLE IS TRENDING', 'DID YOU MEAN: LOSE?', 'PLEASE RATE YOUR LAST POINT']

@reg
class SpamNotifs(Event):
    name = 'NOTIFICATION SPAM'
    sub = 'DING DING DING DING'
    dur = 11
    group = 'toast'

    def start(self):
        self.items = []
        self.cd = 0.0

    def update(self, dt):
        self.cd -= dt
        if self.cd <= 0 and self.t < self.dur - 2.5:
            self.cd = random.uniform(0.45, 0.8)
            self.items.append([0.0, random.choice(SPAM), random.choice(BANNER_COLORS)])
            self.items = self.items[-6:]
            self.g.play('notify', 0.45)
        for it in self.items:
            it[0] += dt
        self.items = [it for it in self.items if it[0] < 2.6]

    def draw_top(self, s):
        g = self.g
        for i, (age, msg, col) in enumerate(self.items):
            slide = int((1 - min(1.0, age / 0.2)) * 300)
            x, y = (W - 292 + slide, 70 + i * 54)
            pygame.draw.rect(s, (30, 30, 40), (x, y, 282, 48))
            pygame.draw.rect(s, col, (x, y, 282, 48), 2)
            pygame.draw.rect(s, col, (x + 8, y + 8, 32, 32))
            g.text_at(s, '!', x + 24, y + 24, 22, BLACK)
            para(g, s, msg, x + 50, y + 9, 15, WHITE, 224)
ACH = ['BREATHING (+0)', 'TOUCHED THE BALL (+0)', 'DID NOTHING (+0)', 'BLINKED (+0)', 'LOOKED AT THE SCREEN (+0)', 'MISSED ON PURPOSE (+0)', 'READ THIS (+0)', 'BEING ALIVE (+0)', 'HOLDING A KEYBOARD (+0)', 'CLICKED NOTHING (+0)']

@reg
class AchievementSpam(Event):
    name = 'ACHIEVEMENT SPAM'
    sub = 'YOU ARE SO GOOD AT EXISTING'
    dur = 10

    def start(self):
        self.items = []
        self.cd = 0.0

    def update(self, dt):
        self.cd -= dt
        if self.cd <= 0 and self.t < self.dur - 2.5:
            self.cd = random.uniform(0.7, 1.1)
            self.items.append([0.0, random.choice(ACH)])
            self.items = self.items[-5:]
            self.g.play('coin', 0.5)
        for it in self.items:
            it[0] += dt
        self.items = [it for it in self.items if it[0] < 2.5]

    def draw_top(self, s):
        g = self.g
        for i, (age, msg) in enumerate(self.items):
            x, y = (14, 80 + i * 50)
            pygame.draw.rect(s, (24, 24, 24), (x, y, 318, 44))
            pygame.draw.rect(s, GOLD, (x, y, 318, 44), 2)
            pygame.draw.rect(s, GOLD, (x + 12, y + 8, 22, 18))
            pygame.draw.rect(s, GOLD, (x + 18, y + 26, 10, 10))
            g.text_at(s, 'ACHIEVEMENT UNLOCKED', x + 46, y + 7, 15, GOLD, center=False)
            g.text_at(s, msg, x + 46, y + 25, 15, WHITE, center=False)

@reg
class PhoneCall(Event):
    name = 'INCOMING CALL'
    dur = 11
    group = 'dialog'
    grabs_keys = True
    CALLERS = ['MOM', 'GRANDMA', 'UNKNOWN NUMBER', 'YOUR BANK', 'THE CPU', 'DAD', 'PIZZA GUY', 'YOUR BOSS', 'SPAM LIKELY']
    TALK = ['DID YOU EAT?', "WE NEED TO TALK ABOUT YOUR CAR'S WARRANTY", 'ARE YOU STILL PLAYING THE PONG?', 'WHY IS THERE A BALL IN MY SOUP?', 'YOUR PIZZA IS ON THE ROOF', 'HAVE YOU TRIED UNPLUGGING YOURSELF?', "I'M NOT ANGRY, JUST DISAPPOINTED"]

    def start(self):
        g = self.g
        self.caller = random.choice(self.CALLERS)
        self.sub = '%s IS CALLING  -  Y ANSWER   N DECLINE' % self.caller
        self.st = 'ring'
        self.ring_t = 0.0
        self.redials = 0
        self.tm = 0.0
        self.line = random.choice(self.TALK)
        self.side = -1 if g.mode == 1 else random.choice((-1, 1))

    def update(self, dt):
        g = self.g
        if self.st == 'ring':
            self.ring_t -= dt
            if self.ring_t <= 0:
                self.ring_t = 1.3
                g.play('ring')
            p = g.paddle(self.side)
            p.y = clamp(p.y + random.uniform(-6, 6), 0, H - p.h)
        elif self.st == 'talk':
            self.tm += dt
            if self.tm > 2.6:
                self.done = True
        else:
            self.tm += dt
            if self.tm > 1.5:
                if self.redials < 2:
                    self.redials += 1
                    self.st = 'ring'
                    self.ring_t = 0.0
                    g.popup(W - 150, H - 220, 'CALLING AGAIN...', (255, 220, 60), 20)
                else:
                    self.done = True

    def on_key(self, key):
        g = self.g
        if self.st != 'ring':
            return
        if key == pygame.K_y:
            self.st = 'talk'
            self.tm = 0.0
            g.paddle(self.side).mod(self, 'frozen', 1)
            g.play('pop')
        elif key == pygame.K_n:
            self.st = 'gone'
            self.tm = 0.0
            g.play('uhoh', 0.6)

    def draw_top(self, s):
        g = self.g
        cx, cy, cw, ch = win95(g, s, W - 320, H - 210, 300, 170, 'PHONE', (20, 120, 60), x_btn=False)
        if self.st == 'talk':
            g.text_at(s, self.caller + ':', cx + cw // 2, cy + 20, 15, (20, 100, 40))
            para(g, s, self.line, cx + 4, cy + 44, 15, BLACK, cw - 8, True)
            return
        shake = int(math.sin(g.t * 40) * 3) if self.st == 'ring' else 0
        g.text_at(s, 'INCOMING CALL' if self.st == 'ring' else 'CALL DECLINED', cx + cw // 2 + shake, cy + 14, 15, (90, 90, 90))
        g.text_at(s, self.caller, cx + cw // 2 + shake, cy + 44, 22, BLACK)
        button(g, s, cx + 6, cy + ch - 36, 120, 30, '[Y] ANSWER', (110, 220, 130))
        button(g, s, cx + cw - 126, cy + ch - 36, 120, 30, '[N] DECLINE', (230, 110, 110))
SUBS = ['[SUSPENSEFUL ACCORDION]', '[THE BALL SAYS BOING]', '[CPU LAUGHS IN BINARY]', '[DISTANT SCREAMING]', '[WET SQUEAKING NOISES]', '[ANGRY PADDLE NOISES]', 'NARRATOR: AND THEN, NOTHING HAPPENED', '[MYSTERIOUS WIND]', '[A DOG BARKS IN SPANISH]', '(DRAMATIC GASP)', '[SOMEONE SPILLS SPAGHETTI]', '[INTENSE BREATHING]', '[RECORD SCRATCH]', '[A SINGLE TEAR]', 'MOM: WHAT ARE YOU PLAYING?', '[THE BALL REGRETS EVERYTHING]', '[ROBOT SIGHS]', '[CRICKETS]', '[MEANINGFUL SILENCE]']

@reg
class Subtitles(Event):
    name = 'SUBTITLES'
    sub = 'THEY ARE NOT HELPFUL'
    dur = 12

    def start(self):
        self.cd = 0.0
        self.txt = ''

    def update(self, dt):
        self.cd -= dt
        if self.cd <= 0:
            self.cd = random.uniform(1.0, 1.7)
            self.txt = random.choice(SUBS)
            if random.random() < 0.15:
                self.txt = '[%s SCREAMS INTERNALLY]' % self.g.who(random.choice((-1, 1)))
            self.g.play('blip_n', 0.5)

    def draw_top(self, s):
        g = self.g
        t_ = g.render(self.txt, 22, WHITE)
        w = t_.get_width() + 30
        x = (W - w) // 2
        pygame.draw.rect(s, BLACK, (x, H - 120, w, 40))
        s.blit(t_, (_sn(x + 15), _sn(H - 120 + 13)))
TIPS = ['TIP: MOVE UP AND DOWN', 'TIP: HIT THE BALL WITH YOUR PADDLE', "TIP: DON'T MISS", 'TIP: THE BALL IS THE SQUARE THING', 'TIP: PRESS W TO GO UP', 'TIP: LOSING IS BAD', 'TIP: POINTS GO UP WHEN YOU SCORE', 'TIP: YOU ARE DOING GREAT (NOT REALLY)', 'TIP: THE WALLS ARE NOT LAVA', 'TIP: HAVE YOU TRIED WINNING?']

@reg
class TutorialPopups(Event):
    name = 'HELPFUL TUTORIAL'
    sub = 'PRESS ANY KEY TO IGNORE THIS HELPFUL TIP'
    dur = 11

    def start(self):
        self.cd = 0.0
        self.tip = random.choice(TIPS)

    def update(self, dt):
        self.cd -= dt
        if self.cd <= 0:
            self.cd = 2.0
            self.tip = random.choice(TIPS)
            self.g.play('blip_n', 0.6)

    def draw_top(self, s):
        g = self.g
        rb = g.real_balls()
        if rb:
            b = rb[0]
            bubble(g, s, self.tip, b.x - 90, b.y - 70 if b.y > 120 else b.y + 40, b.x, b.y - 10 if b.y > 120 else b.y + 10)
        for p in g.paddles:
            if int(g.t * 3) % 2:
                ax = p.x + (36 if p.side < 0 else -22)
                pygame.draw.polygon(s, (255, 230, 0), [(ax, p.cy() - 10), (ax, p.cy() + 10), (ax + (-14 if p.side > 0 else 14), p.cy())])

@reg
class StillWatching(Event):
    name = 'STILL PLAYING?'
    sub = 'PRESS ANY KEY OR THE BALL FALLS ASLEEP'
    dur = 10
    group = 'time'

    def start(self):
        self.st = 'ask'
        self.tm = 0.0
        self.g.fset('bts', self, 0.35)

    def update(self, dt):
        g = self.g
        self.tm += dt
        if self.st == 'ask' and self.tm > 5.0:
            self.st = 'sleep'
            self.tm = 0.0
            g.fset('bts', self, 0.0)
            g.play('timestop', 0.6)
        elif self.st == 'sleep' and self.tm > 2.2:
            self.done = True
            g.popup(W / 2, 200, 'WAKE UP!', (255, 220, 60), 30)
            g.play('go', 0.6)

    def on_key(self, key):
        if self.st == 'ask':
            self.done = True
            self.g.play('pop')

    def draw_top(self, s):
        g = self.g
        if self.st == 'ask':
            g.alpha_rect(s, (0, 0, W, H), BLACK, 100)
            cx, cy, cw, ch = win95(g, s, 220, 200, 360, 150, 'PONG+')
            g.text_at(s, 'ARE YOU STILL PLAYING?', cx + cw // 2, cy + 24, 22, BLACK)
            g.text_at(s, 'AUTO-SLEEP IN %d' % (int(5.0 - self.tm) + 1), cx + cw // 2, cy + 62, 22, (200, 30, 30))
            button(g, s, cx + cw // 2 - 90, cy + ch - 42, 180, 30, 'YES (ANY KEY)', (150, 220, 150))
        else:
            g.alpha_rect(s, (0, 0, W, H), (0, 0, 40), 100)
            for i in range(3):
                g.text_at(s, 'Z', 400 + i * 40, 280 - i * 40 - int(self.tm * 20) % 40, 30 + i * 10, (180, 180, 255))

@reg
class RateGame(Event):
    name = 'RATE THIS GAME'
    sub = 'PRESS 1-5.  CHOOSE WISELY.'
    dur = 10
    group = 'dialog'

    def start(self):
        self.stars = 0
        self.nag = 0.0

    def on_key(self, key):
        g = self.g
        if self.stars or not pygame.K_1 <= key <= pygame.K_5:
            return
        self.stars = key - pygame.K_0
        g.play('coin')
        if self.stars == 5:
            g.popup(W / 2, 150, "WOW THANKS! HERE'S A FREE BALL!", (255, 220, 60), 24)
            rb = g.real_balls()
            if rb:
                g.clone_ball(rb[0])
        elif self.stars == 1:
            g.popup(W / 2, 150, 'WHY?! HAVE SLOW MOTION.', (255, 90, 90), 24)
            g.fset('ts', self, 0.5)
        else:
            g.popup(W / 2, 150, 'THANKS (WE ARE HURT)', (200, 200, 200), 24)
        self.t = max(self.t, self.dur - 1.8)

    def update(self, dt):
        self.nag -= dt
        if self.nag <= 0 and (not self.stars):
            self.nag = 1.6
            self.g.play('notify', 0.5)

    def draw_top(self, s):
        g = self.g
        sh = int(math.sin(g.t * 30) * 2) if not self.stars else 0
        cx, cy, cw, ch = win95(g, s, 200 + sh, 170, 400, 220, 'HOW ARE WE DOING?')
        g.text_at(s, 'ENJOYING PONG: CHAOS EDITION?', cx + cw // 2, cy + 20, 15, BLACK)
        for i in range(5):
            lit = i < self.stars if self.stars else int(g.t * 4) % 6 > i
            col = GOLD if lit else (150, 150, 150)
            sx = cx + 40 + i * 64
            pygame.draw.polygon(s, col, [(sx + 20, cy + 44), (sx + 26, cy + 60), (sx + 42, cy + 62), (sx + 30, cy + 74), (sx + 34, cy + 92), (sx + 20, cy + 82), (sx + 6, cy + 92), (sx + 10, cy + 74), (sx - 2, cy + 62), (sx + 14, cy + 60)])
            g.text_at(s, str(i + 1), sx + 20, cy + 108, 15, BLACK)
        g.text_at(s, 'PLEASE RATE US. PLEASE. PLEASE.', cx + cw // 2, cy + 142, 15, (90, 90, 90))

@reg
class FakePause(Event):
    name = 'PAUSE (NOT REALLY)'
    sub = ''
    dur = 5
    group = 'fullscreen'

    def draw_top(self, s):
        g = self.g
        if self.t < 3.6:
            g.alpha_rect(s, (0, 0, W, H), BLACK, 150)
            g.text_at(s, 'PAUSED', W // 2, H // 2 - 20, 80, WHITE)
            g.text_at(s, 'P / ESC RESUME    ENTER MENU', W // 2, H // 2 + 40, 22, (200, 200, 200))
        else:
            g.text_at(s, 'JUST KIDDING!', W // 2, H // 2, 46, (255, 230, 0) if int(g.t * 8) % 2 else (255, 90, 90))

@reg
class FakeGameOver(Event):
    name = 'GAME OVER (LOL)'
    sub = ''
    dur = 4.6
    group = 'fullscreen'

    def start(self):
        self.who_ = random.choice((-1, 1))
        self.g.play('win', 0.6)

    def draw_top(self, s):
        g = self.g
        if self.t < 3.2:
            g.alpha_rect(s, (0, 150, W, 250), BLACK, 170)
            nm = g.who(self.who_)
            g.text_at(s, '%s WINS!' % nm, W // 2, 215, 70, GOLD)
            g.text_at(s, '7 - %d' % (g.scores[0 if self.who_ > 0 else 1] % 7), W // 2, 285, 50, WHITE)
            g.text_at(s, 'ENTER REMATCH    ESC MENU', W // 2, 350, 22, (210, 210, 210))
        else:
            g.text_at(s, '...JUST KIDDING', W // 2, H // 2, 46, (255, 230, 0) if int(g.t * 8) % 2 else (255, 90, 90))

@reg
class LyingScoreboard(Event):
    name = 'LYING SCOREBOARD'
    sub = 'DO NOT TRUST THE NUMBERS'
    dur = 12
    group = 'score'

    def start(self):
        self.fake_scores = list(self.g.scores)
        self.cd = 0.0

    def update(self, dt):
        self.cd -= dt
        if self.cd <= 0:
            self.cd = random.uniform(0.7, 1.4)
            sc = self.g.scores
            self.fake_scores = [max(0, sc[0] + random.choice((-2, -1, 1, 2, 3))), max(0, sc[1] + random.choice((-2, -1, 1, 2, 3)))]
            if random.random() < 0.25:
                self.fake_scores.reverse()
            self.g.play('blip_n', 0.4)

    def end(self):
        self.g.popup(W / 2, 100, 'THE REAL SCORE: %d-%d' % tuple(self.g.scores), (120, 255, 160), 22)

@reg
class LagSpike(Event):
    name = 'LAG SPIKE'
    sub = 'THE BALL IS RUBBER-BANDING'
    dur = 10
    group = 'time'

    def start(self):
        self.lag = 0.0
        self.run = random.uniform(0.8, 1.4)
        self.ping = 40

    def update(self, dt):
        g = self.g
        if self.lag > 0:
            self.lag -= dt
            self.ping = random.randint(700, 999)
            if self.lag <= 0:
                g.fset('bts', self, 1.0)
                if random.random() < 0.6 and len(g.hist) > 30:
                    snap = g.hist[-24]
                    for b, x, y, vx, vy in snap:
                        if b.alive and b in g.balls and (not b.stuck) and (not b.captured):
                            b.x, b.y, b.vx, b.vy = (x, y, vx, vy)
                    g.play('rewind', 0.4)
                    g.popup(W / 2, 140, 'RUBBER-BAND!', (255, 120, 120), 24)
                self.run = random.uniform(0.9, 1.7)
        else:
            self.ping = random.randint(30, 60)
            self.run -= dt
            if self.run <= 0:
                self.lag = random.uniform(0.35, 0.75)
                g.fset('bts', self, 0.0)
                g.play('glitch', 0.4)

    def draw_top(self, s):
        g = self.g
        col = (255, 60, 60) if self.ping > 300 else (80, 255, 120)
        g.text_at(s, 'PING %dMS' % self.ping, 90, H - 60, 15, col)
        if self.lag > 0:
            g.text_at(s, 'LAG!', W // 2, 130, 46, (255, 60, 60))
            for i in range(8):
                pygame.draw.rect(s, WHITE, (W // 2 - 40 + int(math.cos(g.t * 8 + i) * 40), 200 + int(math.sin(g.t * 8 + i) * 8), 6, 6))

@reg
class Sneeze(Event):
    name = 'AH... AH... AH...'
    sub = ''
    dur = 3.4

    def start(self):
        self.pop = False
        self.g.play('uhoh', 0.4)

    def update(self, dt):
        g = self.g
        if not self.pop and self.t > 2.1:
            self.pop = True
            g.play('sneeze')
            g.flash(WHITE, 200)
            for b in g.real_balls():
                a = random.uniform(-0.9, 0.9)
                sp = min(MAX_SPEED * 0.9, max(b.speed(), BASE_SPEED) * 1.25)
                d = -sign(b.vx) if random.random() < 0.7 else sign(b.vx)
                b.vx, b.vy = (d * math.cos(a) * sp, math.sin(a) * sp)
                g.parts.burst(b.x, b.y, (200, 235, 255), 24, 400, 0.7, 5)
            for p in g.paddles:
                g.parts.burst(p.x + 7, p.cy(), (200, 235, 255), 12, 260, 0.5, 4)

    def draw_top(self, s):
        g = self.g
        if not self.pop:
            k = int(self.t / 0.7) + 1
            g.text_at(s, 'AH' + '.' * min(3, k) if self.t < 2.1 else '', W // 2, 170, 46 + k * 8, (255, 255, 255))
        elif self.t < 3.2:
            g.text_at(s, 'ACHOO!!!', W // 2, 200, 100, (255, 230, 0))

@reg
class FlyInTheRoom(Event):
    name = 'THERE IS A FLY'
    sub = 'BZZZZ'
    dur = 11
    group = 'critter'

    def start(self):
        self.x, self.y = (random.choice((-20, W + 20)), random.uniform(80, H - 80))
        self.a = random.uniform(0, math.tau)
        self.cd = 0.0
        self.hit_cd = 0.0

    def update(self, dt):
        g = self.g
        self.a += random.uniform(-9, 9) * dt
        sp = 190
        rb = g.real_balls()
        if rb and random.random() < 0.025:
            b = rb[0]
            self.a = math.atan2(b.y - self.y, b.x - self.x)
        self.x = clamp(self.x + math.cos(self.a) * sp * dt, 0, W)
        self.y = clamp(self.y + math.sin(self.a) * sp * dt, 0, H)
        self.cd -= dt
        self.hit_cd -= dt
        if self.cd <= 0:
            self.cd = 0.22
            g.play('buzz', 0.45)
        for b in rb:
            if self.hit_cd <= 0 and math.hypot(b.x - self.x, b.y - self.y) < 22:
                self.hit_cd = 0.7
                g.steer(b, random.choice((-1, 1)) * 650)
                g.popup(self.x, self.y - 14, 'BZZ!', (200, 200, 200), 18)

    def draw_top(self, s):
        x, y = (int(self.x), int(self.y))
        wing = int(self.g.t * 40) % 2 * 4
        pygame.draw.rect(s, (30, 30, 30), (x - 4, y - 2, 10, 8))
        pygame.draw.rect(s, (200, 220, 255), (x - 6, y - 8 - wing, 6, 6))
        pygame.draw.rect(s, (200, 220, 255), (x + 2, y - 8 - wing, 6, 6))
        pygame.draw.rect(s, (255, 60, 60), (x + 4, y - 2, 4, 4))

@reg
class Portals(Event):
    name = 'PORTALS'
    sub = "NOW YOU'RE THINKING WITH PADDLES"
    dur = 13
    group = 'world'

    def start(self):
        self.a = (random.uniform(230, 360), random.uniform(80, H - 80))
        self.b = (random.uniform(440, 570), random.uniform(80, H - 80))
        if random.random() < 0.5:
            self.a, self.b = (self.b, self.a)
        self.cool = {}

    def update(self, dt):
        g = self.g
        for k in list(self.cool):
            self.cool[k] -= dt
            if self.cool[k] <= 0:
                del self.cool[k]
        for b in g.real_balls():
            if id(b) in self.cool or b.stuck:
                continue
            for src, dst in ((self.a, self.b), (self.b, self.a)):
                if math.hypot(b.x - src[0], b.y - src[1]) < 28:
                    ang = math.atan2(b.vy, b.vx)
                    g.parts.burst(b.x, b.y, (255, 160, 0) if src is self.a else (60, 170, 255), 14, 240, 0.4)
                    b.x = dst[0] + math.cos(ang) * 44
                    b.y = clamp(dst[1] + math.sin(ang) * 44, 10, H - 10)
                    self.cool[id(b)] = 0.5
                    g.play('portal')
                    g.parts.burst(b.x, b.y, (60, 170, 255) if src is self.a else (255, 160, 0), 14, 240, 0.4)
                    break

    def draw_front(self, s):
        for (x, y), col in ((self.a, (255, 150, 0)), (self.b, (60, 170, 255))):
            x, y = (int(x), int(y))
            pygame.draw.ellipse(s, col, (x - 20, y - 36, 40, 72))
            pygame.draw.ellipse(s, tint(col, 0.45), (x - 14, y - 28, 28, 56))
            pygame.draw.ellipse(s, BLACK, (x - 8, y - 20, 16, 40))
            ph = int(self.t * 12) % 3
            pygame.draw.ellipse(s, WHITE, (x - 20 + ph * 2, y - 36 + ph * 3, 40 - ph * 4, 72 - ph * 6), 2)

@reg
class Conveyors(Event):
    name = 'CONVEYOR BELTS'
    sub = 'THE FLOOR IS MOVING (SIDEWAYS?)'
    dur = 12
    group = 'world'

    def start(self):
        self.bands = [(250, random.randint(90, 170), 300, 70, random.choice((-1, 1))), (250, random.randint(380, 450), 300, 70, random.choice((-1, 1)))]

    def update(self, dt):
        g = self.g
        for x, y, w, h, d in self.bands:
            for b in g.real_balls():
                if x < b.x < x + w and y < b.y < y + h and (not b.stuck):
                    g.steer(b, d * 1500 * g.bdt)

    def draw_front(self, s):
        for x, y, w, h, d in self.bands:
            pygame.draw.rect(s, (50, 50, 60), (x, y, w, h))
            pygame.draw.rect(s, (255, 200, 0), (x, y, w, h), 2)
            for k in range(0, h, 22):
                yy = y + (k + int(self.t * 60 * d)) % h
                pygame.draw.lines(s, (255, 200, 0), False, [(x + 60, yy - 8 * d), (x + 90, yy), (x + 120, yy - 8 * d)], 2)
                pygame.draw.lines(s, (255, 200, 0), False, [(x + 180, yy - 8 * d), (x + 210, yy), (x + 240, yy - 8 * d)], 2)

@reg
class WobblyGoals(Event):
    name = 'WOBBLY GOALS'
    sub = 'ONLY THE MOVING GAP SCORES'
    dur = 11
    group = 'goal'
    GAP = 160

    def gap(self, side):
        c = H / 2 + (H / 2 - self.GAP / 2 - 20) * math.sin(self.t * 1.1 + (0 if side < 0 else 2.2))
        return (c - self.GAP / 2, c + self.GAP / 2)

    def walls(self):
        out = []
        for side in (-1, 1):
            y0, y1 = self.gap(side)
            x = 0 if side < 0 else W - 12
            out.append((x, 0, 12, y0))
            out.append((x, y1, 12, H - y1))
        return out

    def update(self, dt):
        g = self.g
        for r in self.walls():
            for b in g.real_balls():
                if g.bounce_rect(b, r, 1.0):
                    g.play('wall', 0.6)

    def draw_front(self, s):
        for r in self.walls():
            pygame.draw.rect(s, (230, 60, 60), r)
            for k in range(0, int(r[3]), 24):
                pygame.draw.rect(s, WHITE, (r[0], r[1] + k, 12, 10))
        for side in (-1, 1):
            y0, y1 = self.gap(side)
            x = 0 if side < 0 else W - 12
            pygame.draw.rect(s, (255, 230, 0), (x, y0 - 4, 12, 4))
            pygame.draw.rect(s, (255, 230, 0), (x, y1, 12, 4))

@reg
class BananaPeels(Event):
    name = 'BANANA PEELS'
    sub = 'WATCH YOUR STEP'
    dur = 13
    group = 'ctrl'

    def start(self):
        self.peels = []
        for side in (-1, 1):
            for _ in range(3):
                self.peels.append([side, random.uniform(40, H - 60), 0.0])

    def update(self, dt):
        g = self.g
        for pl in self.peels:
            if pl[2] > 0:
                pl[2] -= dt
                if pl[2] <= 0:
                    pl[1] = random.uniform(40, H - 60)
                continue
            p = g.paddle(pl[0])
            for r in p.rects():
                if r[1] - 10 < pl[1] < r[1] + r[3] + 10:
                    p.mod(None, 'invert', 1, 1.6)
                    p.mod(None, 'slip', 1, 1.6)
                    pl[2] = 2.5
                    g.play('slip')
                    g.popup(p.x + 7, pl[1] - 20, 'SLIP!', (255, 230, 0), 22)
                    break

    def draw_front(self, s):
        g = self.g
        for side, y, cd in self.peels:
            if cd > 0:
                continue
            p = g.paddle(side)
            x = p.x + p.w // 2
            pygame.draw.polygon(s, (255, 230, 40), [(x - 22, y + 4), (x - 10, y - 14), (x + 10, y - 18), (x + 24, y - 8), (x + 8, y + 10), (x - 8, y + 12)])
            pygame.draw.polygon(s, (190, 150, 20), [(x - 22, y + 4), (x - 10, y - 14), (x + 10, y - 18), (x + 24, y - 8), (x + 8, y + 10), (x - 8, y + 12)], 2)
            pygame.draw.rect(s, (110, 70, 20), (x + 20, y - 14, 6, 6))
            pygame.draw.rect(s, (110, 70, 20), (x - 6, y - 4, 4, 4))
            pygame.draw.rect(s, (110, 70, 20), (x + 4, y - 8, 4, 4))

@reg
class Seasick(Event):
    name = 'SEASICK'
    sub = 'THE WORLD IS TILTING'
    dur = 10
    group = 'post'

    def post(self, s):
        big = pygame.transform.scale(s, (int(W * 1.16), int(H * 1.16)))
        rot = pygame.transform.rotate(big, 6.0 * math.sin(self.t * 1.7))
        out = pygame.Surface((W, H))
        out.blit(rot, (-(rot.get_width() - W) // 2, -(rot.get_height() - H) // 2))
        return out

@reg
class Heartbeat(Event):
    name = 'HEARTBEAT'
    sub = 'THUMP-THUMP'
    dur = 9
    group = 'post'

    def start(self):
        self.last = -1

    def update(self, dt):
        beat = int(self.t * 2.4)
        if beat != self.last:
            self.last = beat
            self.g.play('drum', 0.7)

    def post(self, s):
        ph = self.t * 2.4 % 1.0
        z = 1.0 + 0.14 * max(0.0, math.sin(ph * math.pi * 2)) ** 2 if ph < 0.5 else 1.0
        if z < 1.01:
            return s
        big = pygame.transform.scale(s, (int(W * z), int(H * z)))
        out = pygame.Surface((W, H))
        out.blit(big, (-(big.get_width() - W) // 2, -(big.get_height() - H) // 2))
        return out

@reg
class BoingWalls(Event):
    name = 'BOING WALLS'
    sub = 'SPRINGS EVERYWHERE'
    dur = 10
    group = 'walls'

    def on_wall(self, b):
        self.g.steer(b, random.choice((-1, 1)) * random.uniform(250, 560))
        self.g.play('boing', 0.6)

    def draw_front(self, s):
        for yy, d in ((0, 1), (H, -1)):
            pts = [(x, yy + d * (4 + i % 2 * 12)) for i, x in enumerate(range(0, W + 1, 20))]
            pygame.draw.lines(s, (120, 255, 120), False, pts, 4)

@reg
class ShrinkingCourt(Event):
    name = 'SHRINKING COURT'
    sub = 'THE WALLS ARE CLOSING IN'
    dur = 11
    group = 'world'

    def inset(self):
        return 150 * (0.5 - 0.5 * math.cos(self.t / self.dur * math.tau))

    def update(self, dt):
        g = self.g
        i = self.inset()
        if i < 4:
            return
        for r in ((70, 0, W - 140, i), (70, H - i, W - 140, i)):
            for b in g.real_balls():
                if g.bounce_rect(b, r, 1.0):
                    g.play('wall', 0.5)

    def draw_front(self, s):
        i = self.inset()
        if i < 4:
            return
        for r in ((70, 0, W - 140, i), (70, H - i, W - 140, i)):
            pygame.draw.rect(s, (120, 70, 40), r)
            for k in range(70, W - 70, 24):
                pygame.draw.rect(s, (80, 40, 20), (k, r[1], 4, r[3]))
        pygame.draw.rect(s, (255, 230, 0), (70, i - 4, W - 140, 4))
        pygame.draw.rect(s, (255, 230, 0), (70, H - i, W - 140, 4))

@reg
class SlimePit(Event):
    name = 'SLIME PIT'
    sub = 'THE BALL GETS STUCK IN THE GOO'
    dur = 12
    group = 'world'

    def start(self):
        self.pits = []
        for _ in range(3):
            self.pits.append((random.uniform(230, 570), random.uniform(80, H - 80), random.uniform(48, 70)))
        self.orig = {}

    def update(self, dt):
        g = self.g
        for b in g.real_balls():
            inside = any((math.hypot(b.x - x, b.y - y) < r for x, y, r in self.pits))
            k = id(b)
            if inside:
                if k not in self.orig:
                    self.orig[k] = b.speed()
                    g.play('splat', 0.5)
                b.set_speed(max(170.0, self.orig[k] * 0.4))
                if random.random() < 0.3:
                    g.parts.burst(b.x, b.y, (90, 255, 90), 1, 60, 0.5, 4, -40)
            elif k in self.orig:
                b.set_speed(max(self.orig.pop(k), BASE_SPEED * 0.8))

    def end(self):
        for b in self.g.real_balls():
            if id(b) in self.orig:
                b.set_speed(max(self.orig[id(b)], BASE_SPEED * 0.8))

    def draw_back(self, s):
        for x, y, r in self.pits:
            pygame.draw.circle(s, (30, 120, 40), (int(x), int(y)), int(r))
            pygame.draw.circle(s, (90, 220, 90), (int(x), int(y)), int(r), 4)
            bx = x + math.cos(self.t * 3 + x) * r * 0.5
            by = y + math.sin(self.t * 2.4 + y) * r * 0.5
            pygame.draw.circle(s, (150, 255, 150), (int(bx), int(by)), 8)

@reg
class BoostPads(Event):
    name = 'BOOST PADS'
    sub = 'TOUCH THEM. GO FASTER.'
    dur = 12
    group = 'world'

    def start(self):
        self.pads = [[random.uniform(230, 540), random.uniform(60, H - 130), 0.0] for _ in range(5)]
        self.cool = {}

    def update(self, dt):
        g = self.g
        for k in list(self.cool):
            self.cool[k] -= dt
            if self.cool[k] <= 0:
                del self.cool[k]
        for b in g.real_balls():
            for i, (x, y, _) in enumerate(self.pads):
                if (id(b), i) in self.cool:
                    continue
                if x - 8 < b.x < x + 58 and y - 8 < b.y < y + 78:
                    b.set_speed(min(MAX_SPEED * 0.92, b.speed() * 1.28))
                    self.cool[id(b), i] = 0.7
                    self.pads[i][2] = 0.3
                    g.play('powerup', 0.4)
                    g.parts.burst(b.x, b.y, (255, 230, 0), 12, 280, 0.4)
        for p_ in self.pads:
            p_[2] = max(0.0, p_[2] - dt)

    def draw_back(self, s):
        for x, y, hit in self.pads:
            pygame.draw.rect(s, (60, 50, 0) if hit <= 0 else (255, 255, 160), (x, y, 50, 70))
            pygame.draw.rect(s, (255, 230, 0), (x, y, 50, 70), 2)
            for k in range(3):
                yy = y + 52 - (k * 22 + int(self.t * 50)) % 66
                pygame.draw.lines(s, (255, 230, 0), False, [(x + 8, yy + 8), (x + 25, yy), (x + 42, yy + 8)], 4)

@reg
class PaddleRoulette(Event):
    name = 'PADDLE ROULETTE'
    sub = 'THE SIZE KEEPS CHANGING'
    dur = 12
    group = 'psize'

    def start(self):
        self.cd = 0.0

    def update(self, dt):
        self.cd -= dt
        if self.cd <= 0:
            self.cd = 1.4
            for p in self.g.paddles:
                p.unmod(self)
                v = random.choice((0.45, 0.7, 1.0, 1.5, 2.0, 2.6))
                p.mod(self, 'h', v)
                self.g.popup(p.x + (50 if p.side < 0 else -50), p.cy(), 'x%.1f' % v, (255, 230, 0), 20)
            self.g.play('coin', 0.5)

@reg
class BreathingPaddles(Event):
    name = 'BREATHING PADDLES'
    sub = 'IN... AND OUT...'
    dur = 10
    group = 'psize'

    def update(self, dt):
        for i, p in enumerate(self.g.paddles):
            p.unmod(self)
            p.mod(self, 'h', 1.0 + 0.7 * math.sin(self.t * 2.2 + i * math.pi))

@reg
class PunchingPaddles(Event):
    name = 'PUNCHING PADDLES'
    sub = 'THEY LUNGE FORWARD'
    dur = 10
    group = 'xoff'

    def update(self, dt):
        for i, p in enumerate(self.g.paddles):
            k = max(0.0, math.sin(self.t * 2.3 + i * 1.7)) ** 2
            p.xoff = -p.side * 150 * k

    def end(self):
        for p in self.g.paddles:
            p.xoff = 0
PaddleDrift.group = 'xoff'
