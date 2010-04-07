import os
from distutils.core import setup

try:
	from setuptools import find_packages
except ImportError:
	from ez_setup import use_setuptools
	use_setuptools()
	from setuptools import find_packages
# END get find_packages

def get_packages():
	root = 'mrv'
	base = os.path.dirname(os.path.abspath(__file__))
	return [root] + [ root + '.' + pkg for pkg in find_packages(base) ]
		

setup(name = "MRV",
      version = "1.0.0-preview",
      description = "MRV Development Environment",
      author = "Sebastian Thiel",
      author_email = "byronimo@gmail.com",
      url = "http://gitorious.org/mrv",
      packages = get_packages(),
      package_dir = {'mrv' : ''} ,
      package_data = { 'mrv' : ['bin/*'] },
      license = "BSD License",
      long_description = """"MRV is a multi-platform python development environment to ease rapid development 
of maintainable, reliable and high-performance code to be used in and around Autodesk Maya."
""",
      classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ]
      )
