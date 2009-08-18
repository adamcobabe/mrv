import sys
from pkg_resources import load_entry_point

sys.exit(
   load_entry_point('Sphinx==0.6.2', 'console_scripts', 'sphinx-autogen')()
)
