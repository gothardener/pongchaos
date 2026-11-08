from __future__ import annotations
import array
import math
import random
import pygame
from .core import *

RATE = 44100

def synth(f0, f1, dur, wave='square', vol=0.3, decay=1.5, vib=0.0):
    if wave in ('sine', 'saw'):
        wave = 'square'
    elif wave == 'tri':
        wave = 'pulse'
    vib = vib * 0.5
    n = max(1, int(RATE * dur))
    buf = array.array('h')
    phase = 0.0
    nv = 0.0
    last = -1
    att = RATE * 0.003
    for i in range(n):
        t = i / n
        f = f0 + (f1 - f0) * t
        if vib:
            f *= 1 + 0.04 * math.sin(i / RATE * math.tau * vib)
        phase += f / RATE
        p = phase % 1.0
        if wave == 'square':
            v = 1.0 if p < 0.5 else -1.0
        elif wave == 'pulse':
            v = 1.0 if p < 0.25 else -1.0
        elif wave == 'saw':
            v = 2 * p - 1
        elif wave == 'tri':
            v = 4 * abs(p - 0.5) - 1
        elif wave == 'sine':
            v = math.sin(math.tau * p)
        else:
            if int(phase) != last:
                last = int(phase)
                nv = random.uniform(-1, 1)
            v = nv
        env = (1 - t) ** decay if decay else 1.0
        a = min(1.0, i / att)
        buf.append(int(32767 * round(vol * v * env * a * 15) / 15.0))
    return buf

def seq(freqs, note_dur, wave='square', vol=0.25, decay=0.8):
    out = array.array('h')
    for f in freqs:
        if f == 0:
            out.extend(array.array('h', [0]) * int(RATE * note_dur))
        else:
            out.extend(synth(f, f, note_dur, wave, vol, decay))
    return out

def mix(a, b):
    n = max(len(a), len(b))
    out = array.array('h', [0]) * n
    for i in range(len(a)):
        out[i] = a[i]
    for i in range(len(b)):
        out[i] = clamp(out[i] + b[i], -32767, 32767)
    return out

def note(n):
    return 440.0 * 2 ** ((n - 69) / 12.0)

class Sfx:

    def __init__(self):
        self.enabled = False
        self.sounds = {}
        self.sfx_on = True
        self.music_on = True
        self.music = None
        self.mood = 'calm'
        self.tracks = {}
        self.channels = 1
        global RATE
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 1, 512)
            info = pygame.mixer.get_init()
            if info:
                RATE = info[0]
                self.channels = info[2]
                pygame.mixer.set_num_channels(24)
                self.enabled = True
        except Exception:
            self.enabled = False
        if self.enabled:
            try:
                self.build()
            except Exception as e:
                print('sound disabled:', e)
                self.enabled = False

    def mk(self, buf):
        if self.channels == 2:
            st = array.array('h', [0]) * (len(buf) * 2)
            st[0::2] = buf
            st[1::2] = buf
            buf = st
        return pygame.mixer.Sound(buffer=buf.tobytes())

    def build(self):
        S = self.sounds
        mk = self.mk
        S['hit'] = mk(synth(459, 459, 0.07, 'square', 0.3, 0))
        S['wall'] = mk(synth(226, 226, 0.07, 'square', 0.3, 0))
        S['score'] = mk(synth(490, 490, 0.45, 'square', 0.3, 0.6))
        S['count'] = mk(synth(660, 660, 0.1, 'square', 0.25, 0.4))
        S['go'] = mk(synth(1320, 1320, 0.35, 'square', 0.25, 1))
        S['event'] = mk(seq([523, 659, 784, 1047, 1319], 0.055, 'pulse', 0.25))
        S['event2'] = mk(seq([880, 740, 622, 523, 392], 0.06, 'saw', 0.18))
        S['event3'] = mk(seq([392, 523, 392, 659, 392, 784], 0.05, 'square', 0.2))
        S['warn'] = mk(seq([1800, 0, 1800], 0.07, 'square', 0.18))
        S['laser'] = mk(mix(synth(3200, 150, 0.35, 'saw', 0.28, 1.2), synth(9000, 400, 0.3, 'noise', 0.15, 1.5)))
        S['tick'] = mk(synth(900, 900, 0.03, 'square', 0.2, 0))
        S['boom'] = mk(mix(synth(3000, 60, 0.7, 'noise', 0.5, 1.8), synth(120, 40, 0.5, 'sine', 0.5, 1)))
        S['zombie'] = mk(synth(95, 55, 0.6, 'saw', 0.28, 0.8, 7))
        S['splat'] = mk(synth(1200, 100, 0.15, 'noise', 0.4, 1.5))
        S['waka1'] = mk(synth(300, 520, 0.09, 'tri', 0.35, 0.3))
        S['waka2'] = mk(synth(520, 300, 0.09, 'tri', 0.35, 0.3))
        S['pacdeath'] = mk(synth(900, 100, 0.5, 'sine', 0.35, 0.5, 9))
        S['eat'] = mk(synth(200, 900, 0.12, 'square', 0.25, 1))
        S['coin'] = mk(seq([988, 1319], 0.08, 'pulse', 0.25, 0.5))
        S['powerup'] = mk(seq([392, 494, 587, 784, 988, 1175, 1568], 0.045, 'square', 0.22, 0.4))
        S['zap'] = mk(mix(synth(7000, 400, 0.22, 'noise', 0.35, 1.5), synth(1500, 200, 0.2, 'saw', 0.2, 1)))
        S['freeze'] = mk(synth(2400, 600, 0.35, 'sine', 0.3, 1, 30))
        S['whoosh'] = mk(synth(300, 3500, 0.3, 'noise', 0.28, 1.3))
        S['pop'] = mk(synth(700, 180, 0.09, 'sine', 0.4, 1))
        S['rewind'] = mk(synth(200, 2600, 0.7, 'saw', 0.22, 0.4, 20))
        S['timestop'] = mk(synth(900, 40, 0.9, 'tri', 0.4, 0.6))
        S['ufo'] = mk(synth(420, 820, 0.9, 'sine', 0.3, 0.3, 12))
        S['bump'] = mk(synth(300, 700, 0.09, 'pulse', 0.35, 1))
        S['thunder'] = mk(mix(synth(6000, 80, 0.9, 'noise', 0.55, 1.6), synth(70, 35, 0.8, 'sine', 0.5, 1)))
        S['shoot'] = mk(synth(1400, 300, 0.1, 'pulse', 0.22, 1))
        S['glitch'] = mk(synth(2500, 2500, 0.14, 'noise', 0.3, 0.2))
        S['uhoh'] = mk(seq([392, 330, 262], 0.12, 'square', 0.25, 0.5))
        S['win'] = mk(seq([523, 659, 784, 1047, 784, 1047, 1319, 0, 1319, 1568], 0.1, 'pulse', 0.28, 0.5))
        S['beep'] = mk(synth(1000, 1100, 0.05, 'square', 0.2, 0.2))
        chords = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [48, 52, 55]), (55, [55, 59, 62])]
        bass = array.array('h')
        lead = array.array('h')
        for root, tri in chords:
            for _ in range(8):
                bass.extend(synth(note(root - 24), note(root - 24), 0.125, 'tri', 0.3, 1.2))
            for k in range(16):
                n_ = tri[k % 3] + (12 if k // 3 % 2 else 0)
                lead.extend(synth(note(n_ + 12), note(n_ + 12), 0.0625, 'pulse', 0.045, 1.5))
        self.music = self.mk(mix(bass, lead))
        self.music.set_volume(0.35)
        self.tracks = {'calm': [self.music], 'good': [], 'evil': []}
        P16 = [0, 1, 2, 1] * 4
        self.tracks['good'].append(self.track([(48, [48, 52, 55]), (43, [43, 47, 50]), (45, [45, 48, 52]), (41, [41, 45, 48])], 0.0625, P16, 'square', 24))
        self.tracks['good'].append(self.track([(60, [60, 64, 67, 72]), (55, [55, 59, 62, 67]), (57, [57, 60, 64, 69]), (53, [53, 57, 60, 65])], 0.05, [0, 1, 2, 3, 2, 1, 0, 1] * 2, 'pulse', 0))
        self.tracks['good'].append(self.track([(50, [50, 54, 57]), (57, [57, 61, 64]), (50, [50, 54, 57]), (55, [55, 59, 62])], 0.07, [0, 2, 1, 2] * 4, 'square', 12))
        self.tracks['evil'].append(self.track([(45, [45, 48, 51]), (44, [44, 47, 50]), (41, [41, 44, 47]), (40, [40, 43, 46])], 0.09, [0, 1, 2, 1, 0, 2, 1, 2] * 2, 'square', 12, True))
        self.tracks['evil'].append(self.track([(48, [48, 49, 54]), (47, [47, 48, 53]), (46, [46, 47, 52]), (45, [45, 46, 51])], 0.045, [0, 2, 1, 2, 0, 2, 1, 2, 0, 2, 1, 2, 0, 1, 2, 1], 'pulse', 12, True))
        self.tracks['evil'].append(self.track([(36, [48, 51, 54]), (36, [48, 51, 54]), (39, [51, 54, 57]), (34, [46, 49, 52])], 0.11, [0, 1, 2, 1] * 4, 'square', 24, True, 12))
        self.build_extra()

    def build_extra(self):
        S = self.sounds
        mk = self.mk

        def cat(*bufs):
            out = array.array('h')
            for b_ in bufs:
                out.extend(b_)
            return out
        S['blip_y'] = mk(synth(540, 540, 0.03, 'square', 0.22, 0))
        S['blip_c'] = mk(synth(300, 300, 0.03, 'pulse', 0.24, 0))
        S['blip_g'] = mk(synth(150, 120, 0.045, 'square', 0.26, 0))
        S['blip_n'] = mk(synth(800, 800, 0.025, 'pulse', 0.18, 0))
        S['cackle'] = mk(seq([392, 311, 392, 311, 392, 330, 262], 0.07, 'square', 0.22, 0.6))
        S['notify'] = mk(seq([1319, 1760], 0.06, 'pulse', 0.22, 0.5))
        S['error'] = mk(seq([330, 0, 247], 0.1, 'square', 0.28, 0.4))
        S['ring'] = mk(seq([880, 1047, 880, 1047, 0, 0, 880, 1047, 880, 1047], 0.04, 'pulse', 0.24, 0.3))
        S['buzz'] = mk(synth(190, 210, 0.12, 'square', 0.12, 0, 60))
        S['meow'] = mk(cat(synth(500, 950, 0.12, 'pulse', 0.24, 0.3), synth(950, 520, 0.2, 'pulse', 0.24, 1.2)))
        S['squawk'] = mk(synth(1000, 420, 0.28, 'square', 0.24, 0.8, 40))
        S['honk'] = mk(mix(synth(220, 220, 0.3, 'square', 0.25, 0.3), synth(277, 277, 0.3, 'square', 0.2, 0.3)))
        S['cluck'] = mk(seq([740, 520, 740, 0, 740], 0.04, 'pulse', 0.24, 0.4))
        S['quack'] = mk(cat(synth(520, 340, 0.1, 'square', 0.26, 0.5), synth(340, 300, 0.06, 'square', 0.2, 1)))
        S['move'] = mk(mix(synth(1400, 300, 0.05, 'noise', 0.35, 2), synth(190, 130, 0.06, 'square', 0.3, 1)))
        S['capture'] = mk(mix(synth(2400, 120, 0.16, 'noise', 0.5, 1.5), synth(130, 60, 0.16, 'square', 0.4, 1)))
        S['check'] = mk(seq([880, 1175, 880, 1175], 0.06, 'pulse', 0.25, 0.4))
        S['mate'] = mk(seq([523, 392, 330, 262, 196], 0.12, 'square', 0.28, 0.4))
        S['right'] = mk(seq([523, 659, 784, 1047], 0.07, 'pulse', 0.28, 0.5))
        S['wrong'] = mk(seq([233, 208, 185, 156], 0.1, 'square', 0.28, 0.5))
        S['drum'] = mk(mix(synth(180, 50, 0.1, 'square', 0.4, 1.2), synth(3000, 500, 0.05, 'noise', 0.2, 2)))
        S['cash'] = mk(seq([1568, 2093], 0.07, 'pulse', 0.26, 0.5))
        S['sneeze'] = mk(mix(synth(2600, 400, 0.4, 'noise', 0.5, 0.8), synth(900, 200, 0.3, 'square', 0.2, 1)))
        S['boing'] = mk(cat(synth(180, 620, 0.1, 'pulse', 0.3, 0.2), synth(620, 160, 0.18, 'pulse', 0.3, 1, 30)))
        S['slip'] = mk(synth(1600, 180, 0.3, 'square', 0.25, 1, 24))
        S['portal'] = mk(synth(300, 1700, 0.2, 'pulse', 0.25, 0.6, 25))
        S['nyan'] = mk(seq([784, 988, 1175, 988, 784, 1175, 1319, 1175, 988, 1175, 1319, 1568], 0.07, 'pulse', 0.24, 0.4))
        S['vac'] = mk(synth(140, 150, 0.25, 'noise', 0.2, 0.3, 20))
        S['key'] = mk(synth(1800, 1800, 0.018, 'square', 0.16, 0))
        S['stinger'] = mk(seq([262, 277, 262, 277, 262, 277], 0.06, 'square', 0.3, 0.2))
        S['flip'] = mk(seq([1047, 1319, 1047, 1319, 1047], 0.05, 'pulse', 0.22, 0.3))
        S['shotgun'] = mk(mix(synth(1800, 80, 0.25, 'noise', 0.55, 1.2), synth(120, 40, 0.25, 'square', 0.45, 1)))
        S['fball'] = mk(synth(300, 900, 0.25, 'pulse', 0.25, 0.6, 20))
        S['dmg'] = mk(mix(synth(320, 90, 0.2, 'square', 0.4, 1), synth(900, 100, 0.15, 'noise', 0.3, 1)))
        S['xpstart'] = mk(seq([523, 659, 784, 1047, 988, 784, 1047, 1319], 0.11, 'pulse', 0.24, 0.5))
        S['xperr'] = mk(seq([740, 494], 0.1, 'square', 0.3, 0.4))
        S['click'] = mk(synth(1500, 900, 0.02, 'square', 0.2, 0))
        S['rimshot'] = mk(cat(synth(180, 60, 0.07, 'square', 0.4, 1), synth(150, 50, 0.07, 'square', 0.4, 1), synth(3000, 500, 0.22, 'noise', 0.4, 1)))
        S['laugh'] = mk(seq([784, 659, 784, 659, 784, 659, 784], 0.06, 'pulse', 0.2, 0.4))
        self.tracks['quiz'] = [self.track([(60, [60, 64, 67, 72]), (55, [55, 59, 62, 67]), (57, [57, 60, 64, 69]), (53, [53, 57, 60, 65])], 0.06, [0, 1, 2, 3, 3, 2, 1, 0, 2, 3, 2, 1, 0, 1, 2, 3], 'pulse', 12, True, 24)]
        self.tracks['spooky'] = [self.track([(45, [45, 48, 52]), (44, [44, 47, 51]), (41, [41, 44, 48]), (40, [40, 44, 47])], 0.12, [0, 2, 1, 2, 0, 2, 1, 2, 0, 1, 2, 1, 0, 2, 1, 2], 'pulse', 12, False, 24)]
        self.tracks['chess'] = [self.track([(50, [50, 53, 57]), (46, [46, 50, 53]), (43, [43, 46, 50]), (45, [45, 49, 52])], 0.1, [0, 1, 2, 1, 0, 2, 1, 2, 0, 1, 2, 1, 2, 1, 0, 1], 'square', 12, False, 24)]

    def track(self, bars, step, pat, lw, lead_oct, noise=False, bass_oct=24):
        bass = array.array('h')
        lead = array.array('h')
        hits = array.array('h')
        for root, ch in bars:
            for k in range(8):
                bass.extend(synth(note(root - bass_oct), note(root - bass_oct), step * 2, 'pulse', 0.3, 1.0))
            for k in range(16):
                n_ = ch[pat[k] % len(ch)] + lead_oct
                lead.extend(synth(note(n_), note(n_), step, lw, 0.05, 1.5))
                if noise and k % 4 == 0:
                    hits.extend(synth(8000, 2000, step, 'noise', 0.1, 2))
                elif noise:
                    hits.extend(array.array('h', [0]) * int(RATE * step))
        m = mix(bass, lead)
        if noise:
            m = mix(m, hits)
        s = self.mk(m)
        s.set_volume(0.35)
        return s

    def change_music(self, mood):
        if not (self.enabled and self.tracks):
            return
        if mood == 'calm' and self.mood == 'calm':
            return
        pool = [t for t in self.tracks.get(mood, []) if t is not self.music] or self.tracks.get(mood, [])
        if not pool:
            return
        self.mood = mood
        new = random.choice(pool)
        if self.music is not None:
            self.music.stop()
        self.music = new
        if self.music_on:
            new.play(loops=-1)

    def play(self, name, vol=1.0):
        if self.enabled and self.sfx_on and (name in self.sounds):
            s = self.sounds[name]
            s.set_volume(clamp(vol, 0, 1))
            s.play()

    def start_music(self):
        if self.enabled and self.music and self.music_on:
            self.music.play(loops=-1)

    def toggle_music(self):
        self.music_on = not self.music_on
        if self.enabled and self.music:
            if self.music_on:
                self.music.play(loops=-1)
            else:
                self.music.stop()
