#!/bin/bash
# A library with common functions required to do a release
# Allows functions to be called directly using:
# releaselib.sh call funcname [ args ]



# allows to call functions directly 
if [[ $1 == "call" ]]; then
	funcname=${2:?"You need to set a function to call as second argument"}
	shift;shift 
	
	$funcname $@
fi