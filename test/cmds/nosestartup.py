# -*- coding: utf-8 -*-
# Runs nose - to be called by the mrv python wrapper which assures the environment 
# is setup properly

import os
import sys

# assure we are initialized properly and the syspath is correct. Else the 
# nose import may fail
import mrv
import mrv.test.cmds as mrvtestcmds

# It is possible to pass additional args which we append to the system args.
# This is required in case we start nose in maya UI mode and want to pass
# nose specific arguments
if mrvtestcmds.env_nose_args in os.environ:
	sys.argv = ['nosetests'] + os.environ[mrvtestcmds.env_nose_args].split(mrvtestcmds.nose_args_splitter)
# END handle extra args


import nose
nose.main()
