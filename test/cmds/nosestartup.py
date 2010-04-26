# -*- coding: utf-8 -*-
# Runs nose - to be called by the mrv python wrapper which assures the environment 
# is setup properly

# assure we are initialized properly and the syspath is correct. Else the 
# nose import may fail
import mrv

import nose
nose.main()
