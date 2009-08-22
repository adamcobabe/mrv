#!/bin/bash
# A library with common functions required to do a release
# Allows functions to be called directly using:
# releaselib.sh call funcname [ args ]


# return: python version string used in the given maya version 
function mapMayaToPythonVersion () {
	mayaversion=${1?:"First argument needs to be the maya version"}
	
	for pyversion in 8.52.4 20082.5 20092.5 ; do
		if [[ $pyversion == ${mayaversion}* ]]; then
			# output python version 
			echo ${pyversion/$mayaversion/}
			return 0
		fi
	done
	
	# could not find version
	echo "MayaVersion $1 unknown"
	return 2
}


# allows to call functions directly 
if [[ $1 == "call" ]]; then
	funcname=${2:?"You need to set a function to call as second argument"}
	shift;shift 
	
	$funcname $@
fi