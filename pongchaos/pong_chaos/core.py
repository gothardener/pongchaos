import array
import colorsys
import math
import random
import sys
from collections import deque
from functools import lru_cache
import pygame
W, H = (800, 600)
FPS = 60
WIN_SCORE = 7
BALL_BASE = 14
BASE_SPEED = 380.0
MAX_SPEED = 1000.0
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
BANNER_COLORS = [(255, 230, 0), (0, 255, 255), (255, 90, 200), (130, 255, 90), (255, 150, 0), (170, 130, 255)]

def clamp(v, a, b):
    return a if v < a else b if v > b else v

def hsv(h, s=1.0, v=1.0):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))

def tint(c, k):
    return (clamp(int(c[0] * k), 0, 255), clamp(int(c[1] * k), 0, 255), clamp(int(c[2] * k), 0, 255))

def rect_hit(a, b):
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and (a[1] < b[1] + b[3]) and (b[1] < a[1] + a[3])

def circle_rect(cx, cy, r, rc):
    nx = clamp(cx, rc[0], rc[0] + rc[2])
    ny = clamp(cy, rc[1], rc[1] + rc[3])
    return (cx - nx) ** 2 + (cy - ny) ** 2 < r * r

def sign(v):
    return 1 if v >= 0 else -1

@lru_cache(maxsize=None)
def _atari_rgb(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    if s < 0.2:
        k = int(round(v * 7) / 7.0 * 255)
        return (k, k, k)
    h = round(h * 15) % 15 / 15.0
    v = max(1, round(v * 7)) / 7.0
    r2, g2, b2 = colorsys.hsv_to_rgb(h, 0.78, v)
    return (int(r2 * 255), int(g2 * 255), int(b2 * 255))

def atari(c):
    c = tuple(c)
    if len(c) > 3:
        return _atari_rgb(int(c[0]), int(c[1]), int(c[2])) + (int(c[3]),)
    return _atari_rgb(int(c[0]), int(c[1]), int(c[2]))
GRID = 2

def _sn(v):
    return int(round(v / float(GRID))) * GRID

def _ew(width):
    return max(GRID, (int(width) + 1) // 2 * 2)
_raw_rect = pygame.draw.rect
_raw_circle = pygame.draw.circle
_raw_ellipse = pygame.draw.ellipse
_raw_polygon = pygame.draw.polygon
_raw_line = pygame.draw.line
_raw_lines = pygame.draw.lines

def _snap_box(rect):
    x, y, w, h = rect
    x0, y0 = (_sn(x), _sn(y))
    x1, y1 = (_sn(x + w), _sn(y + h))
    if x1 - x0 < GRID:
        x1 = x0 + GRID
    if y1 - y0 < GRID:
        y1 = y0 + GRID
    return (x0, y0, x1 - x0, y1 - y0)

def _w_rect(surf, color, rect, width=0, **kw):
    box = _snap_box(rect)
    if width:
        width = _ew(width)
        if width * 2 > min(box[2], box[3]):
            width = 0
    return _raw_rect(surf, atari(color), box, width)

def _w_ellipse(surf, color, rect, width=0):
    box = _snap_box(rect)
    if width:
        width = _ew(width)
        if width * 2 > min(box[2], box[3]):
            width = 0
    return _raw_ellipse(surf, atari(color), box, width)

def _w_circle(surf, color, center, radius, width=0, **kw):
    radius = max(2, int(radius))
    if width:
        width = _ew(width)
        if width >= radius:
            width = 0
    return _raw_circle(surf, atari(color), (int(center[0]), int(center[1])), radius, width)

def _w_polygon(surf, color, points, width=0):
    if width:
        width = _ew(width)
    return _raw_polygon(surf, atari(color), points, width)

def _w_line(surf, color, a, b, width=1):
    return _raw_line(surf, atari(color), a, b, _ew(width))

def _w_lines(surf, color, closed, points, width=1):
    return _raw_lines(surf, atari(color), closed, points, _ew(width))
pygame.draw.rect = _w_rect
pygame.draw.ellipse = _w_ellipse
pygame.draw.circle = _w_circle
pygame.draw.polygon = _w_polygon
pygame.draw.line = _w_line
pygame.draw.lines = _w_lines
_FR = {'A': '.###. #...# #...# ##### #...# #...# #...#', 'B': '####. #...# #...# ####. #...# #...# ####.', 'C': '.###. #...# #.... #.... #.... #...# .###.', 'D': '####. #...# #...# #...# #...# #...# ####.', 'E': '##### #.... #.... ####. #.... #.... #####', 'F': '##### #.... #.... ####. #.... #.... #....', 'G': '.###. #...# #.... #.### #...# #...# .###.', 'H': '#...# #...# #...# ##### #...# #...# #...#', 'I': '.###. ..#.. ..#.. ..#.. ..#.. ..#.. .###.', 'J': '..### ...#. ...#. ...#. ...#. #..#. .##..', 'K': '#...# #..#. #.#.. ##... #.#.. #..#. #...#', 'L': '#.... #.... #.... #.... #.... #.... #####', 'M': '#...# ##.## #.#.# #.#.# #...# #...# #...#', 'N': '#...# ##..# #.#.# #..## #...# #...# #...#', 'O': '.###. #...# #...# #...# #...# #...# .###.', 'P': '####. #...# #...# ####. #.... #.... #....', 'Q': '.###. #...# #...# #...# #.#.# #..#. .##.#', 'R': '####. #...# #...# ####. #.#.. #..#. #...#', 'S': '.#### #.... #.... .###. ....# ....# ####.', 'T': '##### ..#.. ..#.. ..#.. ..#.. ..#.. ..#..', 'U': '#...# #...# #...# #...# #...# #...# .###.', 'V': '#...# #...# #...# #...# #...# .#.#. ..#..', 'W': '#...# #...# #...# #.#.# #.#.# ##.## #...#', 'X': '#...# #...# .#.#. ..#.. .#.#. #...# #...#', 'Y': '#...# #...# .#.#. ..#.. ..#.. ..#.. ..#..', 'Z': '##### ....# ...#. ..#.. .#... #.... #####', '0': '.###. #...# #..## #.#.# ##..# #...# .###.', '1': '..#.. .##.. ..#.. ..#.. ..#.. ..#.. .###.', '2': '.###. #...# ....# ...#. ..#.. .#... #####', '3': '####. ....# ....# .###. ....# ....# ####.', '4': '...#. ..##. .#.#. #..#. ##### ...#. ...#.', '5': '##### #.... ####. ....# ....# #...# .###.', '6': '.###. #.... #.... ####. #...# #...# .###.', '7': '##### ....# ...#. ..#.. .#... .#... .#...', '8': '.###. #...# #...# .###. #...# #...# .###.', '9': '.###. #...# #...# .#### ....# ....# .###.', '!': '..#.. ..#.. ..#.. ..#.. ..#.. ..... ..#..', '?': '.###. #...# ....# ...#. ..#.. ..... ..#..', '.': '..... ..... ..... ..... ..... .##.. .##..', ',': '..... ..... ..... ..... ..##. ..#.. .#...', ':': '..... ..#.. ..#.. ..... ..#.. ..#.. .....', ';': '..... ..#.. ..#.. ..... ..#.. ..#.. .#...', '-': '..... ..... ..... ##### ..... ..... .....', '+': '..... ..#.. ..#.. ##### ..#.. ..#.. .....', "'": '..#.. ..#.. .#... ..... ..... ..... .....', '"': '.#.#. .#.#. .#.#. ..... ..... ..... .....', '/': '....# ....# ...#. ..#.. .#... #.... #....', '%': '##..# ##..# ...#. ..#.. .#... #..## #..##', '(': '...#. ..#.. .#... .#... .#... ..#.. ...#.', ')': '.#... ..#.. ...#. ...#. ...#. ..#.. .#...', '>': '#.... .#... ..#.. ...#. ..#.. .#... #....', '<': '....# ...#. ..#.. .#... ..#.. ...#. ....#', '=': '..... ..... ##### ..... ##### ..... .....', '*': '..#.. #.#.# .###. #.#.# ..#.. ..... .....', '#': '.#.#. .#.#. ##### .#.#. ##### .#.#. .#.#.', '&': '.##.. #..#. #.#.. .#... #.#.# #..#. .##.#', '$': '..#.. .#### #.#.. .###. ..#.# ####. ..#..', '_': '..... ..... ..... ..... ..... ..... #####', '[': '.###. .#... .#... .#... .#... .#... .###.', ']': '.###. ...#. ...#. ...#. ...#. ...#. .###.', '@': '.###. #...# #.### #.#.# #.### #.... .####', '^': '..#.. .#.#. #...# ..... ..... ..... .....', ' ': '..... ..... ..... ..... ..... ..... .....'}
_F = {k: ''.join(('1' if c == '#' else '0' for c in v.replace(' ', ''))) for k, v in _FR.items()}

def text_px(size):
    for lim, px in ((22, 2), (38, 4), (60, 6), (100, 8), (130, 12)):
        if size <= lim:
            return px
    return 14

def wrap_text(text, maxc):
    if len(text) <= maxc:
        return [text]
    words = text.split(' ')
    lines, cur = ([], '')
    for w_ in words:
        if cur and len(cur) + 1 + len(w_) > maxc:
            lines.append(cur)
            cur = w_
        else:
            cur = cur + ' ' + w_ if cur else w_
    if cur:
        lines.append(cur)
    return lines

def draw_digits(surf, txt, cx, y, px, color):
    adv = 6 * px
    total_w = len(txt) * adv - px
    x = cx - total_w // 2
    for ch in txt:
        pat = _F['O' if ch == '0' else ch]
        for i, c in enumerate(pat):
            if c == '1':
                pygame.draw.rect(surf, color, (x + i % 5 * px, y + i // 5 * px, px, px))
        x += adv
INV1 = ['00100000100', '00010001000', '00111111100', '01101110110', '11111111111', '10111111101', '10100000101', '00011011000']
INV2 = ['00100000100', '10010001001', '10111111101', '11101110111', '11111111111', '01111111110', '00100000100', '01000000010']

__all__ = ['BALL_BASE', 'BANNER_COLORS', 'BASE_SPEED', 'BLACK', 'FPS', 'GOLD', 'GRID', 'H', 'INV1', 'INV2', 'MAX_SPEED', 'W', 'WHITE', 'WIN_SCORE', '_F', '_FR', '_atari_rgb', '_ew', '_raw_circle', '_raw_ellipse', '_raw_line', '_raw_lines', '_raw_polygon', '_raw_rect', '_sn', '_snap_box', '_w_circle', '_w_ellipse', '_w_line', '_w_lines', '_w_polygon', '_w_rect', 'array', 'atari', 'circle_rect', 'clamp', 'colorsys', 'deque', 'draw_digits', 'hsv', 'lru_cache', 'math', 'pygame', 'random', 'rect_hit', 'sign', 'sys', 'text_px', 'tint', 'wrap_text']
