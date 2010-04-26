#!/bin/bash
# tmrvr
# Apply full regression testing, testing all maya versions as well as all single 
# tests.
# 
# make it complicated, just to get it to work on osx !
base=${0%/*}/`readlink $0`
base=$(cd ${base%/*} && echo $PWD)
if [[ $base != /* ]]; then
	base=$PWD/$base
fi

# this is obviously as simple as it gets, I could imaging some commandline args
# to limit the tests to run as well as the maya versions. If that should happen, 
# the command should be rewritten in python to have a windows version as well.
for maya_version in 8.5 2008 2009 2010 2011; do
	# try to start the version - on failure skip it
	echo | $base/../../bin/mrv $maya_version
	if [[ $? != 0 ]]; then
		echo "Skipped $maya_version as it is not installed"
		continue
	fi
	
	for test in "" `find $base/.. -name "test_single_*.py"`; do
		echo "tmrv $maya_version ${test##$base/../}"
		
		# the 'echo null' means that python will never drop back into a shell when running
		# in test mode - this happens for example if we run maya post 2010 which 
		# changes the except hook. Could use a custom hook though, but this 
		# appears to be the simplest solution
		echo | $base/tmrv $maya_version $test -v
		if [[ $? != 0 ]]; then
			rval=$?
			echo "tmrv $maya_version ${test##$base/../} failed"
			exit $rval
		fi
	done
done

echo "-----------------------------------------------------------------"
echo "-----------------------------------------------------------------"
echo "You are ready for a release once you have tested the UI manually!"
echo "-----------------------------------------------------------------"
echo "-----------------------------------------------------------------"


