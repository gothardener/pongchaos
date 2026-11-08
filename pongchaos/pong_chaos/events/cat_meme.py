from __future__ import annotations
import math
import random
import pygame
from ..core import *
from .base import *


MEMES = [('I HAS A BAD FEELING', 'ABOUT THIS PONG'), ('MONDAYS', 'AM I RIGHT?'), ('ONE DOES NOT SIMPLY', 'BEAT THE CPU'), ('HELLO. YES. THIS IS CAT.', 'I AM IN YOUR WALLS'), ('THEY SAID I COULD BE ANYTHING', 'I CHOSE LASAGNA'), ('ME: I WILL SLEEP EARLY', 'ALSO ME: 3AM PONG'), ('CAT TAX', 'PAY UP, HUMAN'), ('WHEN THE WIFI DROPS', 'FOR 0.2 SECONDS'), ('KEEP CALM', 'AND KNOCK THE BALL OFF THE TABLE'), ('I AM FINE', '(THE ROOM IS ON FIRE)')]
FRY_SYMS = ['LOL', '100', 'OK', 'LMAO', '!!!', 'XD', 'NICE']

def outline_para(g, s, text, x, y, size, maxw, col=WHITE):
    px = text_px(size)
    adv = 6 * px
    lines = wrap_text(str(text).upper(), max(1, int(maxw // adv)))
    for i, ln in enumerate(lines):
        w_ = g.render(ln, size, col)
        b_ = g.render(ln, size, BLACK)
        xx = _sn(x + (maxw - w_.get_width()) // 2)
        yy = _sn(y + i * 9 * px)
        for ox, oy in ((-4, 0), (4, 0), (0, -4), (0, 4), (-4, -4), (4, 4), (-4, 4), (4, -4)):
            s.blit(b_, (xx + ox, yy + oy))
        s.blit(w_, (xx, yy))
    return y + len(lines) * 9 * px

def draw_meme_cat(s, cx, cy, u, mood, t, fried):
    cx, cy = (int(cx), int(cy))
    fur = (255, 120, 0) if fried else (150, 150, 162)
    dark = (200, 0, 0) if fried else (90, 90, 104)
    light = (255, 255, 0) if fried else (232, 232, 238)

    def R(dx, dy, w, h, c):
        pygame.draw.rect(s, c, (cx + dx * u, cy + dy * u, w * u, h * u))
    pygame.draw.polygon(s, fur, [(cx - 8 * u, cy - 5 * u), (cx - 8 * u, cy - 11 * u), (cx - 2 * u, cy - 6 * u)])
    pygame.draw.polygon(s, fur, [(cx + 8 * u, cy - 5 * u), (cx + 8 * u, cy - 11 * u), (cx + 2 * u, cy - 6 * u)])
    pygame.draw.polygon(s, (255, 150, 170), [(cx - 7 * u, cy - 6 * u), (cx - 7 * u, cy - 9 * u), (cx - 4 * u, cy - 6 * u)])
    pygame.draw.polygon(s, (255, 150, 170), [(cx + 7 * u, cy - 6 * u), (cx + 7 * u, cy - 9 * u), (cx + 4 * u, cy - 6 * u)])
    R(-8, -6, 16, 13, fur)
    R(-1, -6, 2, 3, dark)
    R(-4, -6, 2, 2, dark)
    R(2, -6, 2, 2, dark)
    R(-5, 1, 10, 6, light)
    if mood == 'laugh':
        for sx in (-1, 1):
            pygame.draw.lines(s, BLACK, False, [(cx + sx * 6 * u, cy - 4 * u), (cx + sx * 3 * u, cy - 2 * u), (cx + sx * 6 * u, cy)], max(4, u))
            R(sx * 5 - 1, -1 + int(t * 6) % 3, 1, 2, (80, 180, 255))
        R(-3, 3, 6, 4, (60, 0, 20))
        R(-2, 5, 4, 2, (255, 120, 140))
    elif mood == 'glare':
        for sx in (-1, 1):
            R(sx * 4 - 2, -4, 4, 3, (255, 40, 40))
            pygame.draw.line(s, BLACK, (cx + sx * 7 * u, cy - 6 * u), (cx + sx * 2 * u, cy - 4 * u), max(4, u))
        R(-3, 5, 6, 1, BLACK)
    else:
        for sx in (-1, 1):
            R(sx * 4 - 2, -4, 4, 4, WHITE)
            R(sx * 4 - 1, -4, 2, 4, (60, 220, 90))
            R(sx * 4 - 0.5, -4, 1, 4, BLACK)
        R(-3, 4, 6, 1, dark)
    R(-1, 1, 2, 1, (255, 120, 150))
    for sx in (-1, 1):
        for k in (-1, 0, 1):
            pygame.draw.line(s, WHITE, (cx + sx * 4 * u, cy + 3 * u), (cx + sx * 11 * u, cy + (2 + k * 2) * u), 2)

@reg
class CatMeme(Mode):
    name = 'FUNNY CAT MEME'
    sub = 'IT IS SUPPOSED TO BE FUNNY. THE CAT WILL JUDGE YOU.'
    dur = 26
    cap = 26
    limit = 24
    weight = 2.0
    hint1 = 'VOTE:  W = FUNNY    S = CRINGE'
    hint2 = 'P1: W / S     P2: UP / DOWN'
    T_LOAD, T_TOP, T_BOT, T_VOTE, T_VERD, T_END = (1.6, 2.8, 4.4, 8.4, 8.4, 11.0)

    def begin(self):
        n = 2 if random.random() < 0.7 else 1
        self.memes = random.sample(MEMES, n)
        self.k = 0
        self.points = [0, 0]
        self.new_meme()

    def new_meme(self):
        self.mt = 0.0
        self.vote = [None, None]
        self.vprev = [False, False]
        self.cpu_t = random.uniform(0.8, 2.8)
        self.verdict = None
        self.rim = False
        self.bgc = random.choice(((90, 140, 200), (200, 160, 90), (120, 180, 120), (180, 110, 190)))
        self.last_laugh = 0.0
        self.chars = 0

    def tick(self, dt):
        g = self.g
        self.mt += dt
        fried = self.k == 1
        top, bot = self.memes[self.k]
        if self.mt >= self.T_BOT and (not self.rim):
            self.rim = True
            g.play('rimshot')
        if self.T_BOT <= self.mt < self.T_VOTE:
            if self.mt - self.last_laugh > 0.55:
                self.last_laugh = self.mt
                g.play('laugh', 0.35)
            for side in (-1, 1):
                i = 0 if side < 0 else 1
                if self.vote[i] is not None:
                    continue
                if is_cpu(g, side):
                    if self.mt - self.T_BOT > self.cpu_t:
                        self.vote[i] = 1 if random.random() < 0.55 else 0
                else:
                    L, R, U, D, F = human_keys(g, side)
                    if U or D:
                        self.vote[i] = 1 if U else 0
                        g.play('pop', 0.6)
        if self.mt >= self.T_VERD and self.verdict is None:
            self.verdict = random.random() < (0.5, 0.72)[min(1, self.k)]
            g.play('laugh' if self.verdict else 'wrong')
            g.flash(GOLD if self.verdict else (90, 90, 90), 70)
            for i in (0, 1):
                if self.vote[i] is not None and bool(self.vote[i]) == self.verdict:
                    g.scores[i] += 1
                    g.popup(250 if i == 0 else 550, 470, '%s +1' % g.who(-1 if i == 0 else 1), GOLD, 26)
                    g.play('coin', 0.6)
        if self.mt >= self.T_END:
            self.k += 1
            if self.k >= len(self.memes):
                self.end_soon(0.2)
            else:
                g.play('stinger')
                self.new_meme()

    def draw_front(self, s):
        g = self.g
        t = g.t
        k = min(self.k, len(self.memes) - 1)
        fried = k == 1 and len(self.memes) > 1
        top, bot = self.memes[k]
        s.fill((20, 20, 30))
        jx = random.randint(-4, 4) if fried else 0
        jy = random.randint(-4, 4) if fried else 0
        px_, py_, pw, ph = (130 + jx, 84 + jy, 540, 420)
        if self.mt < self.T_LOAD:
            g.text_at(s, 'BUFFERING MEME... %d%%' % min(99, int(self.mt / self.T_LOAD * 99)), W // 2, 280, 22, WHITE)
            for i in range(8):
                a = t * 6 + i * math.tau / 8
                pygame.draw.rect(s, WHITE if i == int(t * 8) % 8 else (90, 90, 100), (W // 2 + math.cos(a) * 40 - 4, 340 + math.sin(a) * 40 - 4, 8, 8))
            return
        pygame.draw.rect(s, WHITE, (px_ - 6, py_ - 6, pw + 12, ph + 12))
        ps = pygame.Surface((pw, ph))
        ps.fill((255, 220, 0) if fried else self.bgc)
        if fried:
            cxx, cyy = (pw // 2, ph // 2)
            for i in range(18):
                a0 = i * math.tau / 18 + t * 0.6
                a1 = a0 + math.tau / 36
                pygame.draw.polygon(ps, (255, 40, 0), [(cxx, cyy), (cxx + math.cos(a0) * 420, cyy + math.sin(a0) * 420), (cxx + math.cos(a1) * 420, cyy + math.sin(a1) * 420)])
        mood = 'neutral'
        if self.verdict is not None:
            mood = 'laugh' if self.verdict else 'glare'
        u = 14 if self.verdict is None else 14 + int(math.sin(t * 10) * 1)
        draw_meme_cat(ps, pw // 2, ph // 2 + 20, u, mood, t, fried)
        if fried:
            for q_ in range(6):
                rr = random.Random(q_ + int(t * 3))
                g.text_at(ps, rr.choice(FRY_SYMS), rr.randint(30, pw - 30), rr.randint(60, ph - 60), 22, (255, 255, 0))
            if mood == 'glare':
                pygame.draw.line(ps, (255, 0, 0), (pw // 2 - 56, ph // 2 + 24), (0, 60), 6)
                pygame.draw.line(ps, (255, 0, 0), (pw // 2 + 56, ph // 2 + 24), (pw, 60), 6)
        s.blit(ps, (_sn(px_), _sn(py_)))
        if self.mt >= self.T_LOAD:
            n_top = int(clamp((self.mt - self.T_LOAD) / (self.T_TOP - self.T_LOAD), 0, 1) * len(top))
            outline_para(g, s, top[:n_top], px_ + 20, py_ + 14, 30, pw - 40)
        if self.mt >= self.T_TOP:
            n_bot = int(clamp((self.mt - self.T_TOP) / (self.T_BOT - self.T_TOP), 0, 1) * len(bot))
            nl = len(wrap_text(bot.upper(), (pw - 40) // 24))
            outline_para(g, s, bot[:n_bot], px_ + 20, py_ + ph - 14 - (nl * 36 - 8), 30, pw - 40)
        by = 514
        for i, (x, lab, c) in enumerate(((110, '[W] FUNNY', (50, 170, 70)), (410, '[S] CRINGE', (200, 60, 60)))):
            pygame.draw.rect(s, c, (x, by, 280, 40))
            pygame.draw.rect(s, WHITE, (x, by, 280, 40), 2)
            g.text_at(s, lab, x + 140, by + 20, 22, WHITE)
        if self.T_BOT <= self.mt < self.T_VOTE:
            g.text_at(s, 'RATE THE MEME!  %d' % (int(self.T_VOTE - self.mt) + 1), W // 2, 62, 22, (255, 230, 0))
        for i in (0, 1):
            v = self.vote[i]
            if v is not None and (self.verdict is not None or i == 0 or g.mode == 2 or True):
                if self.verdict is not None or self.mt >= self.T_VOTE or v is not None:
                    show = self.verdict is not None
                    x = (110 if v else 410) + 20 + i * 150
                    pygame.draw.rect(s, (120, 220, 255) if i == 0 else (255, 140, 200), (x, by + 44, 100, 16))
                    g.text_at(s, g.who(-1 if i == 0 else 1)[:6] if show else 'LOCKED', x + 50, by + 52, 15, BLACK)
        if self.verdict is not None:
            g.text_at(s, 'THE CAT LAUGHED!' if self.verdict else 'THE CAT IS UNIMPRESSED', W // 2, 62, 22, GOLD if self.verdict else (200, 200, 200))
        if self.mt < self.T_BOT and self.mt > self.T_LOAD and False:
            self.hint(s)
