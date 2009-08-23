#!/bin/bash
# A library with common functions required to do a release
# Allows functions to be called directly using:
# releaselib.sh call funcname [ args ]


# includes 
###########
argscopy=$@
# empty args 
set - ""			
. ${0%/*}/gitlib.sh

# reset args 
set - $argscopy
unset argscopy


# Exit with exit status 1 and error message if there are arguments
function die () {
	if [[ $# > 0 ]]; then 
		echo >&2 $@
	fi
	exit 1
}

# return: python version string used in the given maya version
# arg 1: maya version
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

# compiles *.py to pyc in the given directory, recursively
# arg 1: python version to be used for compilation 
# arg 2: root directory for compilation
# NOTE: cleans all pyc beforehand
function compilePyToPyc () {
	pyversion=${1?:"Needs to be python version"}
	rootpath=${2?:"Needs to be the root path for the compilation"}
	
	find $rootpath -name "*.pyc" -exec rm {} +
	
	python$pyversion -c "import compileall; compileall.compile_dir(\"$rootpath\")" > /dev/null
}

# add files suitable for a mayarv release
# NOTE: Assumes we are in the root of the git repository
function _addFiles () {
	
	# delete folders we are not interested in 
	rm -Rf test build 2>/dev/null
	
	# by default, we add all py and pyc files - not test test files
	find . \( -name "*.pyc" -or -name "*.py" \) -not \( -wholename "./doc*" \) | xargs git add -f
	
	# add docs after moving them up to the doc level
	mv doc/build/html doc/.html
	rm -Rf doc/*
	mv doc/.html/* doc
	rm -Rf doc/.* 2>/dev/null		# delete all hidden files
	
	# add the doc directory 
	git add -f doc/
}

# compile the python files, remove certain directories, put clean data back in
# arg 1: source rev spec to checkout 
# arg 2: target branch to create or update
# arg 3: maya version to compile for

# arg 5: optionsl: command to call to add files to be included in release branch
#			defaults to _addFiles
function makeRelease () {
	srevspec=${1:?"Needs source branch or tag to checkout and release"}
	tbranch=${2:?"Needs target branch to write release data to"}
	mayaversion=${3:?"Needs target maya version to compile python for"}
	precompile=${4:?"Needs 1 or 0 to define whether py files should be precompiled"}
	add_files_script=${5:-"_addFiles"}
	
	pyversion=$(mapMayaToPythonVersion $mayaversion) || exit $?
	curbranch=$(git_currentBranch) || die "Could not determine current branch"
	back_to_sbranch="git checkout -f $curbranch"
	
	# CHECK STATE - needs to be clean
	# if we have a dirty state, abort
	# DONT, for now we are completely non-destructive as we are working additive !
	# - we only add files we want through some git repository knowledge
	# NOT as we also might want to move things to another place beforehand, hence it 
	# will be hard to recreate the state
	git status | grep "modified\|new file\|deleted" && die "abort due to dirty git state"
	
	
	# CHECK SOURCE REV SPEC - it must be valid 
	
	git-rev-parse --quiet --verify $srevspec || die "Source branch or tag at $srevspec does not exist"  

	# CHECKOUT SOURCE 
	##################
	git checkout $srevspec || die "Failed to checkout $srevspec"
	
	# compile pyc 
	deletefileglob="*.py"
	if [[ $precompile == 1 ]]; then 
		compilePyToPyc $pyversion .
	else
		deletefileglob="*.pyc"
	fi
	
	 
	# CHECK TARGET BRANCH - create it if it does not exist
	# otherwise we just switch 'silently' to it - we need a branch for this 
	# as we will advance it with a new commit. We do not want to change the state
	# of the current checkout by checking the existing tbranch out directly, hence 
	# we do it the 'sneaky' way
	tbranchpathshort="refs/heads/$tbranch"
	tbranchpathlong=".git/$tbranchpathshort"
	[[ ! -f $tbranchpathlong ]] &&  git checkout -b $tbranch ||
	echo "ref: $tbranchpathshort" > .git/HEAD
	
	
	# DISABLE SUBMODULES 
	submoduleinfo=$(git_submodule_list)
	
	echo $submoduleinfo | git_submodule_setEnabled 0
	
	# remove index to be able to completly rebuild it from scratch
	rm .git/index
	
	# re-add all files we need
	# delete files we will not need
	find . -name "$deletefileglob" | xargs rm -f 2>/dev/null
	$add_files_script || ( $back_to_sbranch ; die "Failed to add files using $add_files_script" )
	
	# commit changes
	git commit -m "Release $tbranch" > /dev/null
	rval=$?		# keep exit status - allow to return to original state even if we fail
	
	
	# REENABLE SUBMODULES AFTER COMMIT 
	echo $submoduleinfo | git_submodule_setEnabled 1
	
	# finally checkout the original branch, undoing all our possible changes
	# Even if it fails - if we are here, the actual release succeeded
	$back_to_sbranch 
	
	# undo changes in submodules 
	git_submodule_forceUpdate
	
	exit $rval
}


# allows to call functions directly 
if [[ $1 == "call" ]]; then
	funcname=${2:?"You need to set a function to call as second argument"}
	shift;shift 
	
	$funcname $@
fi