#!/bin/bash

# Call with : $mayaversion $pyversion ( 8.5[-x64] 2.4 | 2008[-x64] 2.5 )
mayapath=/usr/autodesk/maya$1
MAYA_LOCATION=$mayapath
# set ldd path to maya directory
export LD_LIBRARY_PATH=$mayapath/lib:$LD_LIBRARY_PATH

# adjust PYTHONPATH to look for maya includes
export PYTHONPATH=$mayapath/lib/python$2/site-packages

# the python home appears to be repsonsible for the weird interactive input setting !
# if python itself starts from the maya home, the pyshell does not support convenience functions
#export PYTHONHOME=$mayapath

scriptdir=`dirname $0`

# ALLOW CUSTOM CALLBACK
script=$scriptdir/mayapy_custom.sh
[ -e $script ] && . $script

# start python and initialize it using the mayastartup script
python$2 -i $scriptdir/mayapystartup.py

