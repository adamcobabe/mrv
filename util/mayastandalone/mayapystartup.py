import maya.standalone
maya.standalone.initialize()

# init readline for nice tabcompletion !
import rlcompleter
import readline
readline.parse_and_bind("tab: complete")
