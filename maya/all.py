# -*- coding: utf-8 -*-
"""Module importing all maya related classes into one place
@note: It will not import anything if the sphinx build system is active as it 
will take too much memory ( ~2gig )"""
import sys
skip_import = False

for imported_path in sys.path_importer_cache.keys():
	if 'sphinx' in imported_path:
		skip_import = True
		break
	# END check for imported sphinx
# END for each imported path to check

if not skip_import:
	# maya 
	from env import *
	from ns import *
	from ref import *
	from scene import *
	from undo import *
	
	# nodes
	from nt import *
	
	if not cmds.about(batch=1):
		from ui import *
	# END selective ui import
# END selective import
