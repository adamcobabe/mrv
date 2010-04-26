#!/bin/bash
# imrv [ mayaversion ] [ args ]
# Maya version can be 8.5, 2008, 2009 and so forth
# 
# start a python shell suitable to run maya and launch ipython in it
# This is useful mainly for debugging
base=$(cd ${0%/*} && echo $PWD)
firstArg=

# if the first argument is the maya version, we have to parse it to be able to 
# put it as first argument, inserting our args for the interpreter
if [[ $1 == 8.5 || $1 == 20?? ]]; then
	firstArg=$1
	shift
fi

# determine which file to start based on existing ones, prefer .py
startupfile=`[[ -f $base/ipythonstartup.py ]] && echo $base/ipythonstartup.py || echo $base/ipythonstartup.pyc`
$base/mrv $firstArg -i $startupfile $@
