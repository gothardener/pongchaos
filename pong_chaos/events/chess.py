from __future__ import annotations
import math
import random
import pygame
from ..core import *
from .base import *


KN_D = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
KG_D = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
DG_D = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
OR_D = [(-1, 0), (1, 0), (0, -1), (0, 1)]
CH_VAL = {'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000}
CH_MAT = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0}
CH_START = [['r.b.k..r', 'pp..qppp', '..n..n..', '...p....', '....P...', '..N..N..', 'PPP..PPP', 'R..QK..R'], ['r...kb.r', 'ppp.qppp', '..n..n..', '...pp...', '..B.P...', '.....N..', 'PPPP.PPP', 'RNBQ.RK.'], ['..k..r..', 'pp..q.pp', '..p..p..', '...n....', '..PP....', '.Q..N...', 'PP...PPP', '..R..RK.'], ['...q.rk.', 'ppp..ppp', '........', '...b....', '...P.B..', '..P..Q..', 'PP...PPP', '...R.RK.']]
CH_SIL = {'P': ['........', '...##...', '..####..', '...##...', '..####..', '...##...', '.######.', '.######.'], 'N': ['..###...', '.#####..', '####.##.', '##..###.', '....###.', '...####.', '..#####.', '.######.'], 'B': ['...##...', '..####..', '..####..', '...##...', '..####..', '...##...', '.######.', '.######.'], 'R': ['##.##.##', '########', '.######.', '..####..', '..####..', '.######.', '########', '########'], 'Q': ['#..##..#', '##.##.##', '########', '.######.', '..####..', '..####..', '.######.', '########'], 'K': ['...##...', '.######.', '...##...', '.######.', '########', '.######.', '..####..', '########']}

def ch_pseudo(b, white):
    out = []
    for r in range(8):
        row = b[r]
        for c in range(8):
            p = row[c]
            if p == '.' or p.isupper() != white:
                continue
            k = p.upper()
            if k == 'P':
                d = -1 if white else 1
                r1 = r + d
                if 0 <= r1 < 8:
                    if b[r1][c] == '.':
                        out.append((r, c, r1, c))
                        if r == (6 if white else 1) and b[r + 2 * d][c] == '.':
                            out.append((r, c, r + 2 * d, c))
                    for dc in (-1, 1):
                        c1 = c + dc
                        if 0 <= c1 < 8:
                            q = b[r1][c1]
                            if q != '.' and q.isupper() != white:
                                out.append((r, c, r1, c1))
            elif k in 'NK':
                for dr, dc in KN_D if k == 'N' else KG_D:
                    r1, c1 = (r + dr, c + dc)
                    if 0 <= r1 < 8 and 0 <= c1 < 8:
                        q = b[r1][c1]
                        if q == '.' or q.isupper() != white:
                            out.append((r, c, r1, c1))
            else:
                for dr, dc in DG_D if k == 'B' else OR_D if k == 'R' else DG_D + OR_D:
                    r1, c1 = (r + dr, c + dc)
                    while 0 <= r1 < 8 and 0 <= c1 < 8:
                        q = b[r1][c1]
                        if q == '.':
                            out.append((r, c, r1, c1))
                        else:
                            if q.isupper() != white:
                                out.append((r, c, r1, c1))
                            break
                        r1 += dr
                        c1 += dc
    return out

def ch_attacked(b, r, c, by_white):
    P, N, B, R, Q, K = 'PNBRQK' if by_white else 'pnbrqk'
    pr = r + 1 if by_white else r - 1
    if 0 <= pr < 8:
        for dc in (-1, 1):
            if 0 <= c + dc < 8 and b[pr][c + dc] == P:
                return True
    for dr, dc in KN_D:
        r1, c1 = (r + dr, c + dc)
        if 0 <= r1 < 8 and 0 <= c1 < 8 and (b[r1][c1] == N):
            return True
    for dr, dc in KG_D:
        r1, c1 = (r + dr, c + dc)
        if 0 <= r1 < 8 and 0 <= c1 < 8 and (b[r1][c1] == K):
            return True
    for dirs, a, q2 in ((DG_D, B, Q), (OR_D, R, Q)):
        for dr, dc in dirs:
            r1, c1 = (r + dr, c + dc)
            while 0 <= r1 < 8 and 0 <= c1 < 8:
                x = b[r1][c1]
                if x != '.':
                    if x == a or x == q2:
                        return True
                    break
                r1 += dr
                c1 += dc
    return False

def ch_king(b, white):
    k = 'K' if white else 'k'
    for r in range(8):
        for c in range(8):
            if b[r][c] == k:
                return (r, c)
    return None

def ch_apply(b, m):
    r, c, r1, c1 = m
    cap, p = (b[r1][c1], b[r][c])
    b[r1][c1] = p
    b[r][c] = '.'
    if p == 'P' and r1 == 0:
        b[r1][c1] = 'Q'
    elif p == 'p' and r1 == 7:
        b[r1][c1] = 'q'
    return (cap, p)

def ch_undo(b, m, sv):
    r, c, r1, c1 = m
    b[r][c] = sv[1]
    b[r1][c1] = sv[0]

def ch_in_check(b, white):
    k = ch_king(b, white)
    return k is not None and ch_attacked(b, k[0], k[1], not white)

def ch_legal(b, white):
    out = []
    for m in ch_pseudo(b, white):
        sv = ch_apply(b, m)
        if not ch_in_check(b, white):
            out.append(m)
        ch_undo(b, m, sv)
    return out

def ch_eval(b):
    sc = 0
    for r in range(8):
        for c in range(8):
            p = b[r][c]
            if p == '.':
                continue
            k = p.upper()
            v = CH_VAL[k]
            if k != 'K':
                v += int(8 * (3.5 - abs(c - 3.5)) + 4 * (3.5 - abs(r - 3.5)))
            if k == 'P':
                v += (6 - r) * 6 if p == 'P' else (r - 1) * 6
            sc += v if p.isupper() else -v
    return sc

def ch_search(b, white, depth, alpha, beta):
    if depth == 0:
        return ch_eval(b) * (1 if white else -1)
    ms = ch_pseudo(b, white)
    if not ms:
        return 0
    ms.sort(key=lambda m: -CH_VAL.get(b[m[2]][m[3]].upper(), 0))
    best = -10 ** 6
    for m in ms:
        if b[m[2]][m[3]].upper() == 'K':
            return 100000 + depth
        sv = ch_apply(b, m)
        sc = -ch_search(b, not white, depth - 1, -beta, -alpha)
        ch_undo(b, m, sv)
        if sc > best:
            best = sc
        if best > alpha:
            alpha = best
        if alpha >= beta:
            break
    return best

def ch_best(b, white, depth, sloppy):
    ms = ch_legal(b, white)
    if not ms:
        return None
    if random.random() < sloppy:
        return random.choice(ms)
    scored = []
    for m in ms:
        sv = ch_apply(b, m)
        sc = -ch_search(b, not white, depth - 1, -10 ** 7, 10 ** 7)
        ch_undo(b, m, sv)
        scored.append((sc + random.uniform(0, 6), m))
    scored.sort(key=lambda q: -q[0])
    return scored[0][1]

def ch_material(b, white):
    return sum((CH_MAT[p.upper()] for row in b for p in row if p != '.' and p.isupper() == white))

def chess_sprite(g, ch):
    key = ('chess', ch)
    s = g.sprite_cache.get(key)
    if s is None:
        sil = CH_SIL[ch.upper()]
        white = ch.isupper()
        fill = (250, 250, 250) if white else (36, 36, 44)
        edge = (10, 10, 10) if white else (240, 240, 240)
        px = 4
        s = pygame.Surface((10 * px, 10 * px), pygame.SRCALPHA)
        cells = set(((x + 1, y + 1) for y, row in enumerate(sil) for x, c in enumerate(row) if c == '#'))
        rim = set()
        for x, y in cells:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if (x + dx, y + dy) not in cells:
                        rim.add((x + dx, y + dy))
        for x, y in rim:
            _raw_rect(s, atari(edge), (x * px, y * px, px, px))
        for x, y in cells:
            _raw_rect(s, atari(fill), (x * px, y * px, px, px))
        g.sprite_cache[key] = s
    return s

@reg
class ChessMatch(Mode):
    name = 'SUDDEN CHESS MATCH'
    sub = 'CAPTURE MORE MATERIAL! 7 SECONDS PER MOVE'
    dur = 46
    cap = 46
    limit = 40
    weight = 2.5
    hint1 = 'WASD/ARROWS MOVE CURSOR   SPACE SELECT / MOVE'
    hint2 = 'P1: WASD + SPACE    P2: ARROWS + ENTER'
    BX, BY, CS = (176, 72, 56)

    def begin(self):
        g = self.g
        self.b = [list(r) for r in random.choice(CH_START)]
        if random.random() < 0.5:
            self.b = [r[::-1] for r in self.b]
        self.white = True
        self.cur = {True: [6, 4], False: [1, 4]}
        self.sel = None
        self.moves_sel = []
        self.mv_cd = 0.0
        self.f_prev = {True: False, False: False}
        self.turn_t = 7.0
        self.ai_wait = 0.0
        self.pause = 1.4
        self.last = None
        self.check = False
        self.count = 0
        self.depth = (2, 3, 3)[g.diff]
        self.sloppy = (0.35, 0.12, 0.0)[g.diff]
        self.ended = False

    def side(self):
        return -1 if self.white else 1

    def human(self):
        return not is_cpu(self.g, self.side())

    def cell_of(self, r, c):
        return (self.BX + c * self.CS, self.BY + r * self.CS)

    def start_turn(self):
        self.turn_t = 7.0
        self.sel = None
        self.moves_sel = []
        if not self.human():
            self.ai_wait = random.uniform(0.9, 1.7)

    def do_move(self, m, auto=False):
        g = self.g
        b = self.b
        cap = b[m[2]][m[3]]
        mover_white = self.white
        sv = ch_apply(b, m)
        self.last = m
        self.count += 1
        x, y = self.cell_of(m[2], m[3])
        if cap != '.':
            g.play('capture')
            g.parts.burst(x + 28, y + 28, (255, 200, 80), 16, 300, 0.6, 5)
            g.popup(x + 28, y, '%s TAKES %s!' % (g.who(-1 if mover_white else 1), {'P': 'PAWN', 'N': 'KNIGHT', 'B': 'BISHOP', 'R': 'ROOK', 'Q': 'QUEEN', 'K': 'KING'}[cap.upper()]), (255, 230, 0), 18)
        else:
            g.play('move')
        if auto:
            g.popup(W // 2, 540, 'TIME! AUTO-MOVE', (255, 120, 120), 18)
        self.white = not self.white
        replies = ch_legal(b, self.white)
        self.check = ch_in_check(b, self.white)
        self.pause = 0.55
        if not replies:
            self.ended = True
            if self.check:
                g.play('mate')
                g.flash(WHITE, 140)
                self.award(-1 if mover_white else 1, 3, 'CHECKMATE! %s +3' % g.who(-1 if mover_white else 1))
            else:
                g.popup(W // 2, H // 2, 'STALEMATE - BOTH +1', WHITE, 26)
                g.scores[0] += 1
                g.scores[1] += 1
            self.end_soon(1.8)
            return
        if self.check:
            g.play('check')
            g.popup(W // 2, 96 + 460 // 2 - 20, 'CHECK!', (255, 80, 80), 46)
        self.start_turn()

    def on_timeout(self):
        g = self.g
        w, k = (ch_material(self.b, True), ch_material(self.b, False))
        if w != k:
            self.award(-1 if w > k else 1, 2, 'MORE MATERIAL! %s +2' % g.who(-1 if w > k else 1))
        else:
            g.popup(W // 2, H // 2, 'EQUAL MATERIAL - DRAW', WHITE, 26)

    def tick(self, dt):
        g = self.g
        if self.ended:
            return
        if self.pause > 0:
            self.pause -= dt
            if self.pause <= 0 and self.count == 0:
                self.start_turn()
            return
        self.turn_t -= dt
        if self.turn_t <= 0:
            ms = ch_legal(self.b, self.white)
            caps = [m for m in ms if self.b[m[2]][m[3]] != '.']
            self.do_move(random.choice(caps or ms), auto=True)
            return
        if not self.human():
            self.ai_wait -= dt
            if self.ai_wait <= 0:
                m = ch_best(self.b, self.white, self.depth, self.sloppy)
                if m is not None:
                    self.do_move(m)
            return
        side = self.side()
        L, R, U, D, F = human_keys(g, side)
        if g.mode == 1 and pygame.key.get_pressed()[pygame.K_RETURN]:
            F = True
        cur = self.cur[self.white]
        self.mv_cd -= dt
        if self.mv_cd <= 0 and (L or R or U or D):
            self.mv_cd = 0.12
            cur[1] = clamp(cur[1] + (1 if R else 0) - (1 if L else 0), 0, 7)
            cur[0] = clamp(cur[0] + (1 if D else 0) - (1 if U else 0), 0, 7)
            g.play('tick', 0.3)
        edge = F and (not self.f_prev[self.white])
        self.f_prev[self.white] = F
        if edge:
            r, c = cur
            p = self.b[r][c]
            if self.sel is not None and (r, c) in [(m[2], m[3]) for m in self.moves_sel]:
                mv = [m for m in self.moves_sel if (m[2], m[3]) == (r, c)][0]
                self.do_move(mv)
            elif p != '.' and p.isupper() == self.white:
                self.sel = (r, c)
                self.moves_sel = [m for m in ch_legal(self.b, self.white) if (m[0], m[1]) == (r, c)]
                g.play('beep', 0.5)
                if not self.moves_sel:
                    g.popup(W // 2, 540, "THAT PIECE CAN'T MOVE", (255, 140, 140), 15)
            else:
                self.sel = None
                self.moves_sel = []

    def draw_front(self, s):
        g = self.g
        s.fill((28, 22, 44))
        pygame.draw.rect(s, (110, 80, 50), (self.BX - 8, self.BY - 8, 8 * self.CS + 16, 8 * self.CS + 16))
        sel_to = set(((m[2], m[3]) for m in self.moves_sel))
        for r in range(8):
            for c in range(8):
                x, y = self.cell_of(r, c)
                col = (196, 222, 156) if (r + c) % 2 == 0 else (64, 118, 78)
                if self.last and (r, c) in ((self.last[0], self.last[1]), (self.last[2], self.last[3])):
                    col = (240, 240, 110) if (r + c) % 2 == 0 else (190, 190, 60)
                if self.sel == (r, c):
                    col = (110, 220, 110)
                pygame.draw.rect(s, col, (x, y, self.CS, self.CS))
                p = self.b[r][c]
                if p != '.':
                    s.blit(chess_sprite(g, p), (x + 8, y + 8))
                if (r, c) in sel_to:
                    if p != '.':
                        pygame.draw.rect(s, (255, 60, 60), (x, y, self.CS, self.CS), 4)
                    else:
                        pygame.draw.rect(s, (60, 160, 70), (x + 20, y + 20, 16, 16))
                if p in ('K', 'k') and self.check and (p.isupper() == self.white):
                    pygame.draw.rect(s, (255, 40, 40), (x, y, self.CS, self.CS), 4)
        if self.human() and (not self.ended) and (self.pause <= 0):
            r, c = self.cur[self.white]
            x, y = self.cell_of(r, c)
            col = (80, 230, 255) if self.white else (255, 110, 220)
            pygame.draw.rect(s, col, (x, y, self.CS, self.CS), 6)
        for white, x in ((True, 88), (False, 712)):
            side = -1 if white else 1
            on = self.white == white and (not self.ended)
            nm = g.who(side)
            col = (80, 230, 255) if white else (255, 110, 220)
            g.text_at(s, 'WHITE' if white else 'BLACK', x, 112, 22, WHITE)
            g.text_at(s, nm, x, 140, 22, col)
            g.text_at(s, 'MATERIAL', x, 200, 15, (170, 170, 170))
            g.text_at(s, str(ch_material(self.b, white)), x, 232, 30, WHITE)
            if on:
                g.text_at(s, 'YOUR MOVE' if self.human() else 'THINKING' + '.' * (int(g.t * 3) % 4), x, 300, 15, (255, 230, 0))
                k = clamp(self.turn_t / 7.0, 0, 1)
                pygame.draw.rect(s, (60, 60, 60), (x - 60, 322, 120, 12))
                pygame.draw.rect(s, (80, 255, 120) if k > 0.35 else (255, 80, 80), (x - 58, 324, int(116 * k), 8))
        self.hint(s, H - 52)
