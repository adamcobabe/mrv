#!/bin/bash

# Call with : $mayaversion $pyversion ( 8.5 2.4 | 2008 2.5 )
mayapath=/usr/autodesk/maya$1
MAYA_LOCATION=$mayapath
# set ldd path to maya directory
export LD_LIBRARY_PATH=$mayapath/lib:$LD_LIBRARY_PATH

# adjust PYTHONPATH to look for maya includes
export PYTHONPATH=/usr/autodesk/maya$1/lib/python$2/site-packages
# the python home appears to be repsonsible for the weird interactive input setting !
# if python itself starts from the maya home, the pyshell does not support convenience functions
#export PYTHONHOME=$mayapath
scriptdir=`dirname $0`
# start python and initialize it using the mayastartup script
python$2 -i $scriptdir/mayapystartup.py

