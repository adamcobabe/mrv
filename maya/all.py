# -*- coding: utf-8 -*-
"""Module importing all maya related classes into one place"""
# maya 
from env import *
from ns import *
from ref import *
from scene import *
from undo import *

# nodes
from nodes import *

if not cmds.about(batch=1):
	from ui import *
# END selective ui import
