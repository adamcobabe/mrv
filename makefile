
# This is a very simple make-file for now to aid keeping the commandline options
# under control. 
# There is no intention to have something like it on windows, but the commandlines
# shown here could work mostly unaltered on the windows platform as well.

.PHONY=preview-docs preview

all:
	echo "Nothing to do - specify an actual target"

preview-docs:
	/usr/bin/python setup.py --force-git-tag  --use-git=1 --regression-tests=0 docdist --zip-archive --dist-remotes=docdistro --root-remotes=gitorious

# Moving-Tag Preview Commit 
preview: preview-docs
	/usr/bin/python setup.py --force-git-tag  --use-git=1 --regression-tests=0 clean --all sdist --format=zip --dist-remotes=distro --root-remotes=gitorious
