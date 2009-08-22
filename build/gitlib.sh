#!/bin/bash
# A library with common functions for git interaction
# Allows functions to be called directly using:
# gitlib.sh call funcname [ args ]

# echo the name of the current branch
function git_currentBranch () {
	
	set -f			# disable globbing ! 
	local IFS=$'\n'		# set IFS to newline only !!!
	branch=
	
	for branchname in `git br`; do
		if [[ "$branchname" == "* "*	 ]]; then 
			branch=${branchname:2}
			if [[ $branch == "(no branch)" ]]; then
				branch=""
			fi
			
			echo $branch
		fi 
	done
	
	set +f
	
	[[ $branch == "" ]] && return 1 || return 0  
}



# allows to call functions directly 
if [[ $1 == "call" ]]; then
	funcname=${2:?"You need to set a function to call as second argument"}
	shift;shift 
	
	$funcname $@
fi