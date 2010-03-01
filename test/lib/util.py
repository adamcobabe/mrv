# -*- coding: utf-8 -*-
import os
import tempfile

def fixturePath( name ):
	"""@return:
		path to fixture file with ``name``, you can use a relative path as well, like
		subfolder/file.ext"""
	return os.path.abspath( os.path.join( os.path.dirname( __file__ ), "../fixtures/%s" % name ) )
	


