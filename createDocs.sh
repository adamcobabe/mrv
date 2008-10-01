#!/bin/bash

# go to our directory 
cd `dirname $0`

# whiteshark docs
export PYTHONPATH=$PYTHONPATH:./ext/pyparsing:./ext/pydot:./ext/networkx:./py
epydoc --config=./doc/epydoc.cfg --inheritance grouped
