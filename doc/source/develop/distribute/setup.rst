
.. _setup-label:

################
The Setup Script
################
``setup.py`` is the default name for the `distutils`_ compatible script which drives the distribution and installation process. Python comes with a selection of setup-subcommands which may be configured independently.

MRV has re-implemented parts of the distutils to integrate unit testing, documentation generation and git into the distribution process.

In the following, a complete list of overridden or newly added subcommands will be presented including a detailed description of their flags. If a subcommand shows special behavior, it is documented in a dedicated **Specials** section. This kind of behavior can only be altered by providing an alternative implementation which involves deriving from the respective implementation and overriding class level members or methods.

The main class, ``Distribution``, manages its subcommands and can be seen as command root which doesn't do anything itself, but runs subcommands to do the actual work. Flags have been added to it to provide MRV specific information to the distribution system. 

A short example should illustrate how to call ``setup.py`` in general, and how flags map to the ``Distribution`` and to `Subcommands`_::
    
    $ python setup.py --use-git=1 --regression-tests=1 clean --all sdist --format=zip --dist-remotes=distro,hubdistro --root-remotes=gitorious,hub

The ``--use-git`` and ``--regression-tests`` flags are given to the ``Distribution`` instance to serve as general information for subcommands or to trigger general events, such as to run all regression tests.

``clean`` is the first subcommand to trigger the deletion of previously written distribution files. As subcommands are executed in order of appearance, the cleaning will happen before the ``sdist`` command is executed, which will create a source distribution and push the results to the given git remotes.

To show help, you may use the ``--help`` flag::
    
    $ # show help for setup in general
    $ python setup.py --help

    $ # show help for a specific subcommand
    $ python setup.py sdist --help

For more examples of how to perform common tasks, see the :doc:`workflow document <workflow>`.


When documenting command flags, they are given in the form:

 .. cmdoption:: --long-name (-s)

to indicate their long and short names. If the flag takes arguments, it is indicated by '=':

 .. cmdoption:: --flag-with-argument=VALUE (-f)
 
The type of the *VALUE* is usually documented specifically, and is accepted by the short command flag as well.

.. _setup-intimacies-label:

******************************************
Intimacies of sdist, build_py, and install
******************************************
Before diving into the actual command flags and special features, its important to understand the differences and implications between the major subcommands, namely ``sdist``, ``build`` and ``install``.

First of all, sdist and build are detached from each other when it comes to specifying the set of files to put into the distribution. ``sdist`` uses an easy to handle `MANIFEST.in`_ template, whereas ``build``, more specifically ``build_py`` which is called by ``build``, uses the ``packages`` and ``package_data`` keyword passed to the ``setup`` routine of your ``setup.py`` script.

The question may arise why you would bother dealing with the ``build`` setup if you only want to provide source installations anyway ? The answer lies hidden in the way the final command, ``install`` works.

But first, lets just assume we have prepared the ``MANIFEST.in`` and some basic configuration in the :doc:`info module <pinfo>`, and create an ``sdist`` distribution whose archive we upload to `pypi`_. The user wanting to install your project will simply run ...

::
    
    $ easy_install your_project

... which happens right before things go wrong. Easy_install, or any user who called ``python setup.py install`` in the extracted zip distribution of yours, will call the ``install`` subcommand which in turn calls ``build``.

Yes, it calls the ``build`` command in your source distribution which means that it must be setup, or at least tested, as well.

Depending on the complexity of your project, this is easier or harder, but as you will learn in the :doc:`workflow document <workflow>`, its all manageable, and ... what's done is done, the fame will be all yours !

.. _distribution-flags-label: 

******************
Distribution Flags
******************
When calling the ``setup.py`` script, what happens is that a ``Distribution`` instance will be created that in turn handles the keyword arguments given to the ``setup`` routine within the ``setup.py`` script. Afterwards it reads the `setup.cfg`_ configuration file which may override the previous keyword arguments. Finally, the instance parses the commandline arguments to learn about the subcommands to call, as well as additional overrides coming directly from the commandline.

As a summary, this is how to configure the distribution instance, items mentioned later override changes done by items mentioned earlier:

* Keyword Arguments given to ``setup`` routine
* key-value pairs read from the `setup.cfg`_ file
* Commandline arguments given to the *setup.py* script.

The ``Distribution`` instance keeps information about the overall operation to perform, as well as the commands to invoke to achieve this, hence it delegates most work and serves information and general functionality to its subcommands.

In MRV, the ``Distribution`` instance holds additional information about the project itself as accumulated in the :doc:`info module <pinfo>`, global flags to enable the usage of git or to run regression tests before any operation begins.

* .. cmdoption:: --maya-version=VERSION (-m)

 * Specifies the maya version for which to make the build, like ``2011`` or ``8.5``. This information is only used if build_py is to byte-compile all sources, the python version to use for the compilation is deduced by the given maya version.
 
* .. cmdoption:: --use-git=0|1 (-g)

 * If use-git is set to 1, default 0, subcommands will put their results into the underlying git repository and attempt to push them to the remotes configured either by the `Git`_ Command Bases or interactively.

* .. cmdoption:: --force-git-tag (-f)

 * If specified, the tag generated by the system may be forcibly created and possibly overwrite and existing tag with the same name pointing to a different commit. This flag is intended for beta or preview versions which change a lot, and usually don't require a version increment ( and the associated commit altering the ``info.py`` module ).
 * If not specified, tags are required to be unique, and the system will guide you through its interactive commandline interface to accomplish this, possibly incrementing the version information for you.
 * *Note:* Will only be taken into consideration if the ``string`` descriptor of your version, like ``preview``, is actually set and non-empty.

* .. cmdoption:: --regression-tests=0|1 (-t)

 * If set to 1, default 0, full regression tests will be run before a subcommand is called. If one test fails, the whole operation will abort.
 * It is recommended to specify this flag when creating release versions of your software at least. If affordable, it should be enabled for all types of distributions.
 * The program used to run the regression tests specified in the :doc:`info module <pinfo>`, but is most commonly :ref:`tmrvr <tmrvr-label>`.
 
* .. cmdoption:: --add-requires=ID[,ID...] (-r)

 * If specified, the given list of comma separated ids will be added to the existing list of ``requires`` ids as given to the setup() routine.
 * Use this in conjunction with the ``--package-search-dirs=`` flag, as you might want to specify your external dependencies using ``add-requires`` if you don't put them into your distribution directly.
 
* .. cmdoption:: --package-search-dirs=DIR[,DIR...] (-p)

 * If set to a comma separated list of directories relative to the project root, these directories will be specifically searched for additional python packges. The option defaults to search the **ext** directory otherwise.
 * To disable this option entirely, specify ``--package-search-dirs=``
 * *Note:* Is only effective when creating `build <build_py>`_ distributions.

========
Specials
========
* If packages are not explicitly specified using the ``packages`` keyword of the setup() routine, packages will be automatically searched under the root package of this project. The search is affected by the ``--package-search-dirs`` flag as well.
* The default ``package_data`` keyword argument for setup() was extended.

 * Patterns which point to a directory will automatically be expanded to include all subdirectories and files. Previously only file patterns could be specified. For example, a directory structure like ``dir/data``, ``dir/subdir/data2`` can be included as package data just by specifying ``dir`` as pattern.
 * Patterns may be prefixed with an exclamation mark (``!``) to exclude files which match the pattern after the '``!``'. This is useful to exclude portions of paths that you previously included using the directory expansion. To exclude the ``data2`` file from the previous example, you would specify the ``!dir/subdir/data2`` pattern, which may be a glob as well.
 * Please note that the ``packge_data`` is specified on distribution level, but is in fact used by `build_py`_, and has no effect on `sdist`_.

* Git was integrated into the distribution process, see `Git Handling`_.

.. _setup-git-label:

============
Git Handling
============
The MRV distribution integrates git and its repositories into the workflow. Instead of just creating archives to upload on `pypi`_ for example, it allows you to record the archive contents in dedicated repositories, or your project repository, and keep automatically generated tags and commit information, meshing together your distribution history. The git integration helps tremendously to avoid confusion and to track your distributions correctly. In order to associate the actual build with the source commit it was created from, it will be written into the ``info module`` of the distribution. The default line::
    
    src_commit_sha = '0'*40
    
becomes ...::
    
    src_commit_sha = '<40 character sha>'
    
... in the info module of your distribution. This makes sure that even for preview or beta releases which do not increment the version, you will not loose the information about the source commit.

Subcommands supporting the `Git`_ Command Base will store their files into the *closest* git repository they can find, in a branch composed of the project name and the type of the distribution, such as ``mrv-src``, ``mrv-py2.6`` or ``mrv-doc``. The *closest* git repository is the one found when walking the distribution output path upwards. This is at least the project root repository into which you commit your own code, but may be a repository that you have put into the path yourself. If you want a separate repository for all builds you create, you could setup a git repository  in the *build* directory for instance.
No matter into which repository the data is being added, it will be totally separated from your own source code history and commits, contained in their own branches, which looks more like having a sub-repository.

The `Git`_ Command Base allows to specify remotes to push the data to. It distinguishes between the distribution-remotes and root-remotes. Distribution remotes are destined to catch only the data meant for distribution, root-remotes will receive your newly created tag and new commits as stored in the root repository. The root-remote would most commonly be the remote you always push to when submitting your source. 

If ``--use-git`` is 1, the distribution will make sure that your current commit in the root repository is appropriately tagged who is named in accordance to the currently set version. If the version needs to be incremented as a tag with that name already exists, you will be guided through that process using interactive prompts, helping you to conveniently change the version string to generate a unique tag name.

The created git tag will be used to mark the exact commit you are going to distribute. All subcommands will use variations of this tag name as well. 

See the :doc:`workflow document <workflow>` for some actual examples

***********
Subcommands
***********
MRV's distribution system consists of setup subcommands which are partially overriding default ones, or which are new and specific to MRV. The latter ones are marked with *- new -*.

As some commands share the same set of flags, these flag-sets are combined in so called `Command Bases`_.

========
build_py
========
The ``build_py`` subcommand is in charge of creating builds of pure python modules and of copying module specific data into the build directory. On the way, it may also byte-compile the sources and remove the originals in order to create binary-only builds.

Both, the `Git`_ Command Base as well as `post-testing <Testing>`_ Command Base are supported. The latter one becomes especially interesting if you only build a subset of your project and need to assure that this subset is still working as expected.

When byte-compiling python modules using the ``--optimize=1|2`` flag as well as the ``--compile`` flag, the ``--maya-version`` needs to be set on the :ref:`Distribution <distribution-flags-label>` as well. 

* .. cmdoption:: --exclude-from-compile=FILE_GLOB[,FILE_GLOB...] (-e)

 * If given a comma separated list of file globs, all python modules matching these will not be compiled, but left as source file.
 * Use this flag to prevent python modules which are scripted maya plugins from being compiled, as maya may have trouble loading these otherwise.

* .. cmdoption:: --exclude-items=MODULE[,MODULE...] (-m)

 * If given a comma separated list of modules, like ``.module.``, ``modu`` or ``full.module.name``, all packages, modules and data files associated with them will be pruned from the build if they contain the given module as a *substring*. The more specific your module name, the less matches you will have and vice-versa.
 * Use this flag to reduce the amount of files that are put into the build directory, similar, but much less convenient, to the *MANIFEST.in* file the `sdist`_ command supports.  

Specials
--------
* When byte-compiling modules, the resulting ``*.pyo`` files will be renamed to ``*.pyc`` as many tools in the python world don't properly deal with *pyo* files.
* If optimization is set for byte-compilation with the ``optimize=1|2`` flag, test modules ( all modules with ``.test`` in their name ) will be pruned automatically. 
* When byte compiling, the source file will be removed in the build directory to allow binary-only distributions. Please note that in this case, one distribution must be created per python version, namely 2.4, 2.5 and 2.6 to support maya 8.5 to 2011 respectively.
* Supports the `Git`_ Command Base
* Supports the `Testing`_ Command Base

=============
build_scripts
=============
This command is a subcommand of ``build`` and called after `build_py`_ to prepare files designated as executable scripts. These will be made executable ( on posix systems ) and will be rewritten.

This implementation improves the scripts processing such that it will append the respective python version to the script file, i.e. ``mrv`` becomes ``mrv2.6`` when mangled by a python 2.6 interpreter. This becomes important when scripts are installed on the system as it is totally viable to use different mrv versions in different interpreters. To prevent confusion, the respective python versions are enforced in the file name.

* .. cmdoption:: --exclude-scripts=SCRIPT_PATH[,SCRIPT_PATH...] (-e)

 * Exclude the given comma separated list of script paths, i.e. ``bin/mrv``, from being handled by this command. This will prevent it from being installed as well. This does not cause the given scripts to be excluded in your build directory too.
 * Use this flag if you would like a given set of your executable scripts to be included in your build, but to define a subset which should not be installed when invoked together with the `install`_ command. For example, ``test/bin/tmrv`` is excluded that way as the normal user won't need it on his system, but it is part of the distribution.

=====
sdist
=====
This command will create source distributions from your root project tree and is entirely unrelated to the `build_py`_ subcommand.

Reading the **MANIFEST.in** template file, it generates a list of files being saved to the **MANIFEST** file, which will then be used to copy the named files into the source distribution folder.

This folder can be put into a compressed archive and/or be pushed into git repositories.

Besides providing git support for source distributions through the `Git`_ Command Base, it is also possible to run the unit test framework within the newly created source distribution to verify all files are in a consistent state. This is made available through the `Testing <Testing>`_ Command Base.

Everything else is handled by the `sdist` default implementation.

Specials
--------
* Supports the `Git`_ Command Base
* Supports the `Testing`_ Command Base

.. _setup-manifestin-label:

MANIFEST.in
-----------
The *MANIFEST.in* file acts as a template for the automated creation of the *MANIFEST* file which contains all files to be included in the source distribution.

All valid statements can be found in the `distutils online documentation <http://docs.python.org/distutils/commandref.html#sdist-cmd>`_.


=======
Install
=======
The ``install`` command was overridden to assure the byte-compilation is done by `build_py`_ and not by the install command itself.

Its good to know that ``install`` internally calls `build` which in turn triggers a set of other build related subcommands. Hence a build will be created when installing, everything in the build directory is copied into the respective installation location on your platform.

Everything else is handled by the default implementation.

=================
docdist *- new -*
=================
The ``docdist`` command allows to build documentation using :doc:`makedoc <docs>`, which needs to be pointed at by the :doc:`info module <pinfo>`.

You have the option to create and possibly reuse docs in your main repository, or create documentation as build directly in your build or source distribution output directory.

The build of the documentation is skipped if the last build version matches the currently set version. The version of the individual documentation parts is indicated by the *.version_info files in the *doc* directory.

The documentation output can be put into a zip-archive or into a git repository using the `Git`_ Command Base.

* .. cmdoption:: --zip-archive (-z)

 - If set, a zip archive containing all generated documentation, including the *index.html*, will be put into your distribution output folder, usually ``dist``.

* .. cmdoption:: --from-build-version (-b)

 - If set, the documentation will be built in the output directory as generated by **build_py** ( invoked by **build**) or **sdist**.
 - Should be used if your build or sdist output differs from your actual project contents, for example if you only distribute a subset of your modules. If this is not the case, its recommended not to set this flag as you can reuse documentation you might have already build for your currently set project version.
 - **Be aware** that if you are using the ``--force-git-tag`` distribution flag, without specifying the ``--from-build-version`` flag, it is likely that your documentation appears to be uptodate although the code changed in fact. In this case, you have to manually clean the documentation to force a rebuild.

 
*************
Command Bases
*************
Command Bases provide general functionality used by multiple Subcommands.

===
Git
===
The git command base allows to configure to which remotes the distribution data should be pushed to. The remotes you name must be setup already using ``git add remote ...``, using a url instead of the remote name is not allowed.

If the ``setup`` script's standard output is attached to a tty, the user will be asked to confirm the selection of branches and tags to be pushed to the remotes, which includes the option to alter the selection as desired.

* ..cmdoption:: --root-remotes=REMOTE[,REMOTE...] (-r)

 * The data of the branch currently checked out in your root repository, including the tag located at the commit to which it points, will be pushed to the given list of comma separated remote names.
 
* ..cmdoption:: --dist-remotes=REMOTE[,REMOTE...] (-d)

 * The data of the distribution branch including the tag located at the commit to which it points will be pushed to the given comma separated list of remote names. 

=======
Testing
=======

The distributions created by `build_py`_ or `sdist`_ may only contain a subset of the python modules available in the root project. In that case it is vital to run the unittests in the distribution you are actually going to publish in order to verify the quality of the distribution package.

The Testing Command Base provides a facility to do exactly that and makes sure your distribution fails if a test fails. 

Used in conjunction with the ``--regression-tests`` flag of the :ref:`Distribution <distribution-flags-label>`, quality can be assured ( within the limits of your unit-testing framework ).

* .. cmdoption:: --post-testing=VERSION[,VERSION...] (-t)

 * Run :ref:`tmrv <tmrv-label>` (or equivalent as configured in :doc:`info module <pinfo>`) using the given comma separated list of maya versions, like ``8.5,2009`` on all test cases found in the test directory of your current distribution.
 
* .. cmdoption:: --test-dir=DIR (-d)

 * Specified the directory which contains the test modules to run. It is specified as relative path, as the actual distribution root will be prepended to it.
 * defaults to ``test``


.. _pypi: http://pypi.python.org/pypi
.. _distutils: http://docs.python.org/distutils
.. _setup.cfg: http://docs.python.org/distutils/configfile.html
