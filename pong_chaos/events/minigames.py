from __future__ import annotations
import math
import random
import pygame
from ..core import *
from .base import *


def fire_side(g, key):
    if key in (pygame.K_SPACE, pygame.K_f):
        return -1
    if key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_RSHIFT, pygame.K_KP0, pygame.K_SLASH):
        return 1 if g.mode == 2 else -1
    return None

def micro_bg(s, c1=(24, 24, 60), c2=(40, 24, 80)):
    s.fill(c1)
    for y in range(0, H, 40):
        pygame.draw.rect(s, c2, (0, y, W, 20))

def vs_header(g, s, y=84):
    g.text_at(s, g.who(-1), 200, y, 22, (120, 220, 255))
    g.text_at(s, g.who(1), 600, y, 22, (255, 140, 200))
    g.text_at(s, 'VS', W // 2, y, 22, WHITE)

def draw_hand(s, kind, cx, cy, u, col, flip=1):
    if kind == 0:
        pygame.draw.circle(s, col, (cx, cy), int(u * 5))
        for k in range(4):
            pygame.draw.rect(s, tint(col, 0.7), (cx - 4 * u + k * 2 * u + u // 2, cy - 3 * u, u, 2 * u))
    elif kind == 1:
        pygame.draw.rect(s, col, (cx - 4 * u, cy - 2 * u, 8 * u, 7 * u))
        for k in range(4):
            pygame.draw.rect(s, col, (cx - 4 * u + k * 2 * u, cy - 6 * u + k % 2 * u, 2 * u - 4, 5 * u))
        pygame.draw.rect(s, col, (cx - 6 * u if flip > 0 else cx + 4 * u, cy, 2 * u, 3 * u))
    else:
        pygame.draw.rect(s, col, (cx - 3 * u, cy, 6 * u, 5 * u))
        pygame.draw.line(s, col, (cx - u, cy), (cx - 4 * u, cy - 6 * u), 2 * u)
        pygame.draw.line(s, col, (cx + u, cy), (cx + 4 * u, cy - 6 * u), 2 * u)
        pygame.draw.circle(s, (255, 230, 0), (cx, cy + 2 * u), u)

@reg
class RockPaperScissors(Mode):
    name = 'ROCK PAPER SCISSORS'
    sub = 'BEST OF 3 - PICK FAST!'
    dur = 17
    cap = 17
    limit = 15
    weight = 2.0
    hint1 = 'A = ROCK   S = PAPER   D = SCISSORS'
    hint2 = 'P1: A S D     P2: LEFT DOWN RIGHT'
    NAMES = ('ROCK', 'PAPER', 'SCISSORS')

    def begin(self):
        self.wins = [0, 0]
        self.rd = 0
        self.ph = 'count'
        self.pt = 0.0
        self.pick = [None, None]
        self.cpu_t = random.uniform(0.35, 0.9)
        self.last = None

    def beats(self, a, b):
        return (a - b) % 3 == 1

    def tick(self, dt):
        g = self.g
        self.pt += dt
        if self.ph == 'count':
            if self.pt > 2.0:
                self.ph, self.pt = ('pick', 0.0)
                self.pick = [None, None]
                self.cpu_t = random.uniform(0.35, 0.95)
                g.play('go', 0.6)
            elif int(self.pt / 0.5) != int((self.pt - dt) / 0.5):
                g.play('drum', 0.6)
        elif self.ph == 'pick':
            for side in (-1, 1):
                i = 0 if side < 0 else 1
                if self.pick[i] is not None:
                    continue
                if is_cpu(g, side):
                    if self.pt > self.cpu_t:
                        self.pick[i] = random.randrange(3)
                else:
                    L, R, U, D, F = human_keys(g, side)
                    if L:
                        self.pick[i] = 0
                    elif D:
                        self.pick[i] = 1
                    elif R:
                        self.pick[i] = 2
            if self.pick[0] is not None and self.pick[1] is not None or self.pt > 2.2:
                for i in (0, 1):
                    if self.pick[i] is None:
                        self.pick[i] = random.randrange(3)
                a, b = self.pick
                if a == b:
                    self.last = 'DRAW!'
                elif self.beats(a, b):
                    self.wins[0] += 1
                    self.last = '%s WINS THE ROUND' % g.who(-1)
                else:
                    self.wins[1] += 1
                    self.last = '%s WINS THE ROUND' % g.who(1)
                g.play('coin' if a != b else 'beep')
                self.ph, self.pt = ('show', 0.0)
        elif self.pt > 1.5:
            self.rd += 1
            if max(self.wins) >= 2 or self.rd >= 3:
                if self.wins[0] != self.wins[1]:
                    w = -1 if self.wins[0] > self.wins[1] else 1
                    self.award(w, 2 if max(self.wins) == 2 and min(self.wins) == 0 else 1)
                else:
                    self.g.popup(W / 2, H / 2, 'TIED! NOBODY WINS', WHITE, 30)
                self.end_soon(1.6)
            else:
                self.ph, self.pt = ('count', 0.0)
                self.pick = [None, None]

    def draw_front(self, s):
        g = self.g
        micro_bg(s)
        vs_header(g, s)
        g.text_at(s, 'ROUND %d' % min(3, self.rd + 1), W // 2, 130, 22, (255, 230, 0))
        g.text_at(s, '%d   -   %d' % tuple(self.wins), W // 2, 170, 46, WHITE)
        for i, cx in enumerate((200, 600)):
            col = (120, 220, 255) if i == 0 else (255, 140, 200)
            if self.ph == 'show' or (self.ph == 'pick' and self.pick[i] is not None and False):
                draw_hand(s, self.pick[i], cx, 340, 14, col, 1 if i == 0 else -1)
                g.text_at(s, self.NAMES[self.pick[i]], cx, 460, 22, col)
            else:
                shake = int(math.sin(g.t * 24) * 6) if self.ph == 'count' else 0
                draw_hand(s, 0, cx, 340 + shake, 14, tint(col, 0.6))
                if self.ph == 'pick' and self.pick[i] is not None:
                    g.text_at(s, 'LOCKED!', cx, 460, 22, col)
        if self.ph == 'count':
            word = ('ROCK...', 'PAPER...', 'SCISSORS...', 'SHOOT!')[min(3, int(self.pt / 0.5))]
            g.text_at(s, word, W // 2, 270, 46, (255, 230, 0))
        elif self.ph == 'pick':
            g.text_at(s, 'PICK NOW!', W // 2, 270, 46, (255, 80, 80) if int(g.t * 8) % 2 else WHITE)
        else:
            g.text_at(s, self.last or '', W // 2, 270, 22, (255, 230, 0))
        self.hint(s)
TYPE_WORDS = ['BANANA', 'PADDLE', 'CHAOS', 'TOASTER', 'GOBLIN', 'PICKLE', 'WIZARD', 'NOODLE', 'ROCKET', 'PIRATE', 'COOKIE', 'ZOMBIE', 'SPATULA', 'DRAGON', 'TURBO', 'MUFFIN', 'GALAXY', 'BUBBLE', 'PUDDING', 'OCTOPUS']

@reg
class TypingRace(Mode):
    name = 'TYPING RACE'
    sub = 'TYPE THE WORD FASTER THAN THE CPU'
    dur = 18
    cap = 18
    limit = 16
    weight = 2.0
    grabs_keys = True
    hint1 = 'TYPE THE LETTERS!'
    hint2 = ''

    @classmethod
    def ok(cls, g):
        return super(TypingRace, cls).ok(g) and g.mode == 1

    def begin(self):
        self.words = random.sample(TYPE_WORDS, 3)
        self.wi = 0
        self.pos = 0
        self.cpos = 0.0
        self.wins = [0, 0]
        self.pause = 1.2
        self.rate = (1.6, 2.4, 3.4)[self.g.diff]

    def on_key(self, key):
        if self.over_t is not None or self.pause > 0 or (not 97 <= key <= 122):
            return
        w = self.words[self.wi]
        if chr(key).upper() == w[self.pos]:
            self.pos += 1
            self.g.play('key')
            if self.pos >= len(w):
                self.round_end(0)
        else:
            self.g.play('uhoh', 0.4)
            self.pos = max(0, self.pos - 1)

    def round_end(self, i):
        g = self.g
        self.wins[i] += 1
        g.play('coin' if i == 0 else 'wrong')
        g.popup(W / 2, 330, '%s GOT IT!' % g.who(-1 if i == 0 else 1), (255, 230, 0), 26)
        self.wi += 1
        self.pos = 0
        self.cpos = 0.0
        self.pause = 1.3
        if self.wi >= 3 or max(self.wins) >= 2:
            if self.wins[0] != self.wins[1]:
                self.award(-1 if self.wins[0] > self.wins[1] else 1, 1)
            self.end_soon(1.3)

    def tick(self, dt):
        if self.over_t is not None:
            return
        if self.pause > 0:
            self.pause -= dt
            return
        self.cpos += dt * self.rate * random.uniform(0.6, 1.4)
        if int(self.cpos) >= len(self.words[self.wi]):
            self.round_end(1)

    def draw_front(self, s):
        g = self.g
        micro_bg(s, (10, 40, 30), (14, 56, 40))
        vs_header(g, s)
        g.text_at(s, '%d   -   %d' % tuple(self.wins), W // 2, 140, 46, WHITE)
        if self.wi < 3 and self.over_t is None:
            w = self.words[self.wi]
            x0 = W // 2 - len(w) * 36 // 2 + 18
            for i, ch in enumerate(w):
                col = (80, 255, 120) if i < self.pos else WHITE
                g.text_at(s, ch, x0 + i * 36, 280, 46, col)
            pygame.draw.rect(s, (120, 220, 255), (W // 2 - 150, 340, int(300 * self.pos / float(len(w))), 12))
            pygame.draw.rect(s, (255, 140, 200), (W // 2 - 150, 370, int(300 * min(1.0, self.cpos / len(w))), 12))
            g.text_at(s, 'YOU', W // 2 - 190, 346, 15, (120, 220, 255))
            g.text_at(s, 'CPU', W // 2 - 190, 376, 15, (255, 140, 200))
        self.hint(s)

@reg
class ButtonMash(Mode):
    name = 'BUTTON MASH'
    sub = 'MASH YOUR FIRE KEY FOR 5 SECONDS!'
    dur = 11
    cap = 11
    limit = 8.6
    weight = 2.0
    hint1 = 'MASH SPACE !!!'
    hint2 = 'P1: SPACE     P2: ENTER'

    def begin(self):
        self.n = [0, 0]
        self.go_t = 2.4
        self.rate = (5.5, 7.5, 9.5)[self.g.diff]
        self.acc = 0.0
        self.fin = False

    def on_key(self, key):
        side = fire_side(self.g, key)
        if side is not None and self.t > self.go_t and (not self.fin) and (self.over_t is None):
            self.n[0 if side < 0 else 1] += 1
            self.g.play('tick', 0.5)

    def tick(self, dt):
        g = self.g
        if self.t < self.go_t:
            if int(self.t * 1.25) != int((self.t - dt) * 1.25):
                g.play('count')
            return
        if self.t > self.go_t + 5.0 and (not self.fin):
            self.fin = True
            a, b = self.n
            if a != b:
                w = -1 if a > b else 1
                self.award(w, 2 if max(a, b) > 1.5 * min(a, b) + 2 else 1)
            self.end_soon(1.5)
            return
        if is_cpu(g, 1) and (not self.fin):
            self.acc += dt * self.rate * random.uniform(0.7, 1.3)
            while self.acc >= 1:
                self.acc -= 1
                self.n[1] += 1

    def draw_front(self, s):
        g = self.g
        micro_bg(s, (60, 20, 20), (80, 30, 20))
        vs_header(g, s)
        a, b = self.n
        tot = max(1, a + b)
        pygame.draw.rect(s, (120, 220, 255), (100, 300, int(600 * a / float(tot)), 50))
        pygame.draw.rect(s, (255, 140, 200), (100 + int(600 * a / float(tot)), 300, 600 - int(600 * a / float(tot)), 50))
        pygame.draw.rect(s, WHITE, (100, 300, 600, 50), 4)
        pygame.draw.rect(s, WHITE, (W // 2 - 2, 290, 4, 70))
        g.text_at(s, str(a), 200, 220, 70, (120, 220, 255))
        g.text_at(s, str(b), 600, 220, 70, (255, 140, 200))
        if self.t < self.go_t:
            g.text_at(s, str(int(self.go_t - self.t) + 1), W // 2, 440, 90, (255, 230, 0))
        elif not self.fin:
            left = self.go_t + 5.0 - self.t
            g.text_at(s, 'MASH!!! %.1f' % max(0, left), W // 2, 440, 46, (255, 80, 80) if int(g.t * 10) % 2 else WHITE)
        self.hint(s)

@reg
class QuickDraw(Mode):
    name = 'QUICK DRAW'
    sub = 'WAIT FOR IT... THEN FIRE!'
    dur = 17
    cap = 17
    limit = 15
    weight = 2.0
    hint1 = "PRESS SPACE ONLY AFTER 'DRAW!'"
    hint2 = 'P1: SPACE     P2: ENTER'

    def begin(self):
        self.wins = [0, 0]
        self.rd = 0
        self.ph = 'wait'
        self.pt = 0.0
        self.delay = random.uniform(1.4, 3.6)
        self.cpu_rt = random.uniform(0.32, 0.55) * (1.25, 1.0, 0.8)[self.g.diff]
        self.msg = ''
        self.fl = 0.0

    def finish_round(self, w, msg):
        g = self.g
        if self.ph == 'result':
            return
        self.ph = 'result'
        self.pt = 0.0
        self.msg = msg
        self.wins[0 if w < 0 else 1] += 1
        g.play('boom', 0.6)
        g.flash(WHITE, 120)

    def on_key(self, key):
        side = fire_side(self.g, key)
        if side is None:
            return
        if self.ph == 'wait':
            self.finish_round(-side, '%s FIRED TOO EARLY!' % self.g.who(side))
        elif self.ph == 'draw':
            self.finish_round(side, '%s IS FASTER!  %.2fs' % (self.g.who(side), self.pt))

    def tick(self, dt):
        g = self.g
        self.pt += dt
        if self.ph == 'wait' and self.pt > self.delay:
            self.ph, self.pt = ('draw', 0.0)
            g.play('go')
        elif self.ph == 'draw' and is_cpu(g, 1) and (self.pt > self.cpu_rt):
            self.finish_round(1, '%s IS FASTER!  %.2fs' % (g.who(1), self.pt))
        elif self.ph == 'result' and self.pt > 1.6:
            self.rd += 1
            if max(self.wins) >= 2 or self.rd >= 3:
                self.award(-1 if self.wins[0] > self.wins[1] else 1, 1)
                self.end_soon(1.4)
                self.ph = 'end'
            else:
                self.ph, self.pt = ('wait', 0.0)
                self.delay = random.uniform(1.4, 3.6)
                self.cpu_rt = random.uniform(0.32, 0.55) * (1.25, 1.0, 0.8)[g.diff]

    def draw_front(self, s):
        g = self.g
        draw = self.ph == 'draw'
        micro_bg(s, (120, 20, 20) if draw else (50, 40, 20), (150, 30, 30) if draw else (70, 55, 25))
        pygame.draw.rect(s, (200, 150, 70), (0, 420, W, 180))
        vs_header(g, s)
        g.text_at(s, '%d   -   %d' % tuple(self.wins), W // 2, 140, 46, WHITE)
        for cx, c, f in ((170, (120, 220, 255), 1), (630, (255, 140, 200), -1)):
            pygame.draw.rect(s, c, (cx - 24, 300, 48, 110))
            pygame.draw.rect(s, (230, 190, 140), (cx - 18, 250, 36, 40))
            pygame.draw.rect(s, (90, 50, 20), (cx - 30, 240, 60, 12))
            pygame.draw.rect(s, (90, 50, 20), (cx - 18, 232, 36, 10))
            pygame.draw.rect(s, BLACK, (cx - 8 * f, 266, 4, 4))
        if draw:
            g.text_at(s, 'DRAW!!!', W // 2, 250, 100, (255, 255, 0))
        elif self.ph == 'wait':
            g.text_at(s, 'WAIT FOR IT' + '.' * (int(g.t * 3) % 4), W // 2, 250, 46, WHITE)
        else:
            g.text_at(s, self.msg, W // 2, 250, 22, (255, 230, 0))
        self.hint(s)
