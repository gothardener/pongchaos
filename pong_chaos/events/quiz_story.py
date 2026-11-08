from __future__ import annotations
import math
import random
import pygame
from ..core import *
from .base import *

from .ui import para

QUIZ = [('WHICH COMPANY RELEASED PONG IN 1972?', ['ATARI', 'NINTENDO', 'SEGA', 'SONY'], 0), ('HOW MANY LEGS DOES A SPIDER HAVE?', ['6', '8', '10', '12'], 1), ('WHAT IS THE CAPITAL OF AUSTRALIA?', ['SYDNEY', 'MELBOURNE', 'CANBERRA', 'PERTH'], 2), ('WHICH PLANET IS CLOSEST TO THE SUN?', ['VENUS', 'MERCURY', 'MARS', 'EARTH'], 1), ('HOW MANY SIDES DOES A HEXAGON HAVE?', ['5', '6', '7', '8'], 1), ('WHICH ANIMAL IS THE TALLEST?', ['ELEPHANT', 'GIRAFFE', 'CAMEL', 'MOOSE'], 1), ('WHAT IS 7 TIMES 8?', ['54', '56', '58', '64'], 1), ('WHICH OCEAN IS THE LARGEST?', ['ATLANTIC', 'INDIAN', 'ARCTIC', 'PACIFIC'], 3), ('WHO PAINTED THE MONA LISA?', ['PICASSO', 'DA VINCI', 'MONET', 'DALI'], 1), ('WHICH GAS DO PLANTS TAKE IN?', ['OXYGEN', 'NITROGEN', 'CARBON DIOXIDE', 'HELIUM'], 2), ('HOW MANY SQUARES ARE ON A CHESS BOARD?', ['32', '48', '64', '81'], 2), ('WHICH CHESS PIECE MOVES IN AN L-SHAPE?', ['BISHOP', 'KNIGHT', 'ROOK', 'PAWN'], 1), ('WHAT IS THE FASTEST LAND ANIMAL?', ['LION', 'HORSE', 'CHEETAH', 'GAZELLE'], 2), ('WHAT IS THE CHEMICAL SYMBOL FOR GOLD?', ['GO', 'AU', 'AG', 'GD'], 1), ('HOW MANY CONTINENTS ARE THERE?', ['5', '6', '7', '8'], 2), ('WHAT IS THE LARGEST MAMMAL?', ['BLUE WHALE', 'ELEPHANT', 'GIRAFFE', 'HIPPO'], 0), ('WHICH LANGUAGE IS MAINLY SPOKEN IN BRAZIL?', ['SPANISH', 'PORTUGUESE', 'FRENCH', 'ITALIAN'], 1), ('WHAT IS THE HARDEST NATURAL SUBSTANCE?', ['GOLD', 'IRON', 'DIAMOND', 'QUARTZ'], 2), ('HOW MANY HEARTS DOES AN OCTOPUS HAVE?', ['1', '2', '3', '8'], 2), ('WHICH GAME HAS A YELLOW CIRCLE EATING DOTS?', ['PAC-MAN', 'TETRIS', 'PONG', 'SNAKE'], 0), ('WHAT DOES CPU STAND FOR?', ['CENTRAL PROCESSING UNIT', 'COMPUTER PERSONAL UNIT', 'CENTRAL PADDLE USER', 'CAT PICTURE UPLOADER'], 0), ('WHAT SHAPE IS THE BALL IN THE ORIGINAL PONG?', ['CIRCLE', 'SQUARE', 'TRIANGLE', 'STAR'], 1), ('HOW MANY MINUTES ARE IN ONE DAY?', ['1,240', '1,440', '1,640', '2,400'], 1), ('WHICH METAL IS LIQUID AT ROOM TEMPERATURE?', ['IRON', 'LEAD', 'MERCURY', 'COPPER'], 2), ('WHAT IS THE SQUARE ROOT OF 81?', ['7', '8', '9', '11'], 2), ('WHICH OF THESE BIRDS CANNOT FLY?', ['PENGUIN', 'SPARROW', 'EAGLE', 'OWL'], 0), ('WHAT IS THE SMALLEST PRIME NUMBER?', ['0', '1', '2', '3'], 2), ('HOW MANY STRINGS DOES A STANDARD GUITAR HAVE?', ['4', '5', '6', '8'], 2), ('WHAT DO YOU CALL FROZEN WATER?', ['STEAM', 'ICE', 'FOG', 'DEW'], 1), ('WHAT SHOULD YOU DO WHEN THE BALL COMES AT YOU?', ['HIT IT', 'HUG IT', 'FILE A COMPLAINT', 'BLAME THE WIFI'], 0), ('HOW MANY PADDLES ARE NORMALLY ON THE COURT?', ['1', '2', '3', '47'], 1), ('IN WHAT YEAR WAS PONG RELEASED?', ['1962', '1972', '1982', '1992'], 1), ('WHICH OF THESE IS NOT A CHESS PIECE?', ['BISHOP', 'ROOK', 'DONUT', 'QUEEN'], 2), ('WHICH PLANET HAS FAMOUS RINGS?', ['SATURN', 'MARS', 'EARTH', 'MERCURY'], 0), ('HOW MANY COLORS ARE IN A RAINBOW?', ['5', '6', '7', '9'], 2), ('WHAT DO YOU CALL A BABY CAT?', ['PUP', 'KITTEN', 'CUB', 'CALF'], 1), ('WHICH IS THE LARGEST PLANET?', ['EARTH', 'JUPITER', 'SATURN', 'NEPTUNE'], 1), ('WHICH SPORT USES A SHUTTLECOCK?', ['TENNIS', 'SQUASH', 'BADMINTON', 'GOLF'], 2), ('HOW MANY DAYS ARE IN A LEAP YEAR?', ['364', '365', '366', '367'], 2), ('WHAT COLOR IS THE BALL IN THIS GAME?', ['WHITE', 'GREEN', 'PINK', 'DEPENDS ON THE CHAOS'], 3), ('WHAT DOES THE CPU WANT?', ['WORLD PEACE', 'TO WIN', 'A HUG', 'TACOS'], 1), ('HOW MANY LETTERS ARE IN THE WORD PONG?', ['3', '4', '5', '6'], 1), ('WHICH ONE IS A DOG BREED?', ['BEAGLE', 'SIAMESE', 'TABBY', 'PERSIAN'], 0), ('WHICH IS THE ODD ONE OUT?', ['PONG', 'TETRIS', 'PAC-MAN', 'A SANDWICH'], 3), ('WHAT HAPPENS WHEN YOU MISS THE BALL?', ['YOU WIN', 'THE CPU SCORES', 'NOTHING', 'IT BECOMES A BIRD'], 1)]
QCOLS = [(226, 27, 60), (19, 104, 206), (255, 166, 2), (38, 137, 12)]

def quiz_icon(s, k, cx, cy, u=14):
    w = WHITE
    if k == 0:
        pygame.draw.polygon(s, w, [(cx, cy - u), (cx + u, cy + u), (cx - u, cy + u)])
    elif k == 1:
        pygame.draw.polygon(s, w, [(cx, cy - u), (cx + u, cy), (cx, cy + u), (cx - u, cy)])
    elif k == 2:
        pygame.draw.circle(s, w, (cx, cy), u)
    else:
        pygame.draw.rect(s, w, (cx - u + 2, cy - u + 2, 2 * u - 4, 2 * u - 4))

@reg
class QuizShow(Mode):
    name = 'PONGOOT QUIZ!'
    sub = 'A WILD QUESTION APPEARS. BE FASTER THAN THE OTHER ONE.'
    dur = 38
    cap = 38
    limit = 34
    weight = 2.5
    hint1 = 'W / A / S / D  = RED / BLUE / YELLOW / GREEN   (ARROWS WORK TOO)'
    hint2 = 'P1: W A S D     P2: ARROW KEYS'
    TQ = 10.0

    def make_questions(self, n):
        g = self.g
        pool = random.sample(QUIZ, n)
        out = []
        for q, ans, ci in pool:
            a = list(ans)
            right = a[ci]
            random.shuffle(a)
            out.append((q, a, a.index(right)))
        if random.random() < 0.25:
            s0, s1 = g.scores
            truth = '%d - %d' % (s0, s1)
            wrong = set()
            while len(wrong) < 3:
                w_ = '%d - %d' % (max(0, s0 + random.choice((-2, -1, 1, 2))), max(0, s1 + random.choice((-2, -1, 0, 1, 2))))
                if w_ != truth:
                    wrong.add(w_)
            a = [truth] + sorted(wrong)
            random.shuffle(a)
            out[0] = ('WHAT IS THE CURRENT SCORE?', a, a.index(truth))
        return out

    def begin(self):
        g = self.g
        n = 1 if random.random() < 0.7 else 2
        self.qs = self.make_questions(n)
        self.qi = 0
        self.limit = 16 * n + 4
        self.pts = [0, 0]
        self.new_q()

    def new_q(self):
        self.ph = 'intro'
        self.pt = 0.0
        self.ans = [None, None]
        self.cpu_t = random.uniform(1.8, 6.5) * (1.25, 1.0, 0.75)[self.g.diff]
        self.cpu_ok = random.random() < (0.5, 0.68, 0.85)[self.g.diff]
        self.last_sec = -1
        self.gain = [0, 0]
        self.g.play('drum')

    def tick(self, dt):
        g = self.g
        self.pt += dt
        if self.ph == 'end':
            return
        q, a, ci = self.qs[self.qi]
        if self.ph == 'intro':
            if self.pt > 1.8:
                self.ph, self.pt = ('ask', 0.0)
                g.play('go', 0.6)
            return
        if self.ph == 'ask':
            sec = int(self.TQ - self.pt)
            if sec != self.last_sec and sec < 6:
                self.last_sec = sec
                g.play('tick' if sec > 2 else 'beep', 0.6)
            for side in (-1, 1):
                i = 0 if side < 0 else 1
                if self.ans[i] is not None:
                    continue
                if is_cpu(g, side):
                    if self.pt > self.cpu_t:
                        ch = ci if self.cpu_ok else random.choice([k for k in range(4) if k != ci])
                        self.ans[i] = (ch, self.pt)
                else:
                    L, R, U, D, F = human_keys(g, side)
                    ch = 0 if U else 1 if L else 2 if D else 3 if R else None
                    if ch is not None:
                        self.ans[i] = (ch, self.pt)
                        g.play('pop', 0.6)
            if self.ans[0] and self.ans[1] or self.pt >= self.TQ:
                self.reveal()
            return
        if self.ph == 'reveal' and self.pt > 3.4:
            self.qi += 1
            if self.qi >= len(self.qs):
                self.end_soon(0.2)
                self.ph = 'end'
            else:
                self.new_q()

    def reveal(self):
        g = self.g
        q, a, ci = self.qs[self.qi]
        self.ph, self.pt = ('reveal', 0.0)
        best = None
        for i in (0, 1):
            self.gain[i] = 0
            if self.ans[i] and self.ans[i][0] == ci:
                self.gain[i] = 500 + int(500 * (1 - self.ans[i][1] / self.TQ))
                self.pts[i] += self.gain[i]
                if best is None or self.ans[i][1] < self.ans[best][1]:
                    best = i
        if best is None:
            g.play('wrong')
            g.popup(W / 2, 250, 'NOBODY GOT IT!', (255, 100, 100), 30)
        else:
            g.play('right')
            side = -1 if best == 0 else 1
            pts = 2 if self.ans[best][1] < 3.0 else 1
            self.award(side, pts, '%s +%d%s' % (g.who(side), pts, ' SPEED BONUS!' if pts == 2 else ''))

    def draw_front(self, s):
        g = self.g
        q, a, ci = self.qs[min(self.qi, len(self.qs) - 1)]
        s.fill((70, 28, 120))
        for k in range(0, W, 80):
            pygame.draw.rect(s, (84, 36, 140), (k + int(g.t * 20) % 80, 0, 40, H))
        pygame.draw.rect(s, WHITE, (40, 76, 720, 130))
        pygame.draw.rect(s, (30, 30, 30), (40, 76, 720, 130), 4)
        nl = len(wrap_text(q.upper(), 688 // 24))
        para(g, s, q, 56, 76 + (130 - (nl * 36 - 8)) // 2, 30, (30, 30, 30), 688, True)
        if self.ph == 'intro':
            g.text_at(s, 'QUESTION %d' % (self.qi + 1), W // 2, 330, 46, WHITE)
            g.text_at(s, 'GET READY...' if int(g.t * 4) % 2 else '', W // 2, 400, 30, (255, 230, 0))
            return
        left = max(0.0, self.TQ - self.pt) if self.ph == 'ask' else 0
        pygame.draw.circle(s, WHITE, (70, 250), 34)
        g.text_at(s, str(int(left) + 1 if self.ph == 'ask' else 0), 70, 250, 30, (70, 28, 120))
        for i, cx in enumerate((300, 560)):
            col = (120, 220, 255) if i == 0 else (255, 140, 200)
            nm = g.who(-1 if i == 0 else 1)
            st = 'LOCKED IN!' if self.ans[i] else 'THINKING...'
            g.text_at(s, nm, cx, 232, 15, col)
            g.text_at(s, st if self.ph == 'ask' else '%d PTS' % self.pts[i], cx, 258, 15, WHITE)
        keys = ('W', 'A', 'S', 'D')
        for k in range(4):
            x = 30 + k % 2 * 380
            y = 290 + k // 2 * 110
            col = QCOLS[k]
            right = k == ci
            if self.ph == 'reveal' and (not right):
                col = tint(col, 0.35)
            pygame.draw.rect(s, col, (x, y, 360, 98))
            pygame.draw.rect(s, tint(col, 0.6), (x, y + 90, 360, 8))
            quiz_icon(s, k, x + 34, y + 49)
            sz = 30 if len(a[k]) <= 9 else 22
            px_ = text_px(sz)
            nl = len(wrap_text(a[k].upper(), 280 // (6 * px_)))
            para(g, s, a[k], x + 70, y + (98 - (nl * 9 * px_ - 2 * px_)) // 2 - 2, sz, WHITE, 280)
            g.text_at(s, keys[k], x + 346, y + 12, 15, tint(WHITE, 0.8), center=True)
            if self.ph == 'reveal' and right:
                pygame.draw.rect(s, WHITE, (x, y, 360, 98), 6)
                g.text_at(s, 'CORRECT!', x + 290, y + 78, 15, WHITE)
            for i in (0, 1):
                if self.ans[i] and self.ans[i][0] == k and (self.ph == 'reveal'):
                    c2 = (120, 220, 255) if i == 0 else (255, 140, 200)
                    pygame.draw.rect(s, c2, (x + 8 + i * 70, y + 4, 62, 20))
                    g.text_at(s, g.who(-1 if i == 0 else 1)[:6], x + 39 + i * 70, y + 14, 15, BLACK)
        if self.ph == 'reveal':
            for i, cx in enumerate((300, 560)):
                if self.gain[i]:
                    g.text_at(s, '+%d' % self.gain[i], cx, 205 - 0, 15, (120, 255, 150))
        self.hint(s, H - 48)
GRANNY_NAMES = ['GRANDMA GRIZELDA', 'NANA NIGHTSHADE', 'MEMAW MAYHEM', 'BABUSHKA DOOM', 'AUNT MABEL THE MEAN', 'LADY GERTRUDE VON DOOM', 'GRANNY GLORP', 'OLD MRS. HEXWORTH', 'GREAT-AUNT GRUDGE']
STORIES = [{'title': 'THE COOKIE DEAL', 'lines': [('N', 'THE COURT GOES DARK. SOMETHING SMELLS LIKE OATMEAL.'), ('G', 'AH, THERE YOU ARE, DEARIES. I HAVE WAITED 400 YEARS FOR A GAME OF PONG.'), ('C', 'WHO LET YOU IN? THIS IS A PRIVATE TOURNAMENT.'), ('G', 'I AM THE ANCIENT SPIRIT OF THE FIRST ARCADE CABINET. ALSO I BAKE.'), ('Y', '...ARE THE COOKIES CURSED?'), ('G', 'ONLY A LITTLE. THEY ARE OATMEAL RAISIN. WHICH IS WORSE.'), ('C', 'I WILL TAKE TEN. I HAVE NO TASTE BUDS. I AM A PADDLE.'), ('G', 'ONE COOKIE EACH. ONE IS BLESSED. THE OTHER IS EVIL.'), ('Y', 'HOW DO WE KNOW WHICH IS WHICH?'), ('G', "YOU DON'T, SWEETIE. THAT IS THE FUN PART. NOW CHOOSE.")], 'ask': 'WHICH COOKIE?', 'opts': ('LEFT COOKIE', 'RIGHT COOKIE'), 'good': ([('G', 'THE BLESSED ONE! YOU CAN SEE COLORS NOW. THE COLORS ARE LOUD.'), ('N', 'YOU GAIN 1 POINT. THE OTHER ONE GAINS A COOKIE-SHAPED HOLE IN THEIR SOUL.')], [('pts', 'you', 1)]), 'bad': ([('G', "THE EVIL ONE! HAHAHAHA! DELICIOUS, ISN'T IT?"), ('C', 'MY PADDLE IS SCREAMING. SOMEONE HELP.')], [('pts', 'cpu', 1), ('chaos', 1)])}, {'title': 'RENT IS DUE', 'lines': [('N', 'A DOOR APPEARS IN THE MIDDLE OF THE COURT. IT CREAKS OPEN.'), ('G', 'RENT IS DUE, DEARIES. THIS COURT IS MY LIVING ROOM.'), ('Y', 'WE HAVE PLAYED HERE FOR YEARS!'), ('G', 'AND YOU HAVE LEFT RING STAINS ON MY BALL.'), ('C', 'THE BALL HAS ALWAYS HAD RINGS. IT IS A PLANET.'), ('G', 'SILENCE, TOASTER. I WILL EVICT YOU BOTH, UNLESS SOMEONE PAYS.'), ('Y', 'WE ONLY HAVE POINTS.'), ('G', 'POINTS ARE ACCEPTED. ONE POINT, OR I SUMMON THE BAILIFF.'), ('C', 'WHO IS THE BAILIFF?'), ('G', 'A RAGING CHICKEN. HIS NAME IS DEREK.')], 'ask': 'WELL?', 'opts': ('PAY 1 POINT', 'DEFY GRANNY'), 'good': ([('G', 'HA! YOU HAVE SPUNK. KEEP YOUR POINT. TAKE ONE OF MINE.'), ('Y', 'THANKS... I THINK?')], [('pts', 'you', 1)]), 'bad': ([('G', 'DEREK! ATTACK!'), ('N', 'DEREK HAS ENTERED THE COURT. HE IS VERY ANGRY. HE IS A CHICKEN.')], [('pts', 'cpu', 1), ('event', 'ChickenCrossing')])}, {'title': 'THE PROPHECY', 'lines': [('N', 'A SPOTLIGHT. A DRAMATIC FOG. A VERY SMALL OLD LADY.'), ('G', 'AT LAST. THE CHOSEN PADDLES.'), ('Y', 'I THINK SHE IS A MENU.'), ('G', 'I AM THE ORACLE OF PIXELS. I HAVE SEEN YOUR FUTURE. IT IS SQUARE.'), ('C', 'IS IT A WIN? I ONLY ACCEPT WINS.'), ('G', 'ONE OF YOU WILL WIN THIS MATCH. THE OTHER WILL BE... ALSO HERE.'), ('Y', 'THAT IS NOT A PROPHECY. THAT IS A SCOREBOARD.'), ('G', "DON'T SASS THE ORACLE. THE REAL PROPHECY: YOU WILL BUY MY SWEATERS."), ('C', 'HOW MANY SWEATERS?'), ('G', 'FIFTY. THEY ARE ITCHY. THEY ARE CURSED. THEY ARE 12 DOLLARS.')], 'ask': 'SWEATERS?', 'opts': ('BUY THEM ALL', 'RUN AWAY'), 'good': ([('G', 'EXCELLENT. THE SWEATERS GIVE +10 WARMTH AND +1 POINT.'), ('Y', 'I FEEL SO COZY. AND SO SCRATCHY.')], [('pts', 'you', 1)]), 'bad': ([('G', 'NOBODY RUNS FROM GRANNY. ALSO THE SWEATERS ARE MADE OF BEES.'), ('N', 'THE BEES ARE NOT HAPPY ABOUT THIS.')], [('event', 'BeeSwarm'), ('pts', 'cpu', 1)])}, {'title': 'BINGO NIGHT', 'lines': [('N', 'THE SCOREBOARD FLICKERS. SOMEONE IS HUMMING. SOMEONE IS ALWAYS HUMMING.'), ('G', 'BINGO NIGHT, DEARIES! I HAVE BEEN CALLING NUMBERS SINCE 1962.'), ('C', 'THIS IS A PONG COURT. THERE IS NO BINGO HERE.'), ('G', 'B-7. NOBODY HAS EVER WON. THAT IS WHY I AM SO ANGRY.'), ('Y', 'CAN WE JUST PLAY PONG?'), ('G', 'PONG IS JUST BINGO WITH FEWER NUMBERS AND MORE REGRET.'), ('C', 'I RESPECT THIS LADY.'), ('G', 'I WILL CALL ONE NUMBER. IF IT IS YOURS, YOU WIN A POINT.'), ('Y', "AND IF IT ISN'T?"), ('G', 'THEN THE CAT GETS ONE. WHAT CAT? THE CAT. DO NOT ASK.')], 'ask': 'PICK A NUMBER', 'opts': ('NUMBER 7', 'NUMBER 42'), 'good': ([('G', 'BINGO!! SOMEBODY FINALLY WON! I HAVE WAITED SO LONG!'), ('Y', 'I AM... PROUD? CONFUSED? BOTH.')], [('pts', 'you', 1)]), 'bad': ([('G', 'WRONG! THE CAT TAKES A POINT AND ALSO YOUR DIGNITY.'), ('N', 'THE CAT HAS ARRIVED.')], [('event', 'CatAttack'), ('pts', 'cpu', 1)])}]
S_COL = {'Y': (120, 220, 255), 'C': (255, 140, 200), 'G': (210, 110, 255), 'N': (200, 200, 200)}

def draw_granny(s, cx, by, u, talk, t, evil=True):
    ox, oy = (int(cx - 8 * u), int(by - 20 * u))

    def R(x, y, w, h, c):
        pygame.draw.rect(s, c, (ox + x * u, oy + y * u, w * u, h * u))
    HAIR, SKIN, DK = ((170, 150, 210), (226, 218, 206), (40, 20, 60))
    R(6, 0, 4, 3, HAIR)
    R(5, 1, 6, 2, HAIR)
    R(4, 3, 8, 2, HAIR)
    R(3, 4, 2, 8, HAIR)
    R(11, 4, 2, 8, HAIR)
    R(5, 5, 6, 7, SKIN)
    R(5, 5, 1, 1, DK)
    R(6, 6, 1, 1, DK)
    R(10, 5, 1, 1, DK)
    R(9, 6, 1, 1, DK)
    glow = (255, 50, 50) if int(t * 7) % 3 else (255, 190, 60)
    R(4, 7, 3, 3, DK)
    R(9, 7, 3, 3, DK)
    R(7, 8, 2, 1, DK)
    R(5, 8, 1, 1, glow if evil else WHITE)
    R(10, 8, 1, 1, glow if evil else WHITE)
    R(5, 7, 1, 1, tint(glow, 0.55))
    R(10, 7, 1, 1, tint(glow, 0.55))
    R(7, 9, 2, 2, (170, 160, 150))
    R(5, 10, 1, 1, (170, 160, 150))
    R(10, 10, 1, 1, (170, 160, 150))
    if talk and int(t * 12) % 2:
        R(6, 11, 4, 2, DK)
        R(6, 11, 1, 1, WHITE)
        R(9, 11, 1, 1, WHITE)
    else:
        R(6, 11, 4, 1, DK)
        R(6, 12, 1, 1, WHITE)
        R(9, 12, 1, 1, WHITE)
    R(2, 13, 12, 7, (140, 60, 170))
    R(6, 13, 4, 1, WHITE)
    R(5, 14, 1, 2, WHITE)
    R(10, 14, 1, 2, WHITE)
    for k in range(3):
        R(8, 15 + k * 2, 1, 1, (255, 220, 60))
    R(0, 14, 2, 5, (120, 45, 150))
    R(14, 14, 2, 3, (120, 45, 150))
    R(15, 9, 1, 11, (130, 80, 40))
    R(14, 9, 2, 1, (130, 80, 40))
    R(14, 17, 2, 2, SKIN)

def draw_you(s, cx, by, u, talk, t, scared=False):
    ox, oy = (int(cx - 8 * u), int(by - 20 * u))

    def R(x, y, w, h, c):
        pygame.draw.rect(s, c, (ox + x * u, oy + y * u, w * u, h * u))
    R(3, 1, 10, 19, (40, 70, 110))
    R(4, 2, 8, 17, (120, 220, 255))
    R(5, 6, 2, 3, BLACK)
    R(9, 6, 2, 3, BLACK)
    R(5, 6, 1, 1, WHITE)
    R(9, 6, 1, 1, WHITE)
    if scared and int(t * 2) % 2:
        R(12, 4, 1, 2, (80, 140, 255))
    if talk and int(t * 12) % 2:
        R(6, 12, 4, 2, BLACK)
    elif scared:
        R(6, 13, 4, 1, BLACK)
        R(5, 14, 1, 1, BLACK)
        R(10, 14, 1, 1, BLACK)
    else:
        R(6, 12, 4, 1, BLACK)
        R(5, 11, 1, 1, BLACK)
        R(10, 11, 1, 1, BLACK)
    R(1, 10, 2, 2, (120, 220, 255))
    R(13, 10, 2, 2, (120, 220, 255))

def draw_cpu(s, cx, by, u, talk, t, scared=False):
    ox, oy = (int(cx - 8 * u), int(by - 20 * u))

    def R(x, y, w, h, c):
        pygame.draw.rect(s, c, (ox + x * u, oy + y * u, w * u, h * u))
    R(8, 0, 1, 3, (160, 160, 170))
    R(7, 0, 3, 1, (255, 60, 60) if int(t * 3) % 2 else (120, 30, 30))
    R(3, 3, 10, 17, (60, 70, 100))
    R(4, 4, 8, 15, (140, 150, 175))
    R(4, 6, 8, 3, (10, 30, 40))
    sc = 4 + int(t * 6) % 6
    R(sc, 7, 1, 1, (60, 255, 255))
    R(5, 7, 1, 1, (60, 255, 255) if not scared else (255, 255, 60))
    R(10, 7, 1, 1, (60, 255, 255) if not scared else (255, 255, 60))
    for k in range(4):
        R(6, 12 + k, 4, 1, (60, 70, 100) if k % 2 == 0 else (200, 200, 210))
    if talk and int(t * 12) % 2:
        R(6, 12, 4, 3, (255, 160, 60))
    R(1, 10, 2, 2, (140, 150, 175))
    R(13, 10, 2, 2, (140, 150, 175))

@reg
class StoryTime(Mode):
    name = 'STORY TIME'
    sub = 'AN EVIL OLD LADY WANTS A WORD'
    dur = 50
    cap = 50
    limit = 48
    weight = 2.5
    hint1 = 'SPACE / ENTER SPEEDS UP THE TALKING'
    hint2 = 'SPACE / ENTER SPEEDS UP THE TALKING'
    SPEED = 36.0

    def begin(self):
        g = self.g
        self.story = random.choice(STORIES)
        self.gname = random.choice(GRANNY_NAMES)
        self.seq = list(self.story['lines'])
        self.ci = 0
        self.chars = 0.0
        self.hold = 0.0
        self.ph = 'talk'
        self.choice_t = 0.0
        self.picked = None
        self.chooser = -1
        self.skip = False
        self.outcome = None
        self.applied = False
        self.blip_n = 0
        self.entry = 0.0
        self.ctr = 0.0
        g.play('thunder')
        g.flash(WHITE, 200)

    def who_name(self, sp):
        g = self.g
        return {'Y': 'YOU' if g.mode == 1 else 'P1', 'C': 'CPU' if g.mode == 1 else 'P2', 'G': self.gname, 'N': 'NARRATOR'}[sp]

    def cur(self):
        return self.seq[min(self.ci, len(self.seq) - 1)]

    def on_key(self, key):
        if key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_f):
            self.skip = True
        if self.ph == 'choice' and self.picked is None:
            if key in (pygame.K_a, pygame.K_LEFT, pygame.K_1):
                self.choose(0, 1 if key == pygame.K_LEFT and self.g.mode == 2 else -1)
            elif key in (pygame.K_d, pygame.K_RIGHT, pygame.K_2):
                self.choose(1, 1 if key == pygame.K_RIGHT and self.g.mode == 2 else -1)

    def choose(self, i, side):
        g = self.g
        self.picked = i
        self.chooser = side
        p_good = random.uniform(0.38, 0.62)
        good = random.random() < p_good
        lines, fx = self.story['good' if good else 'bad']
        self.outcome = (good, fx)
        self.seq.append(('Y', 'I CHOOSE: %s' % self.story['opts'][i]))
        self.seq.extend(lines)
        self.ph = 'talk'
        self.ci += 1
        self.chars = 0.0
        self.hold = 0.0
        g.play('pop')

    def apply_effects(self):
        if self.applied or not self.outcome:
            return
        self.applied = True
        g = self.g
        good, fx = self.outcome
        me, other = (self.chooser, -self.chooser)
        for e in fx:
            if e[0] == 'pts':
                who, n = (e[1], e[2])
                sides = [me] if who == 'you' else [other] if who == 'cpu' else [-1, 1]
                for sd in sides:
                    i = 0 if sd < 0 else 1
                    g.scores[i] = max(0, g.scores[i] + n)
                    g.popup(W / 4 if i == 0 else 3 * W / 4, 130, '%+d' % n, (120, 255, 150) if n > 0 else (255, 100, 100), 40)
            elif e[0] == 'event':
                g.queue.append(globals()[e[1]])
            elif e[0] == 'chaos':
                for _ in range(e[1]):
                    for _try in range(12):
                        c = g.pick_event()
                        if c is not None and (not c.is_mode) and (c is not ChaosOverload):
                            g.queue.append(c)
                            break
        g.play('powerup' if good else 'uhoh')
        g.flash(GOLD if good else (255, 60, 60), 90)

    def finish(self):
        self.apply_effects()

    def on_timeout(self):
        self.apply_effects()

    def tick(self, dt):
        g = self.g
        self.ctr += dt
        self.entry = min(1.0, self.entry + dt / 1.2)
        if self.ph == 'choice':
            self.choice_t += dt
            if self.picked is None and self.choice_t > 6.0:
                self.choose(random.randrange(2), -1)
                g.popup(W / 2, 380, 'GRANNY CHOSE FOR YOU', (210, 110, 255), 22)
            self.skip = False
            return
        if self.ph != 'talk':
            return
        sp, text = self.cur()
        if self.ctr < 1.4:
            self.skip = False
            return
        n = len(text)
        if self.chars < n:
            if self.skip:
                self.chars = float(n)
            else:
                prev = int(self.chars)
                self.chars += self.SPEED * dt
                for k in range(prev, min(n, int(self.chars))):
                    if text[k] != ' ' and k % 2 == 0:
                        g.play({'Y': 'blip_y', 'C': 'blip_c', 'G': 'blip_g', 'N': 'blip_n'}[sp], 0.5)
            self.hold = 0.0
        else:
            self.hold += dt
            if sp == 'G' and self.hold < dt * 1.5 and (random.random() < 0.18):
                g.play('cackle', 0.5)
            if self.skip or self.hold > 0.9:
                self.ci += 1
                self.chars = 0.0
                self.hold = 0.0
                if self.ci >= len(self.seq):
                    if self.outcome is None:
                        self.ci = len(self.seq) - 1
                        self.ph = 'choice'
                        self.choice_t = 0.0
                        g.play('stinger')
                        g.flash((255, 60, 60), 80)
                    else:
                        self.apply_effects()
                        self.end_soon(0.4)
                        self.ph = 'done'
        self.skip = False

    def draw_front(self, s):
        g = self.g
        t = g.t
        ph_done = self.ph == 'done'
        for i, c in enumerate(((20, 8, 40), (34, 12, 60), (54, 18, 80), (80, 24, 96))):
            pygame.draw.rect(s, c, (0, i * 93, W, 93))
        rnd = random.Random(7)
        for _ in range(40):
            x, y = (rnd.randint(0, W), rnd.randint(0, 300))
            if (int(t * 3) + x) % 5:
                pygame.draw.rect(s, WHITE, (x, y, 4, 4))
        pygame.draw.circle(s, (240, 235, 190), (90, 100), 40)
        pygame.draw.circle(s, (210, 205, 150), (74, 90), 8)
        pygame.draw.circle(s, (210, 205, 150), (104, 116), 6)
        pygame.draw.rect(s, (40, 16, 56), (0, 372, W, 40))
        for x in range(0, W, 80):
            pygame.draw.rect(s, (60, 24, 80), (x, 372, 40, 40))
        if int(t * 1.3) % 7 == 0 and self.ctr > 2:
            pygame.draw.polygon(s, (255, 255, 160), [(660, 0), (690, 0), (672, 60), (700, 60), (650, 140), (666, 80), (640, 80)])
        sp, text = self.cur()
        talk_g = self.ph == 'talk' and sp == 'G' and (self.chars < len(text)) and (self.ctr > 1.4)
        talk_y = self.ph == 'talk' and sp == 'Y' and (self.chars < len(text))
        talk_c = self.ph == 'talk' and sp == 'C' and (self.chars < len(text))
        scared = self.ph != 'choice' and sp == 'G' and (self.ctr > 1.4)
        gy = 372 - int((1 - self.entry) ** 2 * 260)
        bob = int(math.sin(t * 2.5) * 6)
        draw_you(s, 150, 372 - (6 if talk_y else 0), 8, talk_y, t, scared)
        draw_cpu(s, 650, 372 - (6 if talk_c else 0), 8, talk_c, t, scared and sp == 'G')
        draw_granny(s, 400, gy + bob, 10, talk_g, t)
        if self.ctr < 1.4:
            g.text_at(s, 'SOMETHING APPROACHES...', W // 2, 60, 22, (255, 100, 100))
        if self.ctr >= 1.4 or self.ph != 'talk':
            col = S_COL[sp]
            pygame.draw.rect(s, BLACK, (30, 410, 740, 150))
            pygame.draw.rect(s, col, (30, 410, 740, 150), 4)
            nm = self.who_name(sp)
            tag = g.render(nm, 22, BLACK)
            pygame.draw.rect(s, col, (46, 396, tag.get_width() + 24, 28))
            s.blit(tag, (_sn(58), _sn(403)))
            if self.ph == 'choice':
                self.draw_choice(s)
            elif not ph_done or True:
                lines = wrap_text(text.upper(), 29)
                shown = int(self.chars)
                y = 440
                for ln in lines:
                    part = ln[:max(0, shown)]
                    shown -= len(ln) + 1
                    if part:
                        s.blit(g.render(part, 30, WHITE), (_sn(52), _sn(y)))
                    y += 36
                if self.chars >= len(text) and int(t * 3) % 2:
                    g.text_at(s, 'SPACE >>', 730, 540, 15, (200, 200, 200))

    def draw_choice(self, s):
        g = self.g
        g.text_at(s, self.story['ask'], W // 2, 446, 30, (255, 230, 0))
        for i, x in enumerate((50, 410)):
            c = (226, 27, 60) if i == 0 else (19, 104, 206)
            pygame.draw.rect(s, c, (x, 474, 340, 52))
            pygame.draw.rect(s, WHITE, (x, 474, 340, 52), 2)
            g.text_at(s, '[%s] %s' % (('A / LEFT', 'D / RIGHT')[i], self.story['opts'][i]), x + 170, 500, 15, WHITE)
        k = clamp(1 - self.choice_t / 6.0, 0, 1)
        pygame.draw.rect(s, (255, 230, 0), (50, 536, int(700 * k), 8))
