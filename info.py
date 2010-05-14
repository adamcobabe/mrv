# -*- coding: utf-8 -*-
"""
Provide project related global information
"""

#{ Configuration 

## Version Info 
# See http://docs.python.org/library/sys.html#sys.version_info for more information
#               major, minor, micro, releaselevel, serial
version = (1,     0,     0,     'Preview',        0)

project_name = "mrv"
root_package = "mrv"
author = "Sebastian Thiel"
author_email = 'byronimo@gmail.com'
url = "http://gitorious.org/mrv"
description ='Development Framework for Autodesk Maya'
license = "BSD License"

__scripts_bin = ['bin/mrv', 'bin/imrv']
__scripts_test_bin = ['test/bin/tmrv', 'test/bin/tmrvr']
__scripts_test_bin_s = [ p.replace('test/', '') for p in __scripts_test_bin ]
__ld = """MRV is a multi-platform python development environment to ease rapid development 
of maintainable, reliable and high-performance code to be used in and around Autodesk Maya."""

setup_kwargs = dict(scripts=__scripts_bin + __scripts_test_bin, 
                    long_description = __ld,
                    package_data = {   'mrv.test' : ['fixtures/ma/*', 'fixtures/maya_user_prefs/'] + __scripts_test_bin_s, 
                    					'mrv' : __scripts_bin + ['!*.gitignore'],
                    					'mrv.maya' : ['cache'],
                    					'mrv.doc' : ['source', 'makedoc', '!*source/generated/*']
                    				},   
                    classifiers = [
                        "Development Status :: 5 - Production/Stable",
                        "Intended Audience :: Developers",
                        "License :: OSI Approved :: BSD License",
                        "Operating System :: OS Independent",
                        "Programming Language :: Python",
                        "Programming Language :: Python :: 2.5",
                        "Programming Language :: Python :: 2.6",
                        "Topic :: Software Development :: Libraries :: Python Modules",
                        ], 
					options = dict(build_py={	'exclude_from_compile' : ('*/maya/undo.py', '*/maya/nt/persistence.py'), 
												'exclude_items' : ('mrv.conf', 'mrv.dg', 'mrv.batch', 'mrv.mdp', 
																	'.automation',
																	'mrv.test.test_conf', 'mrv.test.test_dg', 
																	'mrv.test.test_batch', 'mrv.test.test_mdp', 
																	'mrv.test.test_conf') }, 
									build_scripts={ 'exclude_scripts' : ['test/bin/tmrvr']}) 
                    )
#} END configuration

