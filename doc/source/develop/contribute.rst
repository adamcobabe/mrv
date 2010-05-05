
.. _contribute-label:

************
Contributing
************
MRV is an open source project based on the work of just one person ( for now ), which doesn't only mean that this person must be slightly crazy, but also that MRV was written from just one perspective. There is a `gource video <http://vimeo.com/10611158>`_ which illustrates that ... pretty lonely situation.

Many convenience methods, for instance the ones in ``mrv.maya.nt.geometry`` have been written because there was a specific need for it. Many areas that would need additional implementations have not seen any attention yet.

The solution to this problem is to make MRV accessible by providing a solid documentation, and to actually make contribution easy. With traditional SCM's, this is not the case as you may not do anything with the repository unless special permissions are granted.

With `git <http://git-scm.com>`_ though, or any distributed version control system for that matter, this is a problem of the past as your clone of the repository contains all information you need to , theoretically, found your very own version of the software. Make your own branches, apply your own patches, commit whenever you want, and rebase your changes onto the latest version of the mainline repository that you originally cloned from.

With contributions, the scene you have seen in the first video, `might soon look more like this <http://vimeo.com/10617731>`_.
 
Using Git
=========
Once you have cloned your initial copy from the mainline repository ( see :ref:`repo-clone-label` ), you stay up-to-date by fetching ( ``git fetch`` ) the latest changes from mainline and by merging them into your master branch ( ``git merge`` ).

In order to contribute though, the by far easiest workflow is to create your own MRV fork on either `www.gitorious.com <http://gitorious.org/mrv>`_ or on `www.github.com <http://www.github.com/Byron/mrv>`_. 

When creating own features or patches, you just put them into a separate branch ( using ``git co -b myfeature`` ), commit your changes using ``git commit ...`` and finally push everything into your public repository ( ``git push ...`` ) and create a merge request. Once it has been merged into the mainline repository, your change automatically makes it into the next MRV release and the mainline repository. 

The workflow presented here is only a rough introduction to the multitude of possible git workflows, and more concrete examples will be added as the need arises.


