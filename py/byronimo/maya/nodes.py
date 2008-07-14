"""B{byronimo.nodes}

All classes required to wrap maya nodes in an object oriented manner into python objects
and allow easy handling of them.

These python classes wrap the API representations of their respective nodes - most general 
commands will be natively working on them.

These classes follow the node hierarchy as supplied by the maya api.

Optionally: Attribute access is as easy as using properties like 
  node.translateX
  
@note: it is important not to cache these as the underlying obejcts my change over time.
For long-term storage, use handles instead.

Default maya commands will require them to be used as string variables instead.
@todo: This should be done automatically

@todo: more documentation

@newfield revision: Revision
@newfield id: SVN Id
"""
                                            
__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-05-29 02:30:46 +0200 (Thu, 29 May 2008) $"
__revision__="$Revision: 16 $"
__id__="$Id: configuration.py 16 2008-05-29 00:30:46Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'

