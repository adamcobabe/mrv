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


# list information about all submodules reachable from current dir
# arg 1: optional: if 1, default 0, the method will operate recursively, depth first
function git_submodule_list () {
	recurse=${1:-0}
	basepath=$2		# not necessarily set
	git ls-files --error-unmatch --stage -- "" | grep '^160000 ' | 
	while read mode sha1 stage path
	do 
		# return data
		echo $mode $sha1 $stage ${basepath}${path}
		
		if [[ $recurse == 1 && -d $path/.git ]]; then
			curdir=$PWD
			cd $path
			git_submodule_list $recurse $path/
			cd $curdir
		fi
	done	
}

# forcibly update all submodules to assure they contain all files they should
# contain 
# IMPORTANT: WILL DESTROY CHANGES IN THESE SUBMODULES
function git_submodule_forceUpdate () {
	curdir=$PWD
	git_submodule_list |
	while read mode sha1 stage path
	do
		if [[ -e "$path"/.git ]]
		then 
			cd $path && git checkout -f HEAD
		fi
	done
	cd $curdir
}


# disables or enable a submodule - this  allows git to temporarily forget about 
# the fact that the submodule is actually there, so the files of the submodule
# can be added to your own repository
# arg 1: if 1, submodules will be enabled, if 0 they are disabled
# NOTE: reads information as retrieved from git_submodule_list from stdin
# Hence you must call it like git_submodule_list | git_submodule_setEnabled arg
# IMPORTANT: git_submodule_list will not list submodules once you have disabled them
# hence you should cache the result
function git_submodule_setEnabled () { 
	enabled=${1:?"Need to set 1 or 0 to define whether the submodule should be enabled or disabled"}
	
	while read mode sha1 stage path
	do
		# adjust the index to mark deletion ( if hidden ) or revert the old file
		# also move the .git directory to hide it - otherwise git will not allow 
		# to add files that already appear to be mananged by a submodule ( fair enough :) )
		# if enabled
		source=$path/.git
		target=${source}hidden
		if [[ $enabled == 1 ]]
		then 
			tmp=$source
			source=$target
			target=$tmp
			# undo changes to index 
			git reset -q HEAD -- $path > /dev/null
		else
			# remove from index 
			git rm -q --cached $path
		fi
		
		if [[ -d $source ]]; then
			mv $source $target
		fi
	done
}

# allows to call functions directly 
if [[ $1 == "call" ]]; then
	funcname=${2:?"You need to set a function to call as second argument"}
	shift;shift 
	
	$funcname $@
fi