from .base import EVENTS, Event, Mode, reg, human_keys, is_cpu
from .standard import *
from .game_modes import *
from .ui import *
from .world import *
from .minigames import *
from .chess import *
from .quiz_story import *
from .doom import *
from .pongdows import *
from .cat_meme import *
from .overload import *
from .mood import MOOD

from . import world as _world
from . import quiz_story as _quiz_story
from .overload import ChaosOverload
_world.ChaosOverload = ChaosOverload
_quiz_story.ChaosOverload = ChaosOverload
